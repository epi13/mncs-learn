# Integration Boundaries

`mncs-learn` is intentionally narrow in ownership even though it sits in the middle of many MNCS systems. The learning plane should coordinate change without absorbing ingestion, storage, execution, or backend-specific training logic.

## mncs-ingest

**Owns:** turning raw/external data into typed machine-native observations.

Expected handoff into learn:

```text
observation {
  identity
  kind / data type
  structured payload or reference
  provenance
  confidence
  rights
  temporal/context information
  relation hints / semantic features where available
}
```

`mncs-learn` should not grow source-specific parsers for PDFs, images, audio, text protocols, sensors, databases, or other external formats. If learning repeatedly needs information that ingest does not expose, that is pressure on the ingest contract.

## mncs-memory

**Owns:** persistent micro-model state, graph state, relationships, retrieval, revisions/checkpoints, and durable memory semantics.

`mncs-learn` needs memory operations conceptually equivalent to:

- read target snapshot/revision,
- read relevant neighborhood,
- stage proposal against a known revision,
- atomically commit or reject stale proposals,
- create graph revisions for topology operations,
- preserve ancestry/provenance,
- checkpoint/rollback where supported.

The exact memory API should be co-designed rather than guessed inside this repository.

## MNEL

**Owns/hosts:** concrete learning mechanisms and model/back-end implementations where MNEL is the appropriate execution layer.

The relationship is intentionally inverted from "MNEL training defines learning":

```text
mncs-learn
  +-- MNEL operator/backend
  +-- gradient backend
  +-- graph learner
  +-- symbolic learner
  +-- statistical learner
  +-- reinforcement learner
  +-- structural learner
```

MNEL may implement several of those branches. The shared contract stays above them.

## mncs-language

**Owns:** native expression, compilation, and runtime semantics for MNCS programs.

Pressure created by `mncs-learn` includes the need to represent:

- tagged contract objects/events,
- capability negotiation,
- immutable proposal values,
- typed heterogeneous payloads,
- policy/effect boundaries,
- graph/node identifiers and revisions,
- multidimensional fitness,
- deterministic evidence serialization/digests,
- async/deferred evaluation,
- transactional commit abstractions,
- pluggable/foreign operator backends,
- WASM-safe execution for policy/routing/evaluation where appropriate.

Until these are cleanly supported, JSON Schema and the Python reference are bootstrap artifacts only.

## mncs-actions

**Owns:** conformance checking, evidence aggregation, reusable CI policy, and visible proof/badges.

The initial `mncs-learn` boundary proves:

- required architecture/spec files exist,
- contract JSON parses,
- the reference lifecycle tests pass,
- the operator catalog contains the declared v0 vocabulary,
- direct learning mutation is not required by the reference protocol,
- rights can suppress learning.

Future conformance should grow toward native MNCS-language execution rather than adding ever more Python-only checks.

## Rights and provenance

Learning permission is distinct from read/use/retain permissions.

A useful conceptual rights surface is:

```text
inspect      may this evidence be read/activated?
reason       may it influence transient inference?
learn        may it alter generalized model state?
retain       may the original/derived evidence persist?
propagate    may derived learning/evidence cross boundaries?
```

The authoritative rights model belongs in the appropriate MNCS rights subsystem; this list documents the distinction `mncs-learn` needs.

Provenance should flow from observation -> event -> proposal -> evaluation -> commit so learned state can retain ancestry to the evidence that produced it.

## mncs-fabric

**Owns:** placement and execution across heterogeneous workers.

Learning operators may eventually execute on:

- local CPU,
- remote CPU workers,
- Windows/Linux hosts,
- ARM/Raspberry Pi,
- RISC-V emulation/hardware,
- GPU/CUDA/PTX,
- eBPF-capable environments where appropriate,
- WASM sandboxes.

Fabric should determine where/how an eligible operator executes. It should not change the semantic contract for proposal, evaluation, or commit.

This is particularly important when a toolchain or backend is unavailable: execution capability should be represented as capability/obligation state rather than silently changing learning semantics.

## mncs-actions + fabric pressure

Eventually a learning backend should be testable against multiple worker classes. The same event/proposal semantics should hold even when operator implementation differs by target. This creates useful pressure on both `mncs-language` portability and `mncs-fabric` capability discovery.

## Suggested contract flow

```text
mncs-ingest
  emits observation
       |
       v
rights/provenance policy
  annotates/authorizes
       |
       v
mncs-learn
  creates learning_event
  negotiates capability
  selects operator
       |
       +------> MNEL / backend via fabric
       |          returns candidate delta/proposal material
       v
mncs-learn
  evaluates proposal
       |
       v
mncs-memory
  commits state/graph revision
       |
       v
mncs-actions / journal / provenance
  can verify and explain what changed
```

The boundary deliberately avoids assuming that every arrow is a synchronous RPC. Events may be streamed, queued, replayed, or evaluated in batches while preserving the same semantics.
