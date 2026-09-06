# mncs-learn

Machine-native learning orchestration for heterogeneous micro-models, adaptive graphs, and evidence-driven state transitions in the MNCS ecosystem.

> **Core thesis:** training is not parameter optimization. Training is **evidence-governed state transition across a heterogeneous computational graph**.

`mncs-learn` defines how MNCS components are allowed to change because of evidence. It is intentionally broader than gradient descent, backpropagation, epochs, batches, or even neural networks. A micro-model may be a tiny neural network, Bayesian estimator, prototype store, graph neighborhood, state machine, symbolic rule set, memory structure, mathematical function, controller, router, or another machine-native computational form. What they share is not a weight representation; they share a learning protocol.

This repository begins by making that protocol explicit and testable.

## Why this exists

Conventional ML frameworks tend to make the optimizer the center of training:

```text
loss -> backward -> optimizer.step
```

That is a useful implementation for one class of learner, but it is too narrow for the MNCS micro-model architecture. In MNCS, learning may change:

1. **Internal state** — parameters, prototypes, rules, thresholds, statistics, memories, transitions.
2. **Relationships** — edge strength, direction, type, confidence, eligibility, or decay between micro-models.
3. **Topology** — create, split, merge, specialize, retire, or reorganize micro-models.
4. **Routing** — change which observations reach which models and which neighboring models activate.

Gradient descent is therefore one learning operator among many, not the definition of learning.

## System boundary

The intended family-level separation is:

```text
outside world
    |
    v
mncs-ingest
    "What did we observe?"
    |
    v
machine-native observation / evidence
    |
    v
mncs-learn
    "What should change because of it?"
    |
    +--> adaptation proposals
    +--> evaluation / fitness
    +--> commit or reject
    +--> consolidation
    +--> topology / routing evolution
    |
    v
mncs-memory
    "What state and relationships persist?"
```

Other family members participate without collapsing these boundaries:

- **MNEL** supplies one or more learning mechanisms/backends. It does not define learning for every micro-model class.
- **mncs-language** should eventually express the learning contracts and operators natively. This repository does not invent unsupported MNCS syntax to pretend that work is already complete.
- **mncs-actions** proves the repository boundary and machine-verifiable invariants.
- **rights / provenance services** constrain whether evidence may be used, retained, propagated, or transformed.
- **mncs-fabric** may later schedule learning across heterogeneous workers and accelerators without changing the learning contract.

## The learning lifecycle

The native loop is not fundamentally an epoch loop. It is:

```text
OBSERVE
   |
   v
ROUTE
   |
   v
ACTIVATE
   |
   v
COMPARE
   |
   v
PROPOSE
   |
   v
TEST
   |
   v
ADAPT
   |
   v
CONSOLIDATE
```

A live learner may execute this one observation at a time. A GPU-backed neural micro-model may accumulate eligible observations and perform a batch update. A Bayesian node may update immediately. A graph node may reinforce an edge. A symbolic learner may defer until enough consistent evidence exists. The lifecycle stays the same while implementation strategy varies.

## The transactional rule

Observations do **not** mutate persistent model state directly.

```text
evidence
   |
   v
adaptation proposal
   |
   v
evaluation
   |
   +--> REJECT / DEFER
   |
   v
COMMIT
```

Every durable learning change should be attributable to a proposal and a decision. This makes learning inspectable, replayable, auditable, reversible where the underlying model permits it, and compatible with provenance and rights constraints.

The rule applies to all four mutation scopes: internal state, relationships, topology, and routing.

## Core machine-native objects

### Observation

A typed result from ingestion or another trusted producer. It carries payload plus confidence, provenance, rights, time/context, and enough structure for routing.

### Learning event

An observation promoted into the learning plane with desired effects and contextual information. Desired effects may include `remember`, `associate`, `predict`, `discriminate`, `generalize`, `specialize`, or other declared goals.

### Learnable capability

A micro-model advertises what it can consume, which learning operators it supports, how plastic it currently is, what timescales it participates in, and how improvement can be evaluated.

A universal `train()` method is deliberately avoided.

### Adaptation proposal

A candidate state transition. It names the target, operator, mutation scope/timescale, reason, expected effect, preconditions, patch/change description, and evidence ancestry.

### Fitness

Evaluation is multidimensional rather than forced into one scalar loss. A learner may care about prediction error, retrieval quality, relational consistency, compression, task success, stability, resource cost, or other declared dimensions and constraints.

### Evaluation

Compares the relevant before/after state or predicted effect and resolves the proposal to `commit`, `reject`, or `defer`.

## Learning operators

The initial operator vocabulary intentionally spans different learning families:

```text
gradient
hebbian
anti_hebbian
bayesian_update
prototype_update
centroid_update
nearest_neighbor
rule_induction
threshold_adaptation
state_transition_update
graph_edge_update
graph_pruning
reinforcement
memorization
forgetting
temporal_decay
replay
distillation
compression
node_split
node_merge
route_update
no_learning
```

The catalog is a capability vocabulary, not a claim that every operator is implemented here today. Operators are selected according to the target micro-model's declared capability and the learning event. `no_learning` is first class because retaining or reasoning over evidence does not imply permission or need to generalize from it.

See [`docs/operators.md`](docs/operators.md).

## Plasticity is state

Plasticity is not assumed constant. A micro-model can advertise and eventually adapt values such as:

- current plasticity,
- minimum/maximum bounds,
- novelty response,
- contradiction response,
- decay/consolidation behavior.

A young or uncertain model may be highly plastic. Repeated consistent evidence can reduce plasticity. Strong contradiction or distribution shift can raise it within policy bounds. This provides a native place to reason about stability, continual learning, and catastrophic forgetting without pretending one optimizer solves them all.

## Three learning timescales

`mncs-learn` distinguishes three timescales even when an implementation chooses to collapse them:

### Fast adaptation

Immediate or near-immediate updates such as edge reinforcement, short-term state, episodic capture, online statistics, or prototype movement.

### Consolidation

Periodic integration of accumulated evidence: deduplication, replay, distillation, strengthening stable structure, weakening noise, migration from episodic to semantic structures, or controlled compression.

### Evolution

Lower-frequency structural change: split/merge models, change model class, alter routing, retire nodes, create specialists, or reorganize topology.

## Micro-model birth, split, merge, and retirement

Topology is learnable state. A model that is forced to represent two stable modes may be better served by a split than by another parameter update. Two independently created models that converge may be merge candidates. A low-value model may decay or retire under policy.

These are not special cases outside training; they are structural learning operators with stronger evaluation and governance requirements.

## Heterogeneity by design

The same graph may contain:

```text
A -> tiny neural network
B -> Bayesian estimator
C -> finite-state machine
D -> semantic prototype
E -> episodic key/value memory
F -> decision tree
G -> mathematical function
H -> graph neighborhood
```

There is no requirement that these share parameters, tensors, optimizers, or even mathematical learning families. The shared abstraction is an evidence-governed state transition contract.

## Repository map

```text
AGENTS.md                     agent/contributor invariants
README.md                     project orientation
ROADMAP.md                    staged implementation path
mncs-boundary.json            machine-readable repository boundary
rfcs/0001-machine-native-learning.md
                              normative architectural RFC
spec/mncs-learn-v0.schema.json
                              bootstrap contract vocabulary
src/mncs_learn/reference.py   small executable reference protocol
src/mncs_learn/operators.py   operator catalog
examples/fox-learning-cycle.json
                              end-to-end heterogeneous example
docs/architecture.md          component model and mutation scopes
docs/operators.md             operator semantics
docs/integration.md           MNCS family boundaries
tests/                        executable invariants
scripts/mncs_learn_check.py   mncs-actions project evidence producer
.github/workflows/            CI and family conformance
```

## Normative status

The architectural invariant is normative for this repository:

> **Learning is evidence-governed state transition across heterogeneous computational state.**

The JSON schema and Python code are **bootstrap reference artifacts**, not the final MNCS language/runtime representation. Their purpose is to make the design executable and falsifiable while `mncs-language`, its standard library, and the wider family are pressured toward native representations.

When `mncs-language` can express a contract cleanly, this repository should prefer the native form and retain host-language code only where it is genuinely a backend or compatibility layer.

## Current definition of done

The foundation is considered healthy when:

- learning is not defined in terms of gradient descent or a universal `train()` method;
- all durable changes pass through proposal -> evaluation -> decision -> commit;
- internal, relationship, topology, and routing mutation are explicit;
- rights and provenance can prevent or constrain learning;
- heterogeneous micro-model capabilities can coexist;
- fast adaptation, consolidation, and evolution are distinguishable;
- the contract artifacts and examples are machine-checked;
- the repository produces an MNCS conformance result through `mncs-actions`.

## License

Apache-2.0.
