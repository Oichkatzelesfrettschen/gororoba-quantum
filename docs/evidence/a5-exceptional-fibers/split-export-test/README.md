# Split quotient export against the serial export, E8-bar -> N- at p = 32009

`split_test.py` falsifies the per-variable split that engine v9 (`../replay/engine/fiber_rank_v9.py`) adopted for the
quotient export of engine v8 (`../replay/engine/fiber_rank_v8.py`). It runs the serial export script of engine v8
(`QUOTIENT_SCRIPT`), which computes `std(J + m^N)` and then every table in one Singular process, and the split: one
Singular process computes `std(J + m^N)` and its `kbase` and writes them, one process per variable reads the basis
back, marks it a standard basis and writes that variable's multiplication table, two more processes write the first
table in two index halves of `kbase`, and one process writes the reduced generators. Every file is compared with the
serial export byte for byte, and any difference falsifies the split. A nonzero exit status of any Singular process
and a nonempty output directory stop the run. The ledger row is A5-322. The [retention audit](../../../archive/reviews/untracked-records-audit-2026-11-11/README.md) lists the comparison as a result-missing record (section 3A, item 2).

The header is E8-bar -> N- at p = 32009 (`../working/build/inputs/p32009-r10754/e8-nm.sing`); the `J` and `G` of the
serial and split scripts equal that header's ideals.

| N | files compared | mismatches | serial export | split `std` | split total | `std` basis size, quotient length |
|---:|---:|---:|---:|---:|---:|---|
| 9 | 11 | none | 37.3 s | 29.1 s | 31.3 s | 1,996, 3,285 |
| 11 | 11 | none | 524.8 s | 407.6 s | 425.3 s | 3,847, 7,887 |

The 11 files are `qB.txt`, `qG.txt` and `qM1.txt` to `qM9.txt`; the two halves of the first table, joined with a
comma, equal `qM1.txt` at both N. The `n9.log` and `n11.log` runs compared the files after newline removal. A
raw-byte comparison (`cmp` and `sha256sum`) of the 22 serial and split files of those two runs, made afterwards on the
retained export directories, finds every pair byte-identical, and the halves joined with a comma are byte-identical to
`qM1.txt`; every one of these files holds a single line with no line break, so the newline removal changed no
comparison. [byte-comparison.tsv](byte-comparison.tsv) holds the size and SHA-256 of each file and of each joined
pair. The split total exceeds its `std` time by 17.7 s at N = 11, against 117.2 s for the
rest of the serial export. The serial export starts first and runs beside the split on one host, so both timings
include that contention; the program measures `serial`, `split std` and `split total` from one start time.
The record does not state the Singular build or the host.

## Producing command

`"$PYTHON" split_test.py HEADER N OUT` from the repository root, with `Singular` on the path; `HEADER` is the header
above and `OUT` a scratch directory that receives `serial/` and `split/`. The log line is the program's one output
(`n9.log` for `N = 9`, `n11.log` for `N = 11`); the program now compares raw bytes. The exported tables (69.4 MB per export at N = 11) are not retained; they
regenerate from the header and the command.

| File | Content |
|---|---|
| `n9.log`, `n11.log` | the comparison line of each run, made with the newline-removing comparison |
| `n7.txt` | the comparison line of a fresh run at `N = 7` with the byte-comparing, return-code-checking program: 11 files, no mismatch |
| `byte-comparison.tsv` | size, SHA-256 and `cmp` verdict of the 22 files of the `N = 9` and `N = 11` runs, and of the joined halves |
| `n9-split-std.txt`, `n11-split-std.txt` | the Singular line of the split `std` process: `RESULT std` size, quotient length, seconds |
| `n9-serial-quotient.txt`, `n11-serial-quotient.txt` | the Singular line of the serial export: `RESULT quotient` size, generators, seconds |
| `split_test.py` | the comparison program; the retained runs used a version that compared after newline removal and ignored child exit statuses. The retained text compares `read_bytes()`, raises on any nonzero child exit status, refuses a nonempty output directory and has the `found` helper, which raises on a missing match so mypy accepts the `re.search` results |

The `.log` files are hidden by the repository's global ignore pattern and enter with `git add -f`. The tracked test
`test_split_export_equals_serial` in `tests/test_a5_fiber_rank_v9.py` checks the same equality on a small instance
where Singular is installed.
