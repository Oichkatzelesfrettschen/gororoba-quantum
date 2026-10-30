# IBM Fez full-register descriptive pilot

The [findings](findings.md) describe the 24 acquired conditions and retain the
limits of the sampling and execution evidence. The acquisition record and raw
shots belong to `results/live/2026-10-29T191606.826758Z`; the collection and
submission digests in [analysis.json](analysis.json) bind the source bytes.
The independently retained submission and collection custody records supply
the expected digests; digest matching alone does not prove physical shot
alignment or independence.

The producer [analyze.py](analyze.py) reads the full 156-bit strings, checks
indexed bytes and the retained pair tables, and derives only small
projections. It uses the repository's ordered process map for PUBs. It records
its own source identities and library versions. Run from the repository root
with the pinned project interpreter:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export OPENBLAS_NUM_THREADS=1
export GOROROBA_WORKERS=2
"$PYTHON" docs/evidence/ibm-fez-actor-pilot/analyze.py --check
```

[report.py](report.py) regenerates the figure from the retained JSON. The
findings are a descriptive report, not a calibrated statistical test or a
provider-independent causal claim.

The documentation type-check gate checks the producer separately because a
different evidence directory also has an `analyze.py` module. Both files remain
in the type-check gate, and the retained producer path and bytes stay fixed.
