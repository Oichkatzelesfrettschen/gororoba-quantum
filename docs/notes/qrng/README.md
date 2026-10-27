# QRNG seed sources

Every new random seed in the repository comes from a quantum random number
generator (AGENTS.md, Seeds). Each source has an adapter under `scripts/`
that retains one request's raw response bytes, their sha256 and the parsed
values as `docs/evidence/<source>/draw-<UTC>.json`, and an offline `check`
that re-derives the values from the raw bytes. `ci/seed_provenance.py`
registers each evidence directory with its adapter's `admit` (SOURCES), so a
seed allocation in `docs/evidence/qrng_seeds/allocations.json` may name a draw
of any registered source.

## Sources and fallback order

A case takes its values from the first source in this order that still has
quota; the draw record names its source, so mixing sources across cases needs
no further bookkeeping.

| order | source | adapter and evidence | physical source | quota | credential | approval |
|---|---|---|---|---|---|---|
| 1 | ANU Quantum Numbers (aqn, keyed) | `scripts/anu_qrng.py draw` (default), `docs/evidence/anu_qrng/` | vacuum-fluctuation homodyne (ANU) | 100 requests a calendar month, 1 a second; up to 1024 uint16 values a request | `~/.config/anu-qrng/api-key` (mode 600) or `ANU_QRNG_KEY_FILE` | none |
| 2 | ANU legacy (keyless) | `scripts/anu_qrng.py draw --source legacy`, same directory | same generator | 1 request a minute; ANU will scale it back and retire it | none | none |
| 3 | Cisco Outshift QRNG | `scripts/outshift_qrng.py draw`, `docs/evidence/outshift_qrng/` | Outshift's quantum generator, offered as-is | 100000 bits a month; 1 to 10000 bits a block, 1 to 1000 blocks a request | `~/.config/outshift-qrng/api-key` (mode 600) or `OUTSHIFT_QRNG_KEY_FILE` | none |
| 4 | Quandela Cloud QRNG | `scripts/quandela_qrng.py draw --approved-case FILE`, `docs/evidence/quandela_qrng/` | photonic entanglement; every generating job reports its CHSH value and min-entropy | priced per byte through the account's offer, charged in entity credits | the job token file `QUANDELA_TOKEN_FILE` names | an approved written case per draw (AGENTS.md, Hardware services) |

The ANU draw and the Outshift draw are free and need no approval. The Outshift
default request is 256 blocks of 16 bits (4096 of the monthly bits), matching
the uint16 values of the ANU draws; `--bits` and `--blocks` change it within
the service's limits. A Quandela draw is a provider QRNG read: the adapter
refuses before any request unless `--approved-case` names the case file, and
the record binds that file's path and sha256. Its `check` admits a job only
when its CHSH value exceeds the local bound 2 and stays at most 2 sqrt 2, and
its min-entropy lies in (0, 1]. The QRNG `count` parameter is described as
random bytes in `docs/notes/quandela/api/cloud-qt-openapi.json`; the first
approved draw settles whether it counts bytes or integers, so the case states
the count it requests.

## Keys

Each key lives in a mode-600 file outside every checkout; an adapter refuses
a key file that group or others can read, and no record, URL or log carries a
key. To install or rotate a key without echoing it, write it from the
clipboard: `sh -c 'umask 077; mkdir -p ~/.config/outshift-qrng; wl-paste -n >
~/.config/outshift-qrng/api-key'`. A key that appeared in a chat, a terminal
log or a commit is revoked at its service and replaced.

## Candidates outside the table

- QCi uQRNG (Quantum Computing Inc., photon time-mode superposition; free, up
  to 1 Gbit a month): access requested, token pending. It joins the table
  with its own adapter once the token arrives.
- Sequre SeQRNG on AWS Marketplace resells the ANU generator: it adds quota
  but no independent source.
- AUR `r-qrng` generates quasi-random (low-discrepancy) sequences, and
  `rng-tools`, `haveged` and `/dev/hwrng` draw classical entropy; none is a
  quantum source.

## Seeds given at run time

A CLI seed flag is declared through `qrng_seeds.add_seed_argument`
(`gororoba_quantum/qrng_seeds.py`) and takes one of three spellings per value:

| spelling | meaning | record |
|---|---|---|
| `qrng:docs/evidence/<source>/draw-<UTC>.json#<index>` | a new seed: one value of a retained draw, admitted by its source's adapter | `seed_source` names the reference, the script, the flag and the experiment |
| the flag's default | the integer the code already holds, a reproduction seed of `ci/reproduction_seeds.json` | the record is unchanged, so retained outputs replay byte for byte |
| `repro:<integer>` | an explicit reproduction of an earlier run whose seed the code does not hold | `seed_source` marks the value for review |

Any other integer is refused when the arguments are parsed. The experiment a
record names stays the same across the dry run, the submission and the
collection of one experiment, so they share their QRNG values; a second
experiment needs another index. The ledger row that consumes a value lands in
the change that retains the run: `"$PYTHON" ci/seed_provenance.py --add-runtime`
appends a row to the `runtime` list of
`docs/evidence/qrng_seeds/allocations.json` for every retained reference that
lacks one, and `--runtime` (run by the `tests` check) requires every qrng
reference under `results/` to be declared by some `seed_source` entry there
(a replay command, a copy or a `scripts/kaggle_run.py` submission manifest may
repeat it), to have one experiment, and to match exactly one row. A
calibration-adaptive envelope re-plans each submission on the calibration in
force, so a submission that sent nothing usable and its resubmission carry
different approved dry runs for one question; the row then lists the later dry
runs under `resubmissions` and names the approving document under `envelope`,
and the check admits exactly those experiments for the value. A
qrng-seeded Kaggle run therefore retains its collected output, which carries
the `seed_source`, in the same change as its submission manifest. A reference with an index consumes
that index only; a case manifest that names a draw without an index owns the
whole draw.

## Checks

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/anu_qrng.py check docs/evidence/anu_qrng
"$PYTHON" scripts/outshift_qrng.py check docs/evidence/outshift_qrng
"$PYTHON" ci/seed_provenance.py --check
"$PYTHON" ci/seed_provenance.py --runtime
```

`tests/scripts/test_qrng_adapters.py` runs every adapter's self-test and
`check` in the pull-request `tests` job.
