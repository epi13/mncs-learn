# AGENTS.md

## Mission

`mncs-learn` defines the machine-native learning plane for the MNCS ecosystem. Contributions must preserve the core invariant:

> Learning is evidence-governed state transition across heterogeneous computational state.

This repository must not quietly collapse that definition back into "training means gradient descent."

## Required architectural invariants

1. **No universal `train()` assumption.** A learnable advertises capabilities, accepted evidence, operators, plasticity, evaluation dimensions, and timescales. Different model classes may have unrelated state representations.
2. **No direct durable mutation from observations.** Persistent change flows through proposal -> evaluation -> decision -> commit.
3. **Mutation scope is explicit.** Distinguish internal state, relationship/edge state, topology, and routing.
4. **Gradient descent is an operator, not the ontology.** Do not encode tensor-, loss-, epoch-, batch-, or optimizer-specific concepts into the common contract unless they are optional operator-specific payloads.
5. **Provenance and rights travel with evidence.** A learner must be able to refuse learning even when it can read or reason over an observation.
6. **Evaluation may be multidimensional.** Do not force every learner into a scalar loss.
7. **Plasticity is model state/policy.** It may vary with maturity, novelty, contradiction, stability, or explicit governance.
8. **Topology may learn.** Node creation, split, merge, retirement, relationship changes, and routing changes are learning operations when evidence drives them.
9. **Timescales remain distinguishable.** Fast adaptation, consolidation, and evolution may be scheduled differently even when a backend combines them.
10. **`no_learning` is valid.** Observation, reasoning, memory retention, and generalization are separate permissions/effects.

## MNCS-language pressure

The desired end state is native MNCS-language expression of the contracts and critical runtime logic. Until the language can represent a concept correctly:

- use transport-neutral schemas and small bootstrap reference implementations;
- mark them as bootstrap/non-normative implementation artifacts;
- record language/stdlib pressure in `ROADMAP.md` or an RFC;
- do **not** invent attractive but unsupported `.mncs` syntax and present it as working code;
- prefer pushing missing primitives into `mncs-language` rather than permanently growing a host-language shadow runtime.

## Integration ownership

Keep boundaries sharp:

- `mncs-ingest` owns conversion of external/raw data into typed observations/evidence.
- `mncs-learn` owns eligibility, operator selection, adaptation proposals, evaluation, commit policy, consolidation, and structural learning semantics.
- `mncs-memory` owns persistent memory/model graph state and retrieval semantics.
- MNEL may implement learning mechanisms/operators but does not define the universal learning contract.
- `mncs-actions` owns conformance/evidence aggregation and should prove this repo's declared boundary.
- `mncs-fabric` may execute/schedule work across machines but should not redefine learning semantics.

## Change discipline

For changes to contracts or operator semantics:

1. update the relevant RFC/spec first or in the same change;
2. update examples;
3. add/adjust executable invariants;
4. describe compatibility impact;
5. do not broaden a field just to make a test pass without documenting the semantic reason.

For a new operator, document at minimum:

- operator name,
- mutation scope(s),
- typical timescale,
- expected capability declaration,
- proposal shape or operator-specific payload,
- evaluation requirements,
- failure/rollback expectations,
- whether the operation is reversible.

For topology-changing operators, require stronger preconditions and evaluation than ordinary local state updates.

## Testing

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/mncs_learn_check.py --result-file /tmp/mncs-learn-check.json --revision working-tree
```

The second command emits `mncs.check-result/1` evidence consumed by `mncs-actions`.

## Bootstrap code rule

`src/mncs_learn/reference.py` is deliberately small. It exists to prove lifecycle semantics, not to become a general Python ML framework. If feature work starts turning it into the real product, stop and reassess whether the capability belongs in MNCS-language, MNEL, memory, ingest, or another family repo.
