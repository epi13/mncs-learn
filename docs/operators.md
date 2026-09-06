# Learning Operator Catalog

Operators are mechanisms for proposing state transitions. They are not the definition of learning itself.

The catalog below is the initial shared vocabulary. Backends may add operator-specific payloads and constraints. New operators should be added only when they represent a distinct adaptation mechanism, not merely a parameterization of an existing one.

| Operator | Typical scope | Typical timescale | Purpose |
|---|---|---|---|
| `gradient` | internal | fast/consolidation | Optimize differentiable parameters against an objective. |
| `hebbian` | internal/relationship | fast | Strengthen co-activated representations or relations. |
| `anti_hebbian` | internal/relationship | fast | Decorrelate, inhibit, or weaken co-activation patterns. |
| `bayesian_update` | internal | fast | Update beliefs/posteriors from evidence. |
| `prototype_update` | internal | fast | Move/add semantic or feature prototypes. |
| `centroid_update` | internal | fast | Update cluster centroids or representative state. |
| `nearest_neighbor` | internal | fast | Add/update instance-based reference state. |
| `rule_induction` | internal | consolidation | Derive or revise symbolic/rule structure. |
| `threshold_adaptation` | internal/routing | fast | Adjust decision, activation, or gating thresholds. |
| `state_transition_update` | internal | fast | Revise state-machine transition probabilities/rules. |
| `graph_edge_update` | relationship | fast/consolidation | Create, strengthen, weaken, retype, or redirect a relation. |
| `graph_pruning` | relationship/topology | consolidation | Remove low-value or invalid graph structure under policy. |
| `reinforcement` | internal/routing/relationship | fast/consolidation | Adapt from reward/utility signals. |
| `memorization` | internal | fast | Preserve evidence/state without implying generalization. |
| `forgetting` | internal/relationship/topology | consolidation | Explicitly weaken/remove learned state under policy. |
| `temporal_decay` | internal/relationship/routing | consolidation | Reduce influence as a function of time or non-use. |
| `replay` | internal/relationship | consolidation | Re-present prior evidence to stabilize or integrate learning. |
| `distillation` | internal/topology | consolidation | Transfer behavior/knowledge into a smaller or different representation. |
| `compression` | internal/topology | consolidation | Reduce representation cost while preserving declared utility. |
| `node_split` | topology/routing/relationship | evolution | Specialize one overloaded/multimodal node into descendants. |
| `node_merge` | topology/routing/relationship | evolution | Reconcile redundant/converged nodes into one descendant. |
| `route_update` | routing | fast/consolidation/evolution | Adapt dispatch and activation policy. |
| `no_learning` | none | any | Intentionally make no durable adaptation from an event. |

## Operator contract

An operator implementation should be able to answer:

```text
supports(event, capability, policy) -> bool/reason
propose(event, target_snapshot, context) -> proposal(s)
```

Evaluation and commit remain separable. An operator should not silently write durable target state while constructing a proposal.

## Operator-specific state

The common contract permits operator-specific payload. Examples:

### Gradient

May carry:

- objective identifier,
- gradient summary/digest,
- optimizer/backend identity,
- batch/evidence-set identity,
- checkpoint base,
- parameter delta or opaque backend patch.

The common layer does not require these fields for non-gradient operators.

### Bayesian update

May carry:

- prior revision,
- likelihood/evidence model,
- posterior sufficient statistics,
- calibration metrics.

### Graph edge update

May carry:

- edge identity or create intent,
- relation kind,
- old/new strength,
- old/new confidence,
- directionality,
- decay policy,
- causal/associative semantics.

### Node split

May carry:

- source node revision,
- split rationale,
- proposed descendants,
- state partition/migration plan,
- edge redistribution plan,
- routing redistribution plan,
- ancestry map,
- rollback/checkpoint identifier.

## Composition

Multiple operators may be eligible for one event and target. The runtime may:

- compare competing proposals,
- compose compatible proposals,
- defer until more evidence exists,
- schedule different operators at different timescales.

Composition must not bypass evaluation. A composed change is itself a proposal or an explicitly bound proposal set.

## `no_learning`

`no_learning` is semantically important. It may be selected because:

- rights allow inspection but not training/generalization,
- evidence is too weak,
- evidence is redundant,
- the target is sufficiently stable,
- contradictory evidence needs more corroboration,
- the event belongs only in episodic memory,
- changing the model would decrease expected fitness,
- policy explicitly freezes the target.

It should be possible to record why no learning occurred without creating a meaningless state mutation.

## Adding operators

A proposed new operator should document:

1. the unique mechanism it introduces;
2. applicable mutation scopes;
3. typical timescale(s);
4. capability requirements;
5. proposal payload requirements;
6. evaluation dimensions/constraints;
7. rollback/reversibility characteristics;
8. provenance implications;
9. whether an existing operator can represent the same semantics with parameters instead.
