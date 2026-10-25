# Quantum recovery proposal replay

`replay.py` recomputes the computational claims of the nonlocal-transport and
quantum-recovery proposal, and `result.json` holds its output.
[The audit report](../../archive/reviews/quantum-recovery-proposal-audit.md) reads the result.
The replay covers the [[5,1,3]] erasure and region checks, the M/G/1 optimum, the pinching
closed forms, the sedenion zero divisor and the H3 Jordan witness, all computed through
`gororoba_quantum/cd_core.py`, plus the Landau refit of every sweep in the Zenodo Pockels file.
It uses no random draws.

The Pockels file stays external: Zenodo record 15653571 publishes it under CC-BY-4.0, and the
replay refuses any copy whose MD5 differs from the record's checksum.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
curl -sSL -o Fig4a_pockels.csv 'https://zenodo.org/records/15653571/files/Fig4a_pockels.csv?download=1'
"$PYTHON" -I docs/evidence/quantum-recovery-proposal-audit/replay.py . Fig4a_pockels.csv \
  > docs/evidence/quantum-recovery-proposal-audit/result.json
```

The run takes about 90 s on the build host, almost all of it in the exact H3 searches. Least
squares makes the fitted parameters platform-dependent in their last digits, so the replay is
not bit-reproducible across hosts.
