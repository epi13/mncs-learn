"""Bootstrap operator vocabulary for mncs-learn.

This module is intentionally declarative. It does not make Python the
normative learning runtime; it gives tests and early integrations a concrete,
machine-readable catalog while MNCS-language support is developed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class OperatorSpec:
    name: str
    scopes: FrozenSet[str]
    timescales: FrozenSet[str]
    description: str


OPERATORS = {
    spec.name: spec
    for spec in (
        OperatorSpec("gradient", frozenset({"internal"}), frozenset({"fast", "consolidation"}), "Differentiable parameter optimization."),
        OperatorSpec("hebbian", frozenset({"internal", "relationship"}), frozenset({"fast"}), "Strengthen co-activated state or relationships."),
        OperatorSpec("anti_hebbian", frozenset({"internal", "relationship"}), frozenset({"fast"}), "Decorrelate or weaken co-activation."),
        OperatorSpec("bayesian_update", frozenset({"internal"}), frozenset({"fast"}), "Update probabilistic belief state."),
        OperatorSpec("prototype_update", frozenset({"internal"}), frozenset({"fast"}), "Add or move representative prototypes."),
        OperatorSpec("centroid_update", frozenset({"internal"}), frozenset({"fast"}), "Update cluster representative state."),
        OperatorSpec("nearest_neighbor", frozenset({"internal"}), frozenset({"fast"}), "Adapt instance-based reference state."),
        OperatorSpec("rule_induction", frozenset({"internal"}), frozenset({"consolidation"}), "Derive or revise symbolic rules."),
        OperatorSpec("threshold_adaptation", frozenset({"internal", "routing"}), frozenset({"fast"}), "Adjust decision or activation thresholds."),
        OperatorSpec("state_transition_update", frozenset({"internal"}), frozenset({"fast"}), "Revise state-machine transitions."),
        OperatorSpec("graph_edge_update", frozenset({"relationship"}), frozenset({"fast", "consolidation"}), "Create or revise graph relationships."),
        OperatorSpec("graph_pruning", frozenset({"relationship", "topology"}), frozenset({"consolidation"}), "Remove low-value graph structure under policy."),
        OperatorSpec("reinforcement", frozenset({"internal", "relationship", "routing"}), frozenset({"fast", "consolidation"}), "Adapt from reward or utility signals."),
        OperatorSpec("memorization", frozenset({"internal"}), frozenset({"fast"}), "Preserve evidence without implying generalization."),
        OperatorSpec("forgetting", frozenset({"internal", "relationship", "topology"}), frozenset({"consolidation"}), "Explicitly weaken or remove learned state."),
        OperatorSpec("temporal_decay", frozenset({"internal", "relationship", "routing"}), frozenset({"consolidation"}), "Reduce influence over time or non-use."),
        OperatorSpec("replay", frozenset({"internal", "relationship"}), frozenset({"consolidation"}), "Re-present prior evidence for stabilization/integration."),
        OperatorSpec("distillation", frozenset({"internal", "topology"}), frozenset({"consolidation"}), "Transfer behavior into another representation."),
        OperatorSpec("compression", frozenset({"internal", "topology"}), frozenset({"consolidation"}), "Reduce representation cost while preserving utility."),
        OperatorSpec("node_split", frozenset({"topology", "relationship", "routing"}), frozenset({"evolution"}), "Specialize one node into descendants."),
        OperatorSpec("node_merge", frozenset({"topology", "relationship", "routing"}), frozenset({"evolution"}), "Reconcile nodes into a descendant."),
        OperatorSpec("route_update", frozenset({"routing"}), frozenset({"fast", "consolidation", "evolution"}), "Adapt evidence/activation routing."),
        OperatorSpec("no_learning", frozenset(), frozenset({"fast", "consolidation", "evolution"}), "Intentionally perform no durable adaptation."),
    )
}

MUTATION_SCOPES = frozenset({"internal", "relationship", "topology", "routing"})
TIMESCALES = frozenset({"fast", "consolidation", "evolution"})
DECISIONS = frozenset({"commit", "reject", "defer"})
