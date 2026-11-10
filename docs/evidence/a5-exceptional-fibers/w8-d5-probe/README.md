# W8 -> N- degree 5 at small N

Engine v11 (`replay/engine/fiber_rank_v11.py`, sha256 prefix 7849cbc71ccf1787) in quotient mode on header
`working/build/inputs/p32009-r10754/w8-nm.sing`, four workers on the workstation, launched by [run.sh](run.sh) to size
the N = 16 cloud run.

| N | r_N | per-block ranks | wall | peak RSS |
|---|---|---|---|---|
| 10 | 0 | 0 / 0 / 0 / 0 | 54 s | 2.4 GB |
| 11 | 1,911 | 486 / 465 / 480 / 480 | 175 s | 5.0 GB |
| 12 | 2,596 | 646 / 640 / 655 / 655 | 707 s | 8.5 GB |

The N = 13 rung left an empty record (`n13.out`; `n13.err` holds only the worker-pool shutdown warning) and is no
measurement. The ladder closes at N = 16 with r_16 = 4,116 = HF(k[y]/K2, 5) ([w8-n16-azure/](../w8-n16-azure/README.md)).
The records sit outside the registry scan roots: below the closing order they bound nothing that A5-008 (proved) does
not already settle.
