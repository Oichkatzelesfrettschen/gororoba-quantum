# W8 -> N- degree 6 at N = 19, p = 32009: export probe on the laptop

The probe sizes the W8 degree-6 rank run before any cloud host is booked. Engine v11 (`fiber_rank_v11.py`, quotient
mode, the degree-2 receipt `6e464db6...` of `working/distribute/out/a5-w8-receipt-p1`, header `w8-nm.sing` sha256
`585a946d...`) ran `d = 6, N = 19` with `--max-gb 1` (`run-w8-d6-export.sh`), so it stopped at the preflight gate
after the Singular standard basis. Exit status 1 is that intended stop (`w8d6.events`).

| Quantity | Value | Record |
|---|---|---|
| Singular standard basis of J + m^19 (passagemath Singular 4.4.1, 5 export chunks) | wall 2,773.7 s for the whole probe, peak RSS 486,608 KiB | `w8nm_d6_n19_p32009.time` |
| preflight estimate | 375.62 GiB: echelon bases 221.9e9 B, generator blocks 111.0e9 B, walk temporaries 55.5e9 B, product rows 15.0e9 B | `w8nm_d6_n19_p32009.err` |
| export kept on the laptop | `s.txt`, `qB.txt` (hashes beside), `export.json`; 109 MB; the multiplication tables are built by the full run | `export.json`, `*.sha256`; the producing `std.sing` (sha256 `30ea8a6c2bac31f96ba2c3b95e8ed5df07322d42984d372929ba54a0a1623b6e`) embeds a host path and stays on the laptop |

Reading the preflight. The estimate assumes four dense square echelon bases of side cols_b, held twice, and dense
generator blocks. At degree 5, N = 16 the same terms gave 58.9 GiB against a measured peak of 24.9 GiB
(`../w8-n16-azure/README.md`): the four echelon bases are held at once (`W = {b: Echelon(...) for b in blocks}` in
the engine) but at rank_W x cols with one copy, about 10.6 GiB there (rank_W / cols near 0.66), and the rest of the
peak is the sparse tables and shared state. Every term scales as D^2; D grows from 93,024 to 235,543 (factor 6.41 in
D^2), so the degree-6 peak forecast is about 160 GiB, and about 195 GiB if rank_W fills to cols. hypothesis: the
forecast holds when the closure tables stay sparse (`--dense-tables-gb 0`).
