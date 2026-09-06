# Roadmap

This roadmap is ordered to keep `mncs-learn` machine-native rather than accidentally growing a permanent Python training framework.

## Phase 0 — Foundation (this merge)

Goal: establish the semantic boundary before implementation pressure narrows it.

- [x] Define learning as evidence-governed state transition.
- [x] Separate internal, relationship, topology, and routing learning.
- [x] Define proposal -> evaluation -> decision -> commit.
- [x] Define fast adaptation, consolidation, and evolution.
- [x] Establish heterogeneous operator vocabulary.
- [x] Make rights/provenance part of eligibility.
- [x] Treat plasticity as state/policy.
- [x] Treat split/merge/retirement/routing as learning operations.
- [x] Add bootstrap schema and executable reference lifecycle.
- [x] Add MNCS Actions conformance boundary.

## Phase 1 — Native contract pressure

Goal: discover exactly what `mncs-language` and stdlib must support to express v0 without host-language shadow semantics.

- [ ] Express Observation/LearningEvent/Capability/Proposal/Fitness/Evaluation as native MNCS types.
- [ ] Add stable tagged/variant data support where needed.
- [ ] Add deterministic canonical serialization/digest support.
- [ ] Add explicit capability negotiation primitives or stdlib conventions.
- [ ] Add policy/effect boundaries suitable for rights-aware learning.
- [ ] Add revision/checkpoint identifiers as first-class types/conventions.
- [ ] Compile and execute contract tests through MNCS-language/WASM.
- [ ] Replace bootstrap JSON/Python checks where native equivalents become authoritative.

**Rule:** do not create fake `.mncs` examples to mark these items done. Missing language support is useful pressure and should produce concrete language issues/RFCs.

## Phase 2 — Memory handshake

Goal: make proposal/commit semantics real against `mncs-memory`.

- [ ] Define target snapshot/revision contract.
- [ ] Define staged mutation/compare-and-commit semantics.
- [ ] Define relationship update contract.
- [ ] Define graph revision semantics for topology changes.
- [ ] Preserve evidence/provenance ancestry through state revisions.
- [ ] Define stale proposal handling.
- [ ] Define checkpoint/rollback capability advertisement.
- [ ] Demonstrate one internal-state and one graph-edge learning flow end to end.

## Phase 3 — Ingest handshake

Goal: accept heterogeneous observations without source-specific learning logic.

- [ ] Align `mncs-ingest` observation envelope with learning eligibility needs.
- [ ] Define data/semantic kind identifiers.
- [ ] Define novelty/contradiction/redundancy signal handoff vs learn-side derivation.
- [ ] Preserve rights and provenance across the boundary.
- [ ] Test text, numeric/temporal, image/feature, and graph/relation observations.

## Phase 4 — Operator adapters

Goal: prove heterogeneity with meaningfully different learning families.

Implement or integrate at least:

- [ ] prototype/centroid learner,
- [ ] Bayesian/statistical learner,
- [ ] graph edge learner,
- [ ] state-machine/symbolic learner,
- [ ] gradient learner through MNEL or another appropriate backend,
- [ ] memorization/no-learning path.

Each implementation must use the same proposal/evaluation/commit lifecycle without pretending its internal state is universal.

## Phase 5 — Plasticity and continual learning

Goal: make stability/adaptability explicit.

- [ ] Implement bounded plasticity state.
- [ ] Add novelty-driven plasticity adjustment.
- [ ] Add contradiction-driven reopening of stable models.
- [ ] Add maturity/stability accumulation.
- [ ] Add replay/consolidation policy.
- [ ] Add catastrophic-forgetting pressure tests across at least two operator classes.
- [ ] Distinguish rights-mandated deletion from optimization-based forgetting.

## Phase 6 — Structural learning

Goal: make the graph itself trainable under governance.

- [ ] Node split proposal/evaluation/commit.
- [ ] Node merge proposal/evaluation/commit.
- [ ] Node creation/specialization.
- [ ] Node retirement.
- [ ] Edge pruning and relation retyping.
- [ ] Route update learning.
- [ ] State migration and ancestry preservation.
- [ ] Shadow graph / rollback strategy for topology proposals.

A successful demonstration should show a micro-model becoming persistently multimodal, proposing a split, evaluating descendants, committing a graph revision, and preserving provenance.

## Phase 7 — Distributed learning through Fabric

Goal: separate semantic learning from execution placement.

- [ ] Publish operator execution requirements as machine-readable capabilities.
- [ ] Route eligible operators to appropriate workers.
- [ ] Distinguish unsupported/unavailable toolchains from failed learning.
- [ ] Exercise Linux, Windows, ARM/Raspberry Pi, and RISC-V emulation where applicable.
- [ ] Exercise CUDA/PTX for gradient or numeric operators.
- [ ] Explore WASM/eBPF execution only where semantics fit safely.
- [ ] Preserve proposal identity and evidence across remote execution.
- [ ] Test worker loss/retry without double commit.

## Phase 8 — Learning the router

Goal: make activation topology adaptive while retaining hard policy boundaries.

- [ ] Track downstream utility of routes.
- [ ] Generate route-update proposals.
- [ ] Distinguish semantic relationships from activation routing.
- [ ] Prevent learned routing from bypassing rights or hard capability constraints.
- [ ] Test sparse activation and local neighborhood learning.

## Phase 9 — Consolidation and evolution scheduler

Goal: support multiple timescales natively.

- [ ] Event-driven fast adaptation scheduler.
- [ ] Evidence-window/checkpoint consolidation scheduler.
- [ ] Structural evolution scheduler.
- [ ] Budget/resource-aware operator selection.
- [ ] Deferred proposal queues and re-evaluation.
- [ ] Explain why a proposal was scheduled at a given timescale.

## Phase 10 — Self-directed model ecology

Goal: allow a population of micro-models to specialize and reorganize without losing governance, auditability, or reproducibility.

Research targets:

- [ ] learned operator selection,
- [ ] learned plasticity policy,
- [ ] local competition/cooperation between neighboring micro-models,
- [ ] micro-model birth and specialization,
- [ ] utility/resource-driven retirement,
- [ ] cluster-level models composed from micro-model neighborhoods,
- [ ] safe automatic backend/model-class replacement,
- [ ] semantic replay and counterfactual evaluation before structural commit.

This phase should only advance after topology changes are observable, reversible where feasible, and constrained by strong evidence policy.

## Cross-cutting definition of progress

A feature is not considered machine-native merely because it is implemented inside an MNCS repository. Progress should continuously increase:

1. **native expression** — more semantics represented by `mncs-language` rather than host scaffolding;
2. **heterogeneity** — more fundamentally different model/data classes using one contract;
3. **evidence quality** — stronger provenance, rights, evaluation, and replay;
4. **portability** — the same contract survives different workers/backends;
5. **structural capability** — learning extends from parameters to relationships, topology, and routing;
6. **conformance pressure** — `mncs-actions` can prove rather than merely document the behavior.
