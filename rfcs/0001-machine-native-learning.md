# RFC 0001: Machine-Native Learning

- **Status:** Accepted foundation
- **Repository:** `mncs-learn`
- **Scope:** Learning semantics across heterogeneous MNCS micro-models
- **Version:** 0

## 1. Summary

MNCS SHALL define learning as **evidence-governed state transition across heterogeneous computational state**.

The learning contract SHALL NOT require a shared parameter representation, tensor representation, optimizer, loss function, batch model, epoch model, or neural architecture. These MAY exist inside a particular learning operator or model class.

A durable learning change SHALL be represented as an adaptation proposal, evaluated under the target's declared learning policy, and committed only after an explicit decision.

## 2. Motivation

The MNCS micro-model architecture permits a computational graph in which neighboring nodes are not necessarily instances of one model family. A graph may include neural micro-models, statistical estimators, semantic prototypes, episodic stores, state machines, symbolic structures, routers, graph neighborhoods, controllers, and other specialized forms.

If the common training contract were defined as gradient optimization, every non-gradient learner would become an exception. This RFC instead places state transition at the common layer and makes gradient descent one operator in a larger learning vocabulary.

This also permits the graph itself to learn. Relationships, routing, node identity, specialization, split/merge behavior, and retirement may all be evidence-driven state transitions.

## 3. Terminology

### 3.1 Observation

A typed machine-native description of something observed or derived. An observation carries enough provenance, confidence, rights, temporal/contextual, and data-type information to support learning eligibility and routing.

### 3.2 Evidence

An observation plus the contextual signals relevant to learning: provenance, confidence, recency, redundancy, contradiction, rights, and other policy-relevant metadata.

### 3.3 Learning event

An evidence-bearing request for the learning plane to consider adaptation. A learning event may identify candidate targets and desired effects but MUST NOT itself mutate them.

### 3.4 Learnable

Any target capable of declaring a learning capability and participating in the proposal/evaluation/commit protocol. A learnable is not required to be a neural model.

### 3.5 Learning operator

A mechanism that can produce an adaptation proposal for an eligible learnable. Examples include gradient, Bayesian update, prototype update, graph reinforcement, rule induction, replay, node split, or `no_learning`.

### 3.6 Adaptation proposal

A candidate transition from one computational state to another. It identifies target, operator, mutation scope, timescale, preconditions, proposed change, expected effect, and evidence ancestry.

### 3.7 Fitness

A structured evaluation state containing zero or more metric dimensions plus constraints and confidence. Fitness is not required to reduce to one scalar.

### 3.8 Evaluation

The process/result that resolves a proposal to `commit`, `reject`, or `defer` under declared policy.

### 3.9 Consolidation

A slower process that integrates, compresses, replays, strengthens, weakens, or migrates accumulated learning state.

### 3.10 Evolution

Structural adaptation such as node split/merge/create/retire, model-class replacement, topology changes, or routing changes.

## 4. Normative invariants

### I1 — Heterogeneous state

The common protocol MUST permit learnables with unrelated internal representations.

### I2 — Transactional durable mutation

A learning event MUST NOT directly mutate durable target state. Durable mutation MUST be represented by a proposal and explicit decision before commit.

Transient activation used to evaluate an event is not considered a durable mutation.

### I3 — Explicit mutation scope

Every adaptation proposal MUST identify one or more of:

- `internal`
- `relationship`
- `topology`
- `routing`

### I4 — Explicit timescale

Every proposal MUST identify a learning timescale:

- `fast`
- `consolidation`
- `evolution`

Implementations MAY schedule these differently. A backend MAY coalesce them but MUST preserve semantic distinction in evidence.

### I5 — Evidence ancestry

A proposal MUST be traceable to the event/evidence that caused it, unless it is a policy-scheduled consolidation/evolution action whose ancestry is a declared evidence set or checkpoint.

### I6 — Rights-aware eligibility

The learning plane MUST be able to distinguish permission to inspect/use an observation for immediate reasoning from permission to retain it or use it to alter generalized model state.

A denied learning right MUST prevent adaptation even when routing/activation is otherwise possible.

### I7 — Capability negotiation

A learnable MUST advertise enough capability information for the runtime to determine whether an event/operator pairing is eligible without assuming implementation-specific state.

### I8 — Evaluation plurality

The common contract MUST NOT require a scalar loss. A target/operator MAY use one, but the generic fitness representation supports multiple dimensions and hard constraints.

### I9 — No-op learning

`no_learning` MUST be representable as an intentional outcome. Systems MUST NOT infer that an observed datum should generalize merely because it was readable, useful, memorable, or frequently observed.

### I10 — Structural learning is learning

Evidence-driven changes to edges, routing, node identity, node population, and topology MUST use the same governed adaptation lifecycle as internal parameter/state updates.

## 5. Learning dimensions

MNCS recognizes four independently learnable dimensions.

### 5.1 Internal learning

Changes state contained by one micro-model. Examples:

- neural parameters,
- Bayesian priors/posteriors,
- centroids/prototypes,
- symbolic rules,
- thresholds,
- transition probabilities,
- compression dictionaries,
- episodic contents,
- controller parameters.

### 5.2 Relationship learning

Changes a relation between models or states. Examples:

- edge strength,
- relation type,
- directionality,
- confidence,
- activation eligibility,
- temporal decay,
- inhibitory/excitatory character.

Relationship learning need not change either endpoint internally.

### 5.3 Topological learning

Changes graph membership or structure. Examples:

- create a specialist,
- split a multimodal node,
- merge redundant/converged nodes,
- retire an obsolete node,
- replace a model class,
- reorganize a cluster.

Topology changes require stronger preconditions and evaluation because their blast radius exceeds local state updates.

### 5.4 Routing learning

Changes how evidence or activation moves through the graph. Examples:

- observation eligibility,
- target selection,
- activation fan-out,
- route priorities,
- learned suppression,
- downstream utility-based routing.

Routing is considered separately from relationship state because a semantic relationship may exist without implying activation policy.

## 6. Lifecycle

The conceptual lifecycle is:

```text
OBSERVE -> ROUTE -> ACTIVATE -> COMPARE -> PROPOSE -> TEST -> ADAPT -> CONSOLIDATE
```

### 6.1 Observe

Receive or derive a typed observation. The producer owns source parsing; the learning plane consumes the observation contract.

### 6.2 Route

Identify candidate learnables using observation type, context, model capability, rights, graph/routing state, and policy.

### 6.3 Activate

Allow eligible targets or neighborhoods to compute transient responses needed for comparison or proposal generation.

### 6.4 Compare

Determine novelty, prediction error, consistency, contradiction, redundancy, utility, or other target-specific signals.

### 6.5 Propose

Select eligible operator(s) and construct one or more adaptation proposals. Proposal generation MUST remain separable from commit.

### 6.6 Test

Evaluate expected or staged effects against target-specific fitness dimensions and constraints. Higher-blast-radius proposals MAY require sandboxing, replay, shadow state, quorum, or external validators.

### 6.7 Adapt

Commit proposals that satisfy policy. Reject or defer the rest. A commit SHOULD emit a durable record binding proposal, target revision, decision evidence, and resulting revision/state identity.

### 6.8 Consolidate

Integrate accumulated fast learning into stable structures according to policy. Consolidation MAY itself emit proposals and therefore remains governed.

## 7. Learning event

A learning event SHOULD contain:

- stable event identity,
- observation identity/payload reference,
- provenance,
- confidence,
- rights,
- context,
- optional candidate targets,
- desired effects,
- temporal information,
- optional contradiction/novelty/redundancy signals.

Candidate targets are hints, not authority. Runtime policy remains responsible for final eligibility.

## 8. Learnable capability

A learnable capability SHOULD declare:

- model identity and class,
- accepted observation/data kinds,
- supported operators,
- supported mutation scopes,
- supported timescales,
- fitness/evaluation dimensions,
- plasticity state/policy,
- resource or placement constraints when relevant,
- rollback/checkpoint support where relevant.

The capability MUST NOT require disclosure of internal model state merely to route an event.

## 9. Operator selection

Operator selection is a negotiation among:

- event kind and desired effect,
- model capability,
- current plasticity,
- rights/provenance policy,
- graph context,
- resource availability,
- timescale,
- prior operator performance,
- safety/stability constraints.

Multiple proposals MAY be generated for one event/target. Evaluation policy decides whether they compete, compose, defer, or all reject.

## 10. Initial operator vocabulary

The v0 vocabulary includes:

- `gradient`
- `hebbian`
- `anti_hebbian`
- `bayesian_update`
- `prototype_update`
- `centroid_update`
- `nearest_neighbor`
- `rule_induction`
- `threshold_adaptation`
- `state_transition_update`
- `graph_edge_update`
- `graph_pruning`
- `reinforcement`
- `memorization`
- `forgetting`
- `temporal_decay`
- `replay`
- `distillation`
- `compression`
- `node_split`
- `node_merge`
- `route_update`
- `no_learning`

This is an extensible registry, not a closed enum for all future MNCS learning.

## 11. Plasticity

Plasticity SHOULD be treated as governed learnable state rather than a single immutable hyperparameter.

A capability MAY expose:

- current plasticity,
- minimum and maximum bounds,
- novelty sensitivity,
- contradiction sensitivity,
- stability/maturity,
- decay rate,
- consolidation policy.

Plasticity changes that themselves alter future learning behavior SHOULD be evidence-backed and auditable.

## 12. Evaluation and fitness

Fitness MAY contain dimensions such as:

- predictive error/accuracy,
- precision/recall,
- retrieval correctness,
- relational consistency,
- calibration,
- compression ratio,
- reconstruction quality,
- task success,
- downstream utility,
- stability/forgetting cost,
- latency,
- memory use,
- energy/compute cost.

Hard constraints MAY reject a proposal regardless of improvements in other dimensions.

Scalarization is an operator/model policy, not a common-contract requirement.

## 13. Timescales

### Fast

Designed for low-latency adaptation to new evidence. Examples: online statistics, local edge reinforcement, episodic capture, prototype movement, temporary route changes.

### Consolidation

Designed to integrate accumulated evidence and protect stable knowledge. Examples: replay, deduplication, compression, migration from episodic to semantic structures, strengthening/weakening stable relations.

### Evolution

Designed for structural adaptation. Examples: split/merge/create/retire nodes, model-class replacement, topology rewrites, long-term routing policy changes.

## 14. Topology policy

A topology-changing proposal SHOULD include:

- evidence supporting structural inadequacy or redundancy,
- affected neighborhood,
- state migration plan,
- provenance preservation plan,
- rollback/checkpoint strategy when possible,
- expected effect and fitness dimensions,
- compatibility/routing consequences.

A node split SHOULD preserve ancestry to the source node. A merge SHOULD preserve ancestry to all merged sources.

## 15. Consolidation and forgetting

Forgetting is not deletion by accident. It is an explicit learning operation governed by policy.

The system SHOULD distinguish:

- short-term decay,
- confidence decay,
- relation weakening,
- memory compaction,
- model retirement,
- rights-mandated deletion/withdrawal.

Rights-mandated deletion is a governance operation and MUST NOT be modeled merely as ordinary optimization-based forgetting.

## 16. Replay and reproducibility

Because adaptation is proposal-driven, implementations SHOULD support replay at the semantic contract level where practical:

```text
observation/event -> proposal -> evaluation -> decision -> resulting revision
```

Replaying an event does not guarantee byte-identical backend state on nondeterministic hardware, but the evidence trail SHOULD expose enough information to explain divergence.

## 17. Integration contracts

### mncs-ingest -> mncs-learn

Provides typed observations/evidence. `mncs-learn` MUST NOT own raw-source parsing as its primary concern.

### mncs-learn <-> mncs-memory

`mncs-learn` proposes/evaluates state changes; memory owns persistent graph/model state. Exact storage APIs remain to be specified jointly.

### MNEL -> mncs-learn

MNEL may provide concrete operators, model adapters, optimization routines, or training backends. MNEL is one implementation source, not the universal semantic layer.

### mncs-language -> mncs-learn

The language should eventually represent learnable capabilities, events, proposals, evaluation, operators, and policy natively. Missing expressive power is treated as language/stdlib pressure.

### mncs-actions -> mncs-learn

Actions verifies declared invariants and produces evidence/badges. Conformance should eventually include native language checks, schema compatibility, lifecycle tests, and multi-backend pressure.

### mncs-fabric -> mncs-learn

Fabric schedules execution/placement. The same proposal/evaluation/commit semantics should hold whether an operator executes locally, on another CPU architecture, GPU/PTX, WASM sandbox, or another worker class.

## 18. Bootstrap representation

The repository initially carries:

- a transport-neutral JSON Schema vocabulary,
- a small Python reference lifecycle,
- executable contract tests,
- examples.

These artifacts are deliberately bootstrap mechanisms. They MUST NOT become justification for making Python the normative MNCS learning runtime.

The migration target is native MNCS-language representation when the language supports the required semantics cleanly.

## 19. Non-goals for v0

This RFC does not specify:

- a universal optimizer,
- a tensor runtime,
- a universal scalar objective,
- a complete distributed scheduler,
- one graph storage engine,
- one neural architecture,
- autonomous topology evolution policy suitable for production,
- a final wire protocol version.

It defines the semantic boundary those systems must respect.

## 20. Design test

A proposed feature belongs in the common learning layer only if it still makes sense for at least several fundamentally different micro-model classes.

If a concept only makes sense for a neural tensor model, Bayesian estimator, graph learner, or symbolic learner, it belongs in that operator/backend's capability payload rather than the universal contract.
