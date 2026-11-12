# Cost of the standard basis of J + m^N for E8-bar -> N-, N = 12 to 14

`summary.txt` holds the measured cost of one Singular `std` call on the truncated slice ideal J + m^N of
E8-bar -> N- at p = 32009, the first stage of the Singular export that a quotient-mode truncated rank of this fiber
runs ([A5-246](../ledger.tsv) measures the whole export). The ledger row is A5-321.

| N | quotient length (`vdim`) | standard basis size | wall time | peak resident set |
|---:|---:|---:|---:|---:|
| 12 | 11,595 | 5,125 | 626.88 s | 137,620 KiB |
| 13 | 16,575 | 6,739 | 1,584.28 s | 230,356 KiB |
| 14 | 23,128 | 8,687 | 4,195.30 s | 360,028 KiB |

The time grows by 2.53 from N = 12 to 13 and by 2.65 from N = 13 to 14. The quotient lengths equal `dim_quotient` of
the engine v7 records of the same header at N = 12, 13 and 14
([a5-failed-runs/](../a5-failed-runs/README.md)) and the quotient length of A5-288 at N = 12.

## Producing command

Each run is the header of E8-bar -> N- at p = 32009
(`../working/build/inputs/p32009-r10754/e8-nm.sing`, sha256 `7d3521d0e8026e6f...`) followed by one line:

```
int t0=rtimer; system("--ticks-per-sec",1); option(redSB); ideal s=std(J+maxideal(N)); "N N vdim", vdim(s), "size", size(s), "std_s", rtimer-t0; quit;
```

run as `Singular -q --no-rc nN.sing`; `nN.time` holds the wall seconds and peak resident set of the run. The
ordering is `dp`, so the standard basis is global, and `option(redSB)` returns it reduced. `singular-version.txt`
records the build: Singular 4.4.1 (44105, 64 bit) of 30 June 2026, on a desktop-class host. The record does not state
the load on that host, so the times bound the cost on that build and carry no ratio to another build
([A5-280](../ledger.tsv)). The three generated scripts, each the header plus the line above for its N, are not
retained; the header and the line regenerate them byte for byte.

## Files

| File | Content |
|---|---|
| `summary.txt` | the three result lines (`N`, `vdim`, `size`, `std_s`) and the three wall and memory lines |
| `n12.log`, `n13.log`, `n14.log` | the Singular output of each run, one line |
| `n12.time`, `n13.time`, `n14.time` | wall seconds and peak resident set of each run |
| `singular-version.txt` | the Singular version line |

The `.log` files are hidden by the repository's global ignore pattern and enter with `git add -f`.
