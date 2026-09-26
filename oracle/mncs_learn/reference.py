"""Executable bootstrap reference for the mncs-learn lifecycle.

This module proves protocol invariants. It is deliberately small and MUST NOT
be treated as the normative MNCS learning runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .operators import DECISIONS, MUTATION_SCOPES, OPERATORS, TIMESCALES


class Decision(str, Enum):
    COMMIT = "commit"
    REJECT = "reject"
    DEFER = "defer"


@dataclass(frozen=True)
class Rights:
    inspect: bool = True
    reason: bool = True
    learn: bool = True
    retain: bool = True
    propagate: bool = True


@dataclass(frozen=True)
class Observation:
    id: str
    kind: str
    data_type: str
    payload: Any
    provenance: Mapping[str, Any]
    confidence: float
    rights: Rights = field(default_factory=Rights)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("observation confidence must be in [0, 1]")


@dataclass(frozen=True)
class LearningEvent:
    id: str
    observation: Observation
    desired_effects: tuple[str, ...]
    context: Mapping[str, Any] = field(default_factory=dict)
    targets: tuple[str, ...] = ()
    signals: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.desired_effects:
            raise ValueError("a learning event needs at least one desired effect")


@dataclass(frozen=True)
class Plasticity:
    current: float
    minimum: float = 0.0
    maximum: float = 1.0
    novelty_response: float = 0.0
    contradiction_response: float = 0.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.minimum <= self.current <= self.maximum <= 1.0):
            raise ValueError("plasticity must satisfy 0 <= minimum <= current <= maximum <= 1")


@dataclass(frozen=True)
class LearnableCapability:
    model_id: str
    model_class: str
    accepts: frozenset[str]
    operators: frozenset[str]
    mutation_scopes: frozenset[str]
    timescales: frozenset[str]
    evaluation_dimensions: tuple[str, ...]
    plasticity: Plasticity

    def __post_init__(self) -> None:
        unknown_operators = self.operators - OPERATORS.keys()
        if unknown_operators:
            raise ValueError(f"unknown operators: {sorted(unknown_operators)}")
        if not self.mutation_scopes <= MUTATION_SCOPES:
            raise ValueError("capability contains unknown mutation scope")
        if not self.timescales <= TIMESCALES:
            raise ValueError("capability contains unknown timescale")


@dataclass(frozen=True)
class AdaptationProposal:
    id: str
    event_id: str
    target_id: str
    operator: str
    mutation_scopes: frozenset[str]
    timescale: str
    reason: str
    expected_effect: Mapping[str, Any]
    patch: Mapping[str, Any]
    preconditions: tuple[Mapping[str, Any], ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    target_revision: str | None = None
    reversible: bool = False

    def __post_init__(self) -> None:
        if self.operator not in OPERATORS:
            raise ValueError(f"unknown operator: {self.operator}")
        if not self.mutation_scopes <= MUTATION_SCOPES:
            raise ValueError("proposal contains unknown mutation scope")
        if self.timescale not in TIMESCALES:
            raise ValueError("proposal contains unknown timescale")


@dataclass(frozen=True)
class Fitness:
    dimensions: Mapping[str, float]
    constraints: Mapping[str, bool]
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("fitness confidence must be in [0, 1]")

    @property
    def constraints_satisfied(self) -> bool:
        return all(self.constraints.values())


@dataclass(frozen=True)
class Evaluation:
    proposal_id: str
    decision: Decision
    before: Fitness
    after: Fitness
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision.value not in DECISIONS:
            raise ValueError("unknown decision")
        if not self.reasons:
            raise ValueError("evaluation needs at least one reason")


class LearnableAdapter(Protocol):
    """Adapter between common learning semantics and heterogeneous model state."""

    @property
    def capability(self) -> LearnableCapability: ...

    @property
    def revision(self) -> str: ...

    def evaluate(self, proposal: AdaptationProposal) -> Evaluation: ...

    def commit(self, proposal: AdaptationProposal) -> str: ...


class LearningOperator(Protocol):
    name: str

    def supports(self, event: LearningEvent, target: LearnableAdapter) -> bool: ...

    def propose(self, event: LearningEvent, target: LearnableAdapter) -> Sequence[AdaptationProposal]: ...


@dataclass(frozen=True)
class ProcessResult:
    event_id: str
    target_id: str
    proposal_id: str | None
    decision: Decision | None
    resulting_revision: str | None
    reason: str


class LearningScheduler:
    """Minimal proposal/evaluation/commit orchestrator.

    Important: `process` never asks an observation to mutate a target. An
    operator must first create a proposal; only an accepted evaluation may
    reach `commit`.
    """

    def __init__(self, operators: Iterable[LearningOperator]) -> None:
        self._operators = {operator.name: operator for operator in operators}

    @staticmethod
    def eligible(event: LearningEvent, target: LearnableAdapter) -> tuple[bool, str]:
        capability = target.capability
        if not event.observation.rights.learn:
            return False, "learning right denied"
        if event.observation.kind not in capability.accepts and event.observation.data_type not in capability.accepts:
            return False, "observation kind/data type not accepted"
        if event.targets and capability.model_id not in event.targets:
            return False, "target not selected by event"
        if capability.plasticity.current <= 0.0:
            return False, "target plasticity is zero"
        return True, "eligible"

    def process(self, event: LearningEvent, targets: Iterable[LearnableAdapter]) -> list[ProcessResult]:
        results: list[ProcessResult] = []
        for target in targets:
            allowed, reason = self.eligible(event, target)
            if not allowed:
                results.append(ProcessResult(event.id, target.capability.model_id, None, None, None, reason))
                continue

            compatible = [
                self._operators[name]
                for name in target.capability.operators
                if name in self._operators and self._operators[name].supports(event, target)
            ]
            if not compatible:
                results.append(ProcessResult(event.id, target.capability.model_id, None, None, None, "no compatible operator"))
                continue

            for operator in compatible:
                proposals = operator.propose(event, target)
                for proposal in proposals:
                    evaluation = target.evaluate(proposal)
                    resulting_revision = None
                    if evaluation.decision is Decision.COMMIT:
                        resulting_revision = target.commit(proposal)
                    results.append(
                        ProcessResult(
                            event_id=event.id,
                            target_id=target.capability.model_id,
                            proposal_id=proposal.id,
                            decision=evaluation.decision,
                            resulting_revision=resulting_revision,
                            reason="; ".join(evaluation.reasons),
                        )
                    )
        return results
