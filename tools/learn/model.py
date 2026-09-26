"""Dataset and artifact model: typed validation, identity, splits.

A dataset is small, explicit JSON (`mncs.learn-dataset/1`): feature
names (semantic identity, never erased), rows of integers or null
(null means Missing — never zero), integer labels, and label names.
The host validates shapes here, encodes a `mncs-data` Table for the
native call, and digests the canonical JSON for artifact lineage.

Learned artifacts (`mncs.learn-artifact/1`) carry everything Lineage
needs without Learn owning a graph: algorithm identity, feature and
class maps, native state, dataset digest, configuration, metrics, and
revision.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from . import codes
from . import native as bridge


class DatasetError(Exception):
    """A dataset or artifact document is invalid."""


MAX_ROWS = 16
MAX_DIMS = 3


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DatasetError(message)


def validate_dataset(document: Any) -> dict[str, Any]:
    _require(isinstance(document, dict), "dataset must be an object")
    _require(document.get("schema_version") == codes.DATASET_SCHEMA,
              "unknown dataset schema")
    names = document.get("feature_names")
    _require(isinstance(names, list) and 1 <= len(names) <= MAX_DIMS,
              "feature_names must list 1..3 names")
    _require(all(isinstance(name, str) and name for name in names),
              "feature names must be nonempty strings")
    rows = document.get("rows")
    _require(isinstance(rows, list) and 1 <= len(rows) <= MAX_ROWS,
              "rows must list 1..16 rows")
    labels = document.get("labels")
    _require(isinstance(labels, list) and len(labels) == len(rows),
              "labels must match rows one-to-one")
    label_names = document.get("label_names", {})
    _require(isinstance(label_names, dict), "label_names must be a map")
    for index, row in enumerate(rows):
        _require(isinstance(row, list) and len(row) == len(names),
                  f"row {index} must have {len(names)} entries")
        for value in row:
            _require(value is None or isinstance(value, int),
                      f"row {index} entries must be int or null")
    for index, label in enumerate(labels):
        _require(isinstance(label, int), f"label {index} must be int")
    for key, name in label_names.items():
        _require(isinstance(name, str) and name,
                  f"label name for {key} must be a nonempty string")
    return {"schema_version": codes.DATASET_SCHEMA,
            "feature_names": list(names),
            "rows": [list(row) for row in rows],
            "labels": list(labels),
            "label_names": {str(key): name for key, name in
                            label_names.items()}}


def dataset_digest(clean: dict[str, Any]) -> str:
    """Canonical sha256 over the validated dataset (lineage identity)."""
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _cell(value: Any) -> dict[str, Any]:
    if value is None:
        return {"finite": {"type": "Cell", "variant": "Missing"}}
    return {"finite": {"type": "Cell", "variant": "Int",
                       "payload": {"value": bridge.integer(value)}}}


def _int_column(name: str) -> dict[str, Any]:
    encoded = [{"byte": {"value": byte}}
               for byte in name.encode("utf-8")[:32]]
    while len(encoded) < 32:
        encoded.append({"byte": {"value": 0}})
    return bridge.record("ColumnSpec", {
        "name": bridge.sequence(encoded),
        "name_len": bridge.integer(min(len(name.encode("utf-8")), 32)),
        "kind": {"finite": {"type": "CellKind", "variant": "Int"}},
        "required": bridge.boolean(False)})


def table_arg(clean: dict[str, Any]) -> dict[str, Any]:
    """Encode a validated dataset as a `mncs-data` Table wire value."""
    names = clean["feature_names"] + ["label"]
    columns = [_int_column(name) for name in names]
    while len(columns) < 4:
        columns.append(_int_column(f"_pad{len(columns)}"))
    schema = bridge.record("Schema4",
                           {"cols": bridge.sequence(columns[:4])})
    encoded_rows = []
    for row, label in zip(clean["rows"], clean["labels"]):
        cells = [_cell(value) for value in row]
        while len(cells) < 3:
            cells.append(_cell(None))
        encoded_rows.append(
            bridge.sequence((cells[:3] + [_cell(label)])))
    while len(encoded_rows) < 16:
        pad = bridge.sequence([_cell(None)] * 4)
        encoded_rows.append(pad)
    return bridge.record("Table", {
        "schema": schema,
        "rows": bridge.sequence(encoded_rows),
        "row_count": bridge.integer(len(clean["rows"]))})


def state_arg(state: dict[str, Any]) -> dict[str, Any]:
    """Encode a stored CentroidState for a native call."""
    return bridge.record("CentroidState", {
        "nclasses": bridge.integer(state["nclasses"]),
        "class_ids": bridge.sequence(
            [bridge.integer(v) for v in state["class_ids"]]),
        "counts": bridge.sequence(
            [bridge.integer(v) for v in state["counts"]]),
        "sums": bridge.sequence(
            [bridge.sequence([bridge.integer(v) for v in row])
             for row in state["sums"]]),
        "revision": bridge.integer(state["revision"]),
        "ndim": bridge.integer(state["ndim"])})


def features_arg(values: list[int]) -> dict[str, Any]:
    padded = list(values)[:4]
    while len(padded) < 4:
        padded.append(0)
    return bridge.sequence([bridge.integer(v) for v in padded])


def split_holdout(clean: dict[str, Any], every: int = 3) -> tuple[
        dict[str, Any], dict[str, Any]]:
    """Deterministic split: every `every`-th row (1-based) is held out.

    Membership is positional and stable — no rerandomization, and the
    split is reproducible from the dataset plus `every`.
    """
    _require(every >= 2, "holdout stride must be >= 2")
    train = {**clean, "rows": [], "labels": []}
    held = {**clean, "rows": [], "labels": []}
    for index, (row, label) in enumerate(zip(clean["rows"],
                                             clean["labels"])):
        target = held if (index + 1) % every == 0 else train
        target["rows"].append(row)
        target["labels"].append(label)
    _require(train["rows"], "split left no training rows")
    _require(held["rows"], "split left no held-out rows")
    return train, held


def build_artifact(*, name: str, dataset: dict[str, Any],
                   digest: str, ndim: int, state: dict[str, Any],
                   train_report: dict[str, Any],
                   metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    """Assemble a learned artifact from a training result."""
    classes = []
    for slot in range(state["nclasses"]):
        label = state["class_ids"][slot]
        classes.append({"label": label,
                        "name": dataset["label_names"].get(str(label)),
                        "count": state["counts"][slot],
                        "sums": state["sums"][slot][:ndim]})
    return {"schema_version": codes.ARTIFACT_SCHEMA,
            "name": name,
            "algorithm": codes.OPERATORS[codes.OP_CENTROID_UPDATE],
            "operator": codes.OP_CENTROID_UPDATE,
            "scope": codes.SCOPE_INTERNAL,
            "timescale": codes.TIMESCALE_FAST,
            "feature_names": dataset["feature_names"][:ndim],
            "label_names": dataset["label_names"],
            "classes": classes,
            "state": state,
            "dataset_digest": digest,
            "dataset_rows": len(dataset["rows"]),
            "config": {"ndim": ndim},
            "train": {"rows_seen": train_report["rows_seen"],
                      "rows_used": train_report["rows_used"],
                      "rows_skipped": train_report["rows_skipped"]},
            "metrics": metrics or {},
            "revision": state["revision"]}
