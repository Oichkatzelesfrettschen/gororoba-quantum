# Four-support real-rank replay

The replay derives exact polynomial certificates for every real coefficient
on the fixed dimension-32 support `{1,10,18,25}`. The
[derivation](../../notes/four_support_rank_loci.md) states the complete
restricted rank classification, kernel frames, source attribution, and
remaining geometric obligations.

Run from the repository root with the pinned project Python dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/four_support_rank/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/four_support_rank/replay.py --check
(cd docs/evidence/four_support_rank && sha256sum -c SHA256SUMS)
```

The replay writes stdout only and checks source bytes before and after the
calculation. `result.json` retains the interpreter and SymPy versions,
eight sector identities, positive rank witnesses,
complete rational kernel comparisons, pivot transitions, path specialization,
spectral coefficient specialization, and negative controls. The normal and
optimized replays must match the retained JSON exactly. A changed source or
runtime requires an explicit reviewed regeneration of the evidence.

`GOROROBA_WORKERS=1` runs serially. Parallel work uses the repository's
order-preserving spawned pool and produces the same JSON. The computation
uses exact rational and symbolic arithmetic. It invokes neither Qiskit
simulation nor IBM hardware. The certificate covers the fixed support;
global rank-locus geometry, attachments, and topology remain separate work.
