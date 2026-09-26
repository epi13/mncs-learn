"""Learning engine: train, predict, evaluate through native calls.

One engine pass trains a dataset into an artifact, predicts from an
artifact, or evaluates an artifact against held-out data. Every number
that means something (state, prediction, metric, decision) comes back
from a native `mncs call`; the host assembles identity and persists
records. Training and evaluation partitions are explicit arguments —
the engine never evaluates on the data it just fit unless told to.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import codes
from . import model
from . import native as bridge
from . import store

CENTROID_PROGRAM = bridge.learning_program("centroid.mncs")
CENTROID_MODULE = "mncs.learn.centroid.v1"
CONTRACT_PROGRAM = bridge.learning_program("contract.mncs")
CONTRACT_MODULE = "mncs.learn.contract.v1"


def _check(report: dict[str, Any], what: str) -> dict[str, Any]:
    if not report.get("ok", False):
        reason = report.get("reason", -1)
        name = codes.REASONS.get(reason, f"reason-{reason}")
        raise bridge.NativeError(f"{what} refused: {name} ({reason})")
    return report


def fresh_state(*, mncs: str, ndim: int) -> dict[str, Any]:
    report = bridge.call_record(
        mncs=mncs, program=CENTROID_PROGRAM, module=CENTROID_MODULE,
        function="fresh_state", args=[bridge.integer(ndim)])
    return _check(report, "fresh_state")["state"]


def train(*, mncs: str, dataset: dict[str, Any],
          ndim: int | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Train on a validated dataset; return (state, train_report)."""
    ndim = ndim or len(dataset["feature_names"])
    state = fresh_state(mncs=mncs, ndim=ndim)
    report = bridge.call_record(
        mncs=mncs, program=CENTROID_PROGRAM, module=CENTROID_MODULE,
        function="train_table",
        args=[model.table_arg(dataset), model.state_arg(state)])
    _check(report, "train_table")
    return report["state"], report


def predict(*, mncs: str, state: dict[str, Any],
            features: list[int]) -> dict[str, Any]:
    """Predict from stored state; return the native PredictOut."""
    ndim = int(state["ndim"])
    if len(features) != ndim:
        raise bridge.NativeError(
            f"feature arity {len(features)} != trained ndim {ndim}")
    report = bridge.call_record(
        mncs=mncs, program=CENTROID_PROGRAM, module=CENTROID_MODULE,
        function="predict_row",
        args=[model.state_arg(state),
              model.features_arg(features)])
    return _check(report, "predict_row")


def update(*, mncs: str, state: dict[str, Any], features: list[int],
           label: int) -> dict[str, Any]:
    """Incremental update: state + one labeled row -> new state."""
    report = bridge.call_record(
        mncs=mncs, program=CENTROID_PROGRAM, module=CENTROID_MODULE,
        function="train_row",
        args=[model.state_arg(state), model.features_arg(features),
              bridge.integer(label)])
    return _check(report, "train_row")["state"]


def evaluate(*, mncs: str, dataset: dict[str, Any],
             state: dict[str, Any]) -> dict[str, Any]:
    """Evaluate stored state on a dataset; return the EvalReport."""
    report = bridge.call_record(
        mncs=mncs, program=CENTROID_PROGRAM, module=CENTROID_MODULE,
        function="evaluate_table",
        args=[model.table_arg(dataset), model.state_arg(state)])
    return _check(report, "evaluate_table")


def accuracy(report: dict[str, Any]) -> int:
    """Accuracy in per-mille, computed host-side from exact counts."""
    total = int(report["total"])
    if total <= 0:
        raise bridge.NativeError("cannot score an empty evaluation")
    return (int(report["correct"]) * 1000) // total


def baseline_accuracy(report: dict[str, Any]) -> int:
    total = int(report["total"])
    if total <= 0:
        raise bridge.NativeError("cannot score an empty evaluation")
    return (int(report["majority_correct"]) * 1000) // total


def decide(*, mncs: str, before_pm: int, after_pm: int,
           constraints_ok: bool = True) -> dict[str, Any]:
    """Resolve fitness to commit/reject/defer via the native contract."""
    return bridge.call_record(
        mncs=mncs, program=CONTRACT_PROGRAM, module=CONTRACT_MODULE,
        function="decide",
        args=[bridge.integer(before_pm), bridge.integer(after_pm),
              bridge.boolean(constraints_ok)])


def check_eligible(*, mncs: str, capability: dict[str, Any],
                   obs_kind: int, rights_learn: bool) -> dict[str, Any]:
    """Eligibility via the native contract; returns the LearnRep."""
    cap = bridge.record("Capability", {
        "model": bridge.integer(capability["model"]),
        "class_code": bridge.integer(capability.get("class_code", 0)),
        "accepts_kind": bridge.integer(capability["accepts_kind"]),
        "operator": bridge.integer(capability["operator"]),
        "scope": bridge.integer(capability.get("scope", 0)),
        "timescale": bridge.integer(capability.get("timescale", 0)),
        "plast_cur_pm": bridge.integer(capability["plasticity"][0]),
        "plast_min_pm": bridge.integer(capability["plasticity"][1]),
        "plast_max_pm": bridge.integer(capability["plasticity"][2])})
    return bridge.call_record(
        mncs=mncs, program=CONTRACT_PROGRAM, module=CONTRACT_MODULE,
        function="check_eligible",
        args=[cap, bridge.integer(obs_kind),
              bridge.boolean(rights_learn)])


def save_artifact(*, state_dir: str | Path, artifact: dict[str, Any]) -> Path:
    paths = store.ensure(state_dir)
    name = artifact["name"]
    revision = artifact["revision"]
    path = paths["artifacts"] / f"{name}-r{revision}.json"
    store.write_json(path, artifact)
    return path


def save_evaluation(*, state_dir: str | Path,
                    evaluation: dict[str, Any]) -> Path:
    paths = store.ensure(state_dir)
    name = (f"{evaluation['artifact']}-eval-"
            f"{evaluation['dataset_digest'][7:15]}.json")
    path = paths["evaluations"] / name
    store.write_json(path, evaluation)
    return path
