"""Host suite for the canonical native mncs-learn path.

Every learning number is produced by a native `mncs call`; the Python
oracle (`oracle.mncs_learn`) is used only for parity — same inputs, same
decisions — plus an independent plain-Python centroid that shares no
code with either implementation. Known answers are hand-computed.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
# The oracle package must win over tools/mncs_learn.py (the CLI shim).
SRC = REPO / "oracle"
if str(SRC) in sys.path:
    sys.path.remove(str(SRC))
sys.path.insert(0, str(SRC))

from learn import codes, engine, model, native, store  # noqa: E402

WORKSPACE = REPO.parent


def _libraries() -> list[str]:
    libs = [str(WORKSPACE / "mncs-test" / "native"),
            str(REPO / "native")]
    root = os.environ.get("MNCS_LANGUAGE_ROOT")
    if root:
        libs.append(str(Path(root) / "library"))
    for repo, sub in (("mncs-data", "src"), ("mncs-math", "src")):
        candidate = WORKSPACE / repo / sub
        if candidate.is_dir():
            libs.append(str(candidate))
    return libs


MNCS = native.find_mncs()
LIBRARIES = _libraries()


def need_mncs(test):
    return unittest.skipIf(MNCS is None, "mncs binary unavailable")(test)


class Case(unittest.TestCase):
    def setUp(self) -> None:
        import shutil
        self.tmp = Path(tempfile.mkdtemp(prefix="learn-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def dataset(self, rows, labels, names=None, label_names=None):
        return model.validate_dataset({
            "schema_version": codes.DATASET_SCHEMA,
            "feature_names": names or ["x", "y"],
            "rows": rows, "labels": labels,
            "label_names": label_names or {}})

    def two_class(self):
        return self.dataset([[0, 0], [2, 0], [10, 0], [12, 0]],
                            [0, 0, 1, 1])


class CodesMirrorTests(Case):
    @need_mncs
    def test_native_codes_match_host(self) -> None:
        pairs = [("decision_commit", codes.DECISION_COMMIT),
                 ("decision_reject", codes.DECISION_REJECT),
                 ("decision_defer", codes.DECISION_DEFER),
                 ("op_centroid_update", codes.OP_CENTROID_UPDATE),
                 ("op_no_learning", codes.OP_NO_LEARNING),
                 ("reason_untrained", codes.REASON_UNTRAINED),
                 ("reason_overflow", codes.REASON_OVERFLOW),
                 ("reason_stale_revision", codes.REASON_STALE_REVISION),
                 ("reason_rights_denied", codes.REASON_RIGHTS_DENIED)]
        for function, expected in pairs:
            document = native.call_function(
                mncs=MNCS,
                program=str(REPO / "native" / "mncs" / "learn" /
                            "codes.mncs"),
                module="mncs.learn.codes.v1", function=function,
                args=[], libraries=LIBRARIES)
            value = native.plain(document["call"]["returned"][0])
            self.assertEqual(value, expected, function)


class OracleParityTests(Case):
    def test_fox_lifecycle_matches_oracle(self) -> None:
        from mncs_learn import (AdaptationProposal, Decision, Evaluation,
                                Fitness, LearnableCapability, LearningEvent,
                                LearningScheduler, Observation, Plasticity,
                                Rights)
        state: list = []
        commits = [0]

        class Target:
            capability = LearnableCapability(
                model_id="model:fox", model_class="semantic-prototype",
                accepts=frozenset({"semantic"}),
                operators=frozenset({"prototype_update"}),
                mutation_scopes=frozenset({"internal"}),
                timescales=frozenset({"fast"}),
                evaluation_dimensions=("semantic_consistency",),
                plasticity=Plasticity(current=0.7, minimum=0.05,
                                      maximum=0.95))

            @property
            def revision(self):
                return f"rev:{commits[0]}"

            def evaluate(self, proposal):
                return Evaluation(
                    proposal.id, Decision.COMMIT,
                    Fitness({"semantic_consistency": 0.5},
                            {"rights": True}, 0.9),
                    Fitness({"semantic_consistency": 0.6},
                            {"rights": True}, 0.9),
                    ("fitness improves",))

            def commit(self, proposal):
                commits[0] += 1
                state.append(proposal.patch["append"])
                return self.revision

        class Operator:
            name = "prototype_update"

            def supports(self, event, target):
                return True

            def propose(self, event, target):
                return [AdaptationProposal(
                    id="proposal:1", event_id=event.id,
                    target_id=target.capability.model_id,
                    target_revision=target.revision,
                    operator=self.name,
                    mutation_scopes=frozenset({"internal"}),
                    timescale="fast", reason="evidence",
                    expected_effect={"semantic_consistency_delta": 0.1},
                    patch={"append": event.observation.payload},
                    provenance={"source": event.id}, reversible=True)]

        event = LearningEvent(
            id="event:1",
            observation=Observation(
                id="obs:1", kind="semantic",
                data_type="language/semantic-graph",
                payload={"entity": "fox"}, provenance={"source": "test"},
                confidence=0.97, rights=Rights()),
            desired_effects=("generalize",), targets=("model:fox",))
        results = LearningScheduler([Operator()]).process(event, [Target()])
        self.assertEqual(results[0].decision, Decision.COMMIT)
        self.assertEqual(results[0].resulting_revision, "rev:1")
        self.assertEqual(state, [{"entity": "fox"}])
        self.assertEqual(commits[0], 1)

    def test_oracle_gates_match_native_reasons(self) -> None:
        from mncs_learn import (LearnableCapability, LearningEvent,
                                LearningScheduler, Observation, Plasticity,
                                Rights)
        target = type("T", (), {})()
        target.capability = LearnableCapability(
            model_id="m", model_class="c", accepts=frozenset({"semantic"}),
            operators=frozenset({"prototype_update"}),
            mutation_scopes=frozenset({"internal"}),
            timescales=frozenset({"fast"}),
            evaluation_dimensions=("d",),
            plasticity=Plasticity(current=0.0, minimum=0.0, maximum=1.0))

        def event(learn: bool):
            return LearningEvent(
                id="e", observation=Observation(
                    id="o", kind="semantic", data_type="t", payload={},
                    provenance={}, confidence=1.0,
                    rights=Rights(learn=learn)),
                desired_effects=("g",))

        allowed, _ = LearningScheduler.eligible(event(True), target)
        self.assertFalse(allowed)  # plasticity zero blocks
        denied, reason = LearningScheduler.eligible(event(False), target)
        self.assertFalse(denied)
        self.assertEqual(reason, "learning right denied")

    @need_mncs
    def test_native_decide_matches_oracle_fitness(self) -> None:
        up = engine.decide(mncs=MNCS, before_pm=500, after_pm=600)
        self.assertEqual(
            (up["decision"], up["reason"]),
            (codes.DECISION_COMMIT, codes.REASON_IMPROVES))
        flat = engine.decide(mncs=MNCS, before_pm=600, after_pm=600)
        self.assertEqual(
            (flat["decision"], flat["reason"]),
            (codes.DECISION_DEFER, codes.REASON_NO_CHANGE))
        down = engine.decide(mncs=MNCS, before_pm=600, after_pm=500)
        self.assertEqual(
            (down["decision"], down["reason"]),
            (codes.DECISION_REJECT, codes.REASON_REGRESSES))
        blocked = engine.decide(mncs=MNCS, before_pm=100, after_pm=900,
                                constraints_ok=False)
        self.assertEqual(
            (blocked["decision"], blocked["reason"]),
            (codes.DECISION_REJECT, codes.REASON_CONSTRAINT_VIOLATED))

    @need_mncs
    def test_native_eligibility_matches_oracle(self) -> None:
        base = {"model": 1, "class_code": 7,
                "accepts_kind": codes.OBS_FEATURE_LABEL,
                "operator": codes.OP_CENTROID_UPDATE, "scope": 0,
                "timescale": 0, "plasticity": (700, 50, 950)}
        good = engine.check_eligible(mncs=MNCS, capability=base,
                                     obs_kind=codes.OBS_FEATURE_LABEL,
                                     rights_learn=True)
        self.assertTrue(good["ok"])
        denied = engine.check_eligible(mncs=MNCS, capability=base,
                                       obs_kind=codes.OBS_FEATURE_LABEL,
                                       rights_learn=False)
        self.assertEqual(denied["reason"], codes.REASON_RIGHTS_DENIED)
        kind = engine.check_eligible(mncs=MNCS, capability=base,
                                     obs_kind=codes.OBS_FEATURE_ONLY,
                                     rights_learn=True)
        self.assertEqual(kind["reason"], codes.REASON_INELIGIBLE_KIND)
        zero = dict(base, plasticity=(0, 0, 1000))
        plast = engine.check_eligible(mncs=MNCS, capability=zero,
                                      obs_kind=codes.OBS_FEATURE_LABEL,
                                      rights_learn=True)
        self.assertEqual(plast["reason"], codes.REASON_PLASTICITY_ZERO)


def trunc_div(a: int, b: int) -> int:
    quotient = abs(a) // abs(b)
    return quotient if (a < 0) == (b < 0) else -quotient


def independent_centroids(rows, labels):
    sums: dict[int, list[int]] = {}
    counts: dict[int, int] = {}
    for row, label in zip(rows, labels):
        sums.setdefault(label, [0] * len(row))
        counts[label] = counts.get(label, 0) + 1
        for dim, value in enumerate(row):
            sums[label][dim] += value
    return {label: [trunc_div(total, counts[label]) for total in totals]
            for label, totals in sums.items()}


def independent_predict(centroids, point):
    best, best_dist = None, None
    for label in sorted(centroids):
        dist = sum((value - center) ** 2
                   for value, center in zip(point, centroids[label]))
        if best_dist is None or dist < best_dist:
            best, best_dist = label, dist
    return best, best_dist


class CentroidKnownAnswerTests(Case):
    @need_mncs
    def test_trains_exact_hand_computed_state(self) -> None:
        dataset = self.two_class()
        state, report = engine.train(mncs=MNCS, dataset=dataset)
        self.assertTrue(report["ok"])
        self.assertEqual(report["rows_used"], 4)
        self.assertEqual(state["nclasses"], 2)
        self.assertEqual(state["counts"][:2], [2, 2])
        self.assertEqual(state["sums"][0][:2], [2, 0])
        self.assertEqual(state["sums"][1][:2], [22, 0])
        self.assertEqual(state["revision"], 4)
        # Independent implementation agrees, sharing no code.
        centroids = independent_centroids(dataset["rows"],
                                          dataset["labels"])
        self.assertEqual(centroids, {0: [1, 0], 1: [11, 0]})

    @need_mncs
    def test_predicts_known_points(self) -> None:
        dataset = self.two_class()
        state, _ = engine.train(mncs=MNCS, dataset=dataset)
        near = engine.predict(mncs=MNCS, state=state, features=[1, 0])
        self.assertEqual((near["label"], near["dist2"]), (0, 0))
        far = engine.predict(mncs=MNCS, state=state, features=[9, 0])
        self.assertEqual((far["label"], far["dist2"]), (1, 4))
        centroids = independent_centroids(dataset["rows"],
                                          dataset["labels"])
        self.assertEqual(independent_predict(centroids, [9, 0]), (1, 4))

    @need_mncs
    def test_incremental_update_equals_batch(self) -> None:
        dataset = self.two_class()
        batch, _ = engine.train(mncs=MNCS, dataset=dataset)
        state = engine.fresh_state(mncs=MNCS, ndim=2)
        for row, label in zip(dataset["rows"], dataset["labels"]):
            state = engine.update(mncs=MNCS, state=state, features=row,
                                  label=label)
        self.assertEqual(state["counts"], batch["counts"])
        self.assertEqual(state["sums"], batch["sums"])
        self.assertEqual(state["revision"], batch["revision"])

    @need_mncs
    def test_repeat_training_is_deterministic(self) -> None:
        dataset = self.two_class()
        first, _ = engine.train(mncs=MNCS, dataset=dataset)
        second, _ = engine.train(mncs=MNCS, dataset=dataset)
        self.assertEqual(first, second)


class TableSemanticsTests(Case):
    @need_mncs
    def test_missing_rows_skip_without_coercion(self) -> None:
        dataset = self.dataset([[0, 0], [None, 0], [10, 0], [12, 0]],
                               [0, 0, 1, 1])
        state, report = engine.train(mncs=MNCS, dataset=dataset)
        self.assertTrue(report["ok"])
        self.assertEqual(report["rows_seen"], 4)
        self.assertEqual(report["rows_used"], 3)
        self.assertEqual(report["rows_skipped"], 1)
        # Class 0 saw only (0,0): centroid (0,0), not a coerced zero row.
        self.assertEqual(state["sums"][0][:2], [0, 0])
        self.assertEqual(state["counts"][0], 1)

    @need_mncs
    def test_wrong_column_kind_is_schema_mismatch(self) -> None:
        state = engine.fresh_state(mncs=MNCS, ndim=2)
        table = model.table_arg(self.two_class())
        fields = dict(table["record"]["fields"])
        schema = dict(fields["schema"]["record"]["fields"])
        cols = list(schema["cols"]["sequence"]["values"])
        col0 = dict(cols[0]["record"]["fields"])
        col0["kind"] = {"finite": {"type": "CellKind",
                                   "variant": "Text"}}
        cols[0] = {"record": {"type": "ColumnSpec", "fields": col0}}
        schema["cols"] = {"sequence": {"values": cols}}
        fields["schema"] = {"record": {"type": "Schema4",
                                       "fields": schema}}
        bad = {"record": {"type": "Table", "fields": fields}}
        report = native.call_record(
            mncs=MNCS, program=engine.CENTROID_PROGRAM,
            module=engine.CENTROID_MODULE, function="train_table",
            args=[bad, model.state_arg(state)], libraries=LIBRARIES)
        self.assertFalse(report["ok"])
        self.assertEqual(report["reason"], codes.REASON_SCHEMA_MISMATCH)

    @need_mncs
    def test_all_skipped_is_empty_dataset(self) -> None:
        dataset = self.dataset([[None, 0], [1, None]], [0, 1])
        state = engine.fresh_state(mncs=MNCS, ndim=2)
        report = native.call_record(
            mncs=MNCS, program=engine.CENTROID_PROGRAM,
            module=engine.CENTROID_MODULE, function="train_table",
            args=[model.table_arg(dataset), model.state_arg(state)],
            libraries=LIBRARIES)
        self.assertFalse(report["ok"])
        self.assertEqual(report["reason"], codes.REASON_EMPTY_DATASET)

    @need_mncs
    def test_untrained_evaluation_is_explicit(self) -> None:
        dataset = self.two_class()
        state = engine.fresh_state(mncs=MNCS, ndim=2)
        report = native.call_record(
            mncs=MNCS, program=engine.CENTROID_PROGRAM,
            module=engine.CENTROID_MODULE, function="evaluate_table",
            args=[model.table_arg(dataset), model.state_arg(state)],
            libraries=LIBRARIES)
        self.assertFalse(report["ok"])
        self.assertEqual(report["reason"], codes.REASON_UNTRAINED)

    @need_mncs
    def test_predict_rejects_wrong_arity(self) -> None:
        dataset = self.two_class()
        state, _ = engine.train(mncs=MNCS, dataset=dataset)
        with self.assertRaises(native.NativeError):
            engine.predict(mncs=MNCS, state=state, features=[1, 0, 0])


class EvaluationTests(Case):
    @need_mncs
    def test_held_out_beats_baseline(self) -> None:
        rows = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1],
                [10, 0], [11, 0], [12, 0], [10, 1], [11, 1], [12, 1]]
        labels = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        dataset = self.dataset(rows, labels)
        train, held = model.split_holdout(dataset, every=3)
        self.assertEqual(len(train["rows"]), 8)
        self.assertEqual(len(held["rows"]), 4)
        state, _ = engine.train(mncs=MNCS, dataset=train)
        report = engine.evaluate(mncs=MNCS, dataset=held, state=state)
        self.assertTrue(report["ok"])
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["correct"], 4)
        self.assertEqual(engine.accuracy(report), 1000)
        # Balanced held-out: majority baseline gets half right.
        self.assertEqual(engine.baseline_accuracy(report), 500)
        decision = engine.decide(
            mncs=MNCS, before_pm=engine.baseline_accuracy(report),
            after_pm=engine.accuracy(report))
        self.assertEqual(decision["decision"], codes.DECISION_COMMIT)

    @need_mncs
    def test_unseen_label_counts_against_accuracy(self) -> None:
        dataset = self.two_class()
        state, _ = engine.train(mncs=MNCS, dataset=dataset)
        novel = self.dataset([[1, 0], [50, 50]], [0, 2])
        report = engine.evaluate(mncs=MNCS, dataset=novel, state=state)
        self.assertTrue(report["ok"])
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["correct"], 1)
        # Confusion only tracks known-label rows: one entry total.
        self.assertEqual(sum(report["confusion"]), 1)

    @need_mncs
    def test_single_class_ties_baseline(self) -> None:
        dataset = self.dataset([[4, 0], [4, 0], [5, 1]], [9, 9, 9])
        state, _ = engine.train(mncs=MNCS, dataset=dataset)
        report = engine.evaluate(mncs=MNCS, dataset=dataset, state=state)
        self.assertTrue(report["ok"])
        # Perfect training fit that proves nothing: accuracy equals the
        # majority baseline, and the decision defers for real evidence.
        self.assertEqual(engine.accuracy(report),
                         engine.baseline_accuracy(report))
        decision = engine.decide(
            mncs=MNCS, before_pm=engine.baseline_accuracy(report),
            after_pm=engine.accuracy(report))
        self.assertEqual(decision["decision"], codes.DECISION_DEFER)

    @need_mncs
    def test_artifact_round_trip_preserves_predictions(self) -> None:
        dataset = self.two_class()
        state, train_report = engine.train(mncs=MNCS, dataset=dataset)
        artifact = model.build_artifact(
            name="round-trip", dataset=dataset,
            digest=model.dataset_digest(dataset), ndim=2, state=state,
            train_report=train_report)
        path = engine.save_artifact(state_dir=self.tmp, artifact=artifact)
        reloaded = store.read_json(path)
        for point in ([1, 0], [9, 0], [0, 5]):
            before = engine.predict(mncs=MNCS, state=state, features=point)
            after = engine.predict(mncs=MNCS, state=reloaded["state"],
                                   features=point)
            self.assertEqual((before["label"], before["dist2"]),
                             (after["label"], after["dist2"]))
        self.assertEqual(reloaded["dataset_digest"],
                         model.dataset_digest(dataset))


class DatasetModelTests(unittest.TestCase):
    def test_rejects_bad_shapes(self) -> None:
        base = {"schema_version": codes.DATASET_SCHEMA,
                "feature_names": ["x", "y"], "rows": [[0, 0]],
                "labels": [0], "label_names": {}}
        for mutate in (lambda d: d.update(feature_names=[]),
                       lambda d: d.update(rows=[[0]]),
                       lambda d: d.update(labels=["a"]),
                       lambda d: d.update(rows=[[0, "a"]]),
                       lambda d: d.update(rows=[[0, 0]] * 17),
                       lambda d: d.pop("schema_version")):
            document = json.loads(json.dumps(base))
            mutate(document)
            with self.assertRaises(model.DatasetError):
                model.validate_dataset(document)

    def test_split_is_deterministic(self) -> None:
        clean = model.validate_dataset({
            "schema_version": codes.DATASET_SCHEMA,
            "feature_names": ["x"], "rows": [[i] for i in range(6)],
            "labels": list(range(6)), "label_names": {}})
        train, held = model.split_holdout(clean, every=3)
        self.assertEqual(held["labels"], [2, 5])
        self.assertEqual(train["labels"], [0, 1, 3, 4])
        again_train, again_held = model.split_holdout(clean, every=3)
        self.assertEqual((train, held), (again_train, again_held))


if __name__ == "__main__":
    unittest.main()
