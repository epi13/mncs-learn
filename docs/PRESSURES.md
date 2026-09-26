# Pressure ledger (learn workload)

Genuine gaps found while building the first canonical native
implementation. `mncs-language` and `mncs-compiler` are read-only;
active-campaign repositories were inspected, never modified.

## LEARN-P1: no float numbers in the Data cell model (non-blocking)

`mncs-data` Cells are Int/Text/Bool/Missing/Invalid by design; float
ordering and NaN semantics are an explicit non-goal there. Learn
therefore represents confidence in per-mille integers and centroids in
truncating integer division, documented and parity-tested. If statistical
learners need real-valued state, the pressure belongs to a
Numeric-coherent float design, not to Learn-private floats.

## LEARN-P2: fixed bounds force chunking (non-blocking)

The native centroid holds at most 4 classes × 4 dims; Tables hold 16
rows × 4 columns. Larger datasets chunk into successive tables and
incremental updates thread state across them (tested: incremental ≡
batch). Bounded-memory streaming over datasets larger than one Table is
an explicit Data pressure, not silent behavior. If Learn outgrows these
windows, the bounds move in Data/collections, not in Learn-private
tensor code.

## LEARN-P3: language ergonomics found while writing native Learn

All worked around without touching Language/Compiler; recorded so the
workarounds do not look like style:

- Array/record indexing requires a plain binding: `sums[slot]` after
  `let sums = state.sums` works, `state.sums[slot]` does not parse.
- Accumulators must thread explicitly: an `iterate` helper that reads
  the original collection instead of the carried accumulator silently
  drops all but the last update (caught by the known-answer suite).
- `let` bindings are single-assignment; multi-step flag logic uses
  `select` expressions instead.
- Checked-op consumption is continuation-passing (`let t = ...` then
  `match` into a helper); match arms stay single expressions.
- `next` and `over` are reserved words (binding names to avoid).
- `u64`/`i64` never coerce: boundary casts are explicit (`as`).

## LEARN-P4: small-state Store surface (non-blocking)

`mncs-store` is a content-addressed object/generation system — the
right long-term home for artifact persistence, but heavier than what a
16-row learner needs today. Learn persists atomic JSON artifacts (same
precedent as Automation) carrying dataset digests, revisions, and
metrics, so migration to Store generations later is a change of
durability, not of semantics. The staged compare-and-commit memory
handshake (ROADMAP Phase 2) remains future scope.

## LEARN-P5: per-call compile cost (non-blocking)

Every native evaluation spawns `mncs call` (~30s cold, ~4s warm with a
shared content-keyed cache). Training calls are infrequent by
construction (one call per table, not per row), so the cost is
acceptable; a fleet of per-observation updates would want a retained
session or batch entry. Same precedent as Automation (AUTO-P5).

## LEARN-P6: capability negotiation is single-operator (non-blocking)

v1 capabilities accept exactly one observation kind and one operator.
Set negotiation, operator composition/competing proposals, and learned
operator selection (ROADMAP Phases 4/9/10) are explicitly future scope.

## LEARN-P7: no Learn-private streaming (by design, non-blocking)

Online learning exposes `state + observation -> state` (native
`train_row`); supplying observations stays with whoever owns the
stream. No Learn-private queue, scheduler, or background loop was
built; Automation remains the scheduling owner.

## Closed during this campaign

- Typed `mncs call` wire shapes for records, nested records, fixed
  arrays, enum payloads (`payload` key), and `byte`/`float` tags:
  probed and documented in code.
- `mncs-data` Table/Schema4/Cell as the dataset representation with
  Missing-never-zero skip semantics.
- `mncs-math` checked arithmetic (`checked_add/sub/mul`) as the
  overflow discipline: structured reasons, no traps, no NaNs.
- Truncating integer division semantics (-13/2 = -6), matched by the
  Python parity rule.
- Zero-initialized class slots vs label 0: `find_class` searches only
  live slots (caught by the known-answer suite, regression-covered).
