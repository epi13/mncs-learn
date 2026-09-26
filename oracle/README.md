# Oracle (non-canonical reference)

`mncs_learn/` is the historical Python implementation of the v0 learning
protocol: operator vocabulary, eligibility, proposal/evaluation/commit
lifecycle, rights and plasticity gates.

It is **not** a runtime path. Normal Learn functionality runs through
native MNCS (`native/mncs/learn/`) with the thin host bridge
(`tools/learn/`). This package exists solely as an independent oracle
for parity tests (`tests/test_learn.py`: same inputs, same decisions)
and as executable design evidence for the RFC.

Do not import it from production code. Do not extend it with new
learning semantics — those belong in native MNCS.
