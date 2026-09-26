from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "oracle"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mncs_learn import (  # noqa: E402
    AdaptationProposal,
    Decision,
    Evaluation,
    Fitness,
    LearnableCapability,
    LearningEvent,
    LearningScheduler,
    Observation,
    OPERATORS,
    Plasticity,
    Rights,
)


class PrototypeOperator:
    name = "prototype_update"

    def supports(self, event, target):
        return "prototype_update" in target.capability.operators

    def propose(self, event, target):
        return [
            AdaptationProposal(
                id=f"proposal:{event.id}:{target.capability.model_id}",
                event_id=event.id,
                target_id=target.capability.model_id,
                target_revision=target.revision,
                operator=self.name,
                mutation_scopes=frozenset({"internal"}),
                timescale="fast",
                reason="high-confidence semantic prototype evidence",
                expected_effect={"semantic_consistency_delta": 0.1},
                patch={"append": event.observation.payload},
                provenance={"source": event.id, "evidence_ids": [event.observation.id]},
                reversible=True,
            )
        ]


class DummyPrototype:
    def __init__(self):
        self.state = []
        self._revision = 0
        self.commit_calls = 0
        self.capability = LearnableCapability(
            model_id="model:fox",
            model_class="semantic-prototype",
            accepts=frozenset({"semantic"}),
            operators=frozenset({"prototype_update"}),
            mutation_scopes=frozenset({"internal"}),
            timescales=frozenset({"fast"}),
            evaluation_dimensions=("semantic_consistency",),
            plasticity=Plasticity(current=0.7, minimum=0.05, maximum=0.95),
        )

    @property
    def revision(self):
        return f"rev:{self._revision}"

    def evaluate(self, proposal):
        before = Fitness({"semantic_consistency": 0.5}, {"rights": True}, 0.9)
        after = Fitness({"semantic_consistency": 0.6}, {"rights": True}, 0.9)
        return Evaluation(proposal.id, Decision.COMMIT, before, after, ("fitness improves",))

    def commit(self, proposal):
        self.commit_calls += 1
        self.state.append(proposal.patch["append"])
        self._revision += 1
        return self.revision


class MachineNativeLearningTests(unittest.TestCase):
    def event(self, *, learn=True):
        return LearningEvent(
            id="event:1",
            observation=Observation(
                id="obs:1",
                kind="semantic",
                data_type="language/semantic-graph",
                payload={"entity": "fox"},
                provenance={"source": "test"},
                confidence=0.97,
                rights=Rights(learn=learn),
            ),
            desired_effects=("generalize",),
            targets=("model:fox",),
        )

    def test_operator_catalog_is_heterogeneous(self):
        expected = {
            "gradient",
            "hebbian",
            "bayesian_update",
            "prototype_update",
            "rule_induction",
            "graph_edge_update",
            "reinforcement",
            "memorization",
            "node_split",
            "node_merge",
            "route_update",
            "no_learning",
        }
        self.assertTrue(expected <= OPERATORS.keys())
        scopes = set().union(*(spec.scopes for spec in OPERATORS.values()))
        self.assertEqual({"internal", "relationship", "topology", "routing"}, scopes)

    def test_event_cannot_mutate_before_commit(self):
        target = DummyPrototype()
        scheduler = LearningScheduler([PrototypeOperator()])
        event = self.event()

        self.assertEqual([], target.state)
        results = scheduler.process(event, [target])

        self.assertEqual(1, target.commit_calls)
        self.assertEqual([{"entity": "fox"}], target.state)
        self.assertEqual(Decision.COMMIT, results[0].decision)
        self.assertEqual("rev:1", results[0].resulting_revision)

    def test_rights_can_block_learning(self):
        target = DummyPrototype()
        scheduler = LearningScheduler([PrototypeOperator()])
        results = scheduler.process(self.event(learn=False), [target])

        self.assertEqual(0, target.commit_calls)
        self.assertEqual([], target.state)
        self.assertIsNone(results[0].proposal_id)
        self.assertEqual("learning right denied", results[0].reason)

    def test_zero_plasticity_blocks_learning(self):
        target = DummyPrototype()
        target.capability = LearnableCapability(
            model_id="model:fox",
            model_class="semantic-prototype",
            accepts=frozenset({"semantic"}),
            operators=frozenset({"prototype_update"}),
            mutation_scopes=frozenset({"internal"}),
            timescales=frozenset({"fast"}),
            evaluation_dimensions=("semantic_consistency",),
            plasticity=Plasticity(current=0.0, minimum=0.0, maximum=1.0),
        )
        scheduler = LearningScheduler([PrototypeOperator()])
        results = scheduler.process(self.event(), [target])
        self.assertEqual("target plasticity is zero", results[0].reason)
        self.assertEqual(0, target.commit_calls)

    def test_schema_and_example_are_machine_readable(self):
        schema = json.loads((ROOT / "spec" / "mncs-learn-v0.schema.json").read_text())
        example = json.loads((ROOT / "examples" / "fox-learning-cycle.json").read_text())
        boundary = json.loads((ROOT / "mncs-boundary.json").read_text())

        self.assertEqual("MNCS Learn v0 bootstrap contracts", schema["title"])
        self.assertEqual("learning_event", example["learning_event"]["kind"])
        self.assertEqual(
            "Learning is evidence-governed state transition across heterogeneous computational state.",
            boundary["thesis"],
        )
        self.assertEqual(
            {"internal", "relationship", "topology", "routing"},
            set(boundary["mutation_scopes"]),
        )

    def test_foundation_docs_are_present(self):
        required = [
            "README.md",
            "AGENTS.md",
            "ROADMAP.md",
            "rfcs/0001-machine-native-learning.md",
            "docs/architecture.md",
            "docs/operators.md",
            "docs/integration.md",
            "spec/mncs-learn-v0.schema.json",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
