# Architecture

`mncs-learn` is a protocol and orchestration layer for heterogeneous learning. It defines how evidence becomes a governed state transition without requiring every learner to share an implementation model.

## 1. Component model

```text
                          +--------------------+
                          |   mncs-ingest      |
                          | typed observations |
                          +---------+----------+
                                    |
                                    v
+------------------+      +---------+----------+      +------------------+
| rights/provenance|----->| learning event     |<-----| context / policy |
+------------------+      +---------+----------+      +------------------+
                                    |
                                    v
                          +---------+----------+
                          | eligibility/router |
                          +---------+----------+
                                    |
                         candidate learnables
                                    |
                                    v
                          +---------+----------+
                          | operator selection |
                          +---------+----------+
                                    |
                                    v
                          +---------+----------+
                          | adaptation proposal|
                          +---------+----------+
                                    |
                                    v
                          +---------+----------+
                          | evaluation/fitness |
                          +----+----------+----+
                               |          |
                         reject/defer   commit
                                          |
                                          v
                                  +-------+-------+
                                  | mncs-memory   |
                                  | graph / state |
                                  +-------+-------+
                                          |
                                resulting revision
                                          |
                                          v
                                  evidence / replay
```

The learning plane does not require one physical process. Eligibility may run on one host, proposal generation on an accelerator, evaluation in a sandbox, and commit against persistent graph state. The semantic transitions remain stable.

## 2. Four mutation scopes

### Internal

State owned by a target model changes while model identity and graph placement remain stable.

Examples: weights, posterior parameters, prototypes, rule confidence, state-transition probabilities, local memories.

### Relationship

An edge or relation changes without requiring either endpoint to change internally.

Examples: affinity, causal confidence, inhibitory/excitatory weight, relation kind, eligibility, decay.

### Topology

The population or structure of models changes.

Examples: split, merge, create, retire, replace model class, move membership between clusters.

### Routing

Activation policy changes.

Examples: which data types reach a model, route priorities, neighborhood fan-out, suppression, learned dispatch based on downstream utility.

A proposal may touch more than one scope, but broad proposals should be rarer and receive stronger evaluation.

## 3. The control plane and the learning plane

Two related ideas should remain distinguishable.

The **learning plane** handles evidence-driven adaptation: event eligibility, operator selection, proposals, fitness, decisions, commits, consolidation, and evolution.

The **control plane** handles execution concerns: worker placement, quotas, accelerator availability, checkpoint transport, sandboxing, policy distribution, and scheduling. `mncs-fabric` is a natural control-plane participant.

This separation keeps "where/how the work runs" from becoming "what learning means."

## 4. Capability-directed dispatch

Every learnable exposes a capability descriptor rather than a universal training function.

Conceptually:

```text
learnable capability
  model_class
  accepts[]
  operators[]
  mutation_scopes[]
  timescales[]
  evaluation_dimensions[]
  plasticity
  constraints
```

The dispatcher intersects the event with the capability and policy:

```text
eligible =
    observation type matches
    AND desired effect is supported
    AND rights permit learning
    AND at least one operator is viable
    AND model/policy constraints are satisfied
```

The exact eligibility function may itself become learnable through routing adaptation, but hard rights/policy constraints remain authoritative.

## 5. Operator-directed adaptation

Operators turn eligible events into proposals. An operator is not assumed to own persistence.

```text
event + target snapshot + operator context
                  |
                  v
           adaptation proposal
```

Operator-specific payload is allowed. For example, a gradient operator may include optimizer state or batch metadata while a node split operator may include child initialization and state migration plans. Those fields remain operator-specific rather than contaminating the common contract.

## 6. Evaluation-directed commit

Evaluation compares a proposal with declared dimensions and constraints. The common result is one of:

- `commit`
- `reject`
- `defer`

A scalar objective is permitted but not required. A topology change may require a different evaluation strategy than a local prototype update.

Commit should bind:

- proposal identity,
- target revision before change,
- decision/evaluation evidence,
- resulting target/graph revision,
- ancestry/provenance.

That binding is essential for replay, audit, debugging, rollback, and eventually machine-native self-explanation.

## 7. Learning timescales

### Fast adaptation

Runs near the observation path and is biased toward local, reversible, low-blast-radius changes.

### Consolidation

Runs over accumulated evidence and checkpoints. It may replay, compress, distill, strengthen, weaken, migrate, or reconcile state.

### Evolution

Changes structural assumptions. It may alter topology, model class, or routing architecture. It should be conservative, evidence-rich, and checkpoint-aware.

These are semantic timescales, not fixed wall-clock intervals.

## 8. Plasticity

Plasticity controls how willing a learnable is to change. It is not merely a learning rate.

Useful dimensions include:

```text
current
minimum
maximum
novelty_response
contradiction_response
maturity
stability
consolidation_decay
```

A model may become less plastic as stable evidence accumulates, then temporarily become more plastic when contradiction or distribution shift is detected. Plasticity itself may be adapted through governed proposals.

## 9. Structural adaptation

### Split

A split is appropriate when one model persistently carries separable modes that damage discrimination, consistency, or utility.

A split proposal should describe:

- triggering evidence,
- source node/revision,
- child identities/classes,
- state partition/migration,
- edge/routing redistribution,
- ancestry preservation,
- evaluation plan,
- rollback/checkpoint plan.

### Merge

A merge is appropriate when multiple models are redundant or converge strongly enough that separate state creates needless cost or inconsistency.

A merge proposal should preserve ancestry to all sources and explicitly reconcile conflicting state.

### Retirement

Retirement is not arbitrary garbage collection. It should distinguish low utility, obsolescence, consolidation, policy removal, and rights-mandated deletion.

## 10. Memory relationship

`mncs-memory` and `mncs-learn` are tightly coupled but should not collapse into one subsystem.

Memory answers:

- what persistent state exists,
- what relationships exist,
- how state is retrieved,
- what revision/checkpoint is current.

Learn answers:

- whether evidence is eligible to cause change,
- which change is proposed,
- how it is evaluated,
- whether it commits,
- whether consolidation or evolution is warranted.

A micro-model can therefore be both computation and memory without confusing storage ownership with adaptation semantics.

## 11. Failure model

The proposal boundary creates natural failure containment.

- If operator execution fails before proposal creation, no durable state changes.
- If evaluation fails, the proposal can defer or reject.
- If commit fails, persistence should remain on the previous revision or use store-specific atomicity/rollback.
- If a distributed worker disappears, the proposal can be retried from evidence/checkpoint if the operator permits it.
- If evidence rights are revoked before commit, policy can reject the outstanding proposal.

Topology-changing operations may require multi-object transactional support from memory or staged graph revisions.

## 12. Bootstrap vs native end state

The Python reference implementation and JSON Schema in this repo are scaffolding. They prove semantic invariants while the language/runtime catches up.

The intended pressure path is:

```text
bootstrap schema/reference
        |
        v
mncs-language types + stdlib primitives
        |
        v
native WASM/runtime execution where appropriate
        |
        v
heterogeneous operator backends via stable contracts
```

The architecture should resist a permanent host-language control layer when MNCS-language can own the logic directly.
