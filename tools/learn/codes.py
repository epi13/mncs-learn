"""Shared numeric vocabulary: mirrors `native/mncs/learn/codes.mncs`.

The host never re-derives a learning decision; these numbers exist so it
can encode arguments and decode reasons without inventing semantics.
"""

SCOPE_INTERNAL = 0
SCOPE_RELATIONSHIP = 1
SCOPE_TOPOLOGY = 2
SCOPE_ROUTING = 3

TIMESCALE_FAST = 0
TIMESCALE_CONSOLIDATION = 1
TIMESCALE_EVOLUTION = 2

DECISION_COMMIT = 0
DECISION_REJECT = 1
DECISION_DEFER = 2
DECISIONS = {DECISION_COMMIT: "commit", DECISION_REJECT: "reject",
             DECISION_DEFER: "defer"}

OBS_FEATURE_LABEL = 0
OBS_FEATURE_ONLY = 1

OP_CENTROID_UPDATE = 0
OP_MEMORIZATION = 1
OP_NO_LEARNING = 2
OPERATORS = {OP_CENTROID_UPDATE: "centroid_update",
             OP_MEMORIZATION: "memorization",
             OP_NO_LEARNING: "no_learning"}

REASON_OK = 0
REASON_UNTRAINED = 1
REASON_SCHEMA_MISMATCH = 2
REASON_OVERFLOW = 3
REASON_EMPTY_DATASET = 4
REASON_DEGENERATE = 5
REASON_UNKNOWN_LABEL = 6
REASON_STALE_REVISION = 7
REASON_RIGHTS_DENIED = 8
REASON_INELIGIBLE_KIND = 9
REASON_PLASTICITY_ZERO = 10
REASON_OPERATOR_MISMATCH = 11
REASON_CAPACITY = 12
REASON_CONSTRAINT_VIOLATED = 13
REASON_NO_CHANGE = 14
REASON_IMPROVES = 15
REASON_REGRESSES = 16
REASON_SKIPPED_ROW = 17
REASONS = {
    REASON_OK: "ok", REASON_UNTRAINED: "untrained",
    REASON_SCHEMA_MISMATCH: "schema_mismatch", REASON_OVERFLOW: "overflow",
    REASON_EMPTY_DATASET: "empty_dataset", REASON_DEGENERATE: "degenerate",
    REASON_UNKNOWN_LABEL: "unknown_label",
    REASON_STALE_REVISION: "stale_revision",
    REASON_RIGHTS_DENIED: "rights_denied",
    REASON_INELIGIBLE_KIND: "ineligible_kind",
    REASON_PLASTICITY_ZERO: "plasticity_zero",
    REASON_OPERATOR_MISMATCH: "operator_mismatch",
    REASON_CAPACITY: "capacity",
    REASON_CONSTRAINT_VIOLATED: "constraint_violated",
    REASON_NO_CHANGE: "no_change", REASON_IMPROVES: "improves",
    REASON_REGRESSES: "regresses", REASON_SKIPPED_ROW: "skipped_row",
}

DEFINITION_SCHEMA = "mncs.learn-definition/1"
ARTIFACT_SCHEMA = "mncs.learn-artifact/1"
EVALUATION_SCHEMA = "mncs.learn-evaluation/1"
DATASET_SCHEMA = "mncs.learn-dataset/1"
