"""D3: parallel crosstalk at the written case's full replica density, from the raw shot lists of both runs.

Falsifier, fixed before the numbers: crosstalk between active neighbors exists if the 90 percent Newcombe-Wilson
interval of packed minus isolated replica-0 score of the null block k0 minus arm lies below -0.015 (its upper end under
-0.015, which excludes zero); the interval inside +-0.015 shows none at this resolution. The score is the share of shots
on the ideal support of the arm, packed replica 0 against live_run's isolated reference (the same circuit alone on
replica 0). The computation repeats live_run's collector interval from the raw counts of PUB 0 and PUB 1.
"""

import json
import math

from d_data import run_dir
from pathion_parallel_coset_analysis import counts_to_law
from scipy import stats

import pathion_parallel_coset as ppc
import variance

BAND = 0.015
MEMBER = "cmap_e1pe17_k0_minus"
ISOLATED = "cmap_e1pe17_k0_minus_isolated"
# Retained 8192-shot runs of the coset map (CASE.md, "Parallel crosstalk").
EARLIER = {"ibm_fez": (0.0011, -0.0067, 0.0089), "ibm_marrakesh": (0.0059, -0.0028, 0.0145)}

ideal = next(m.ideal for m in ppc.pathion_parallel_coset_group().members if m.name == MEMBER)
print(f"falsifier: the 90 percent interval of packed minus isolated k0 minus score has its upper end below -{BAND}")
rows = {}
for backend in ("ibm_fez", "ibm_kingston"):
    directory = run_dir(backend)
    record = json.loads((directory / "record.json").read_bytes())
    raw = next((directory / "raw").iterdir())
    index = {c["member"]: i for i, p in enumerate(record["execution_pubs"]) for c in p["components"]}
    laws = {}
    for member in (MEMBER, ISOLATED):
        pub = json.loads((raw / f"pub_{index[member]:02d}.json").read_bytes())
        reg = pub["registers"]["g0_r0_c"]
        laws[member] = (counts_to_law(reg["bitstrings"], reg["num_bits"]), len(reg["bitstrings"]))
    (packed_law, shots), (iso_law, iso_shots) = laws[MEMBER], laws[ISOLATED]
    if shots != iso_shots:
        raise ValueError(f"{backend}: packed {shots} and isolated {iso_shots} shots differ")
    packed, packed_var = variance.score(packed_law, ideal)
    iso, iso_var = variance.score(iso_law, ideal)
    low90, high90 = variance.difference_interval(packed, packed_var, iso, iso_var, shots, True, 0.90)
    low95, high95 = variance.difference_interval(packed, packed_var, iso, iso_var, shots, True, 0.95)
    diff = packed - iso
    se = math.sqrt((packed * (1 - packed) + iso * (1 - iso)) / shots)
    rows[backend] = (diff, se)
    verdict = (
        "crosstalk" if high90 < -BAND else ("inside the band" if -BAND <= low90 and high90 <= BAND else "unresolved")
    )
    print(
        f"{backend:13s} shots {shots}  packed {packed:.4f}  isolated {iso:.4f}  difference {diff:+.4f}  "
        f"90 percent [{low90:+.4f}, {high90:+.4f}] (half-width {(high90 - low90) / 2:.4f})  95 percent [{low95:+.4f}, {high95:+.4f}]  "
        f"z {diff / se:+.2f}  {verdict}"
    )
weight = {b: 1.0 / se**2 for b, (_, se) in rows.items()}
mean = sum(weight[b] * rows[b][0] for b in rows) / sum(weight.values())
se_mean = math.sqrt(1.0 / sum(weight.values()))
print(
    f"inverse-variance mean of the two devices {mean:+.4f} +- {se_mean:.4f}: 90 percent interval "
    f"[{mean - stats.norm.ppf(0.95) * se_mean:+.4f}, {mean + stats.norm.ppf(0.95) * se_mean:+.4f}] (normal approximation)"
)
print("earlier 8192-shot reference runs (90 percent Newcombe-Wilson):")
for name, (difference, low, high) in EARLIER.items():
    print(f"  {name:13s} {difference:+.4f} [{low:+.4f}, {high:+.4f}] (half-width {(high - low) / 2:.4f})")
print("written case's prediction of the 90 percent half-width: 0.008 at 8192 shots and about 0.006 at 14336 shots")
