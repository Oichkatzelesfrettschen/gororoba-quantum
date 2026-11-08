"""D1: the IBM side of A5-186, the coherent sx over-rotation that the Tuna-17 null block's selector offset implies.

Falsifier, fixed before the numbers: IBM shows the Tuna-17 offset if a backend's k0 selector contrast reads at least
+0.006 (the written case's band) while its 1-CZ null blocks k4, k8, k12 read zero, or if the 95 percent interval of the
implied angle epsilon = contrast / 0.57 rad contains the Tuna-17 coin series' +0.0295 rad. IBM excludes the Tuna angle
when each backend's interval stays below it and the combined-error distance exceeds 3 sigma. Inputs: the analysis record
results/live/pathion_parallel_coset_analysis.json (rule null_selector_contrast) and the earlier angles of
c2_overrotation.txt.
"""

import math
import re

from d_data import HERE, SX_RESPONSE, analysis
from scipy import stats

BAND = 0.006
TUNA = (0.0295, 0.0070)

earlier = (HERE / "c2_overrotation.txt").read_text()


def parse(label: str) -> tuple[float, float]:
    found = re.search(
        rf"{label}\s+selector contrast \S+ \+- \S+ -> over-rotation ([+-]\d\.\d+) \+- (\d\.\d+) rad", earlier
    )
    if found is None:
        raise ValueError(f"no angle for {label} in c2_overrotation.txt")
    return float(found.group(1)), float(found.group(2))


print(f"falsifier: k0 contrast >= +{BAND} with the 1-CZ blocks at zero, or an epsilon interval containing +{TUNA[0]}")
print(f"response of the k0 contrast to the over-rotation: {SX_RESPONSE} per rad (written case)")
record = analysis()["backends"]
angles: dict[str, tuple[float, float]] = {}
distance: dict[str, float] = {}
for backend, body in record.items():
    blocks = body["rules"]["null_selector_contrast"]["blocks"]
    n = body["placements"]
    t = stats.t.ppf(0.975, n - 1)
    k0 = blocks["k0_base"]
    ones = [blocks[f"k{k}_base"] for k in (4, 8, 12)]
    one_mean = sum(b["mean"] for b in ones) / 3
    one_se = math.sqrt(sum(b["se"] ** 2 for b in ones)) / 3
    contrast = k0["mean"] - one_mean
    contrast_se = math.hypot(k0["se"], one_se)
    eps, eps_se = k0["mean"] / SX_RESPONSE, k0["se"] / SX_RESPONSE
    angles[backend] = (eps, eps_se)
    contains = eps - t * eps_se <= TUNA[0] <= eps + t * eps_se
    print(
        f"{backend:13s} placements {n}  k0 contrast {k0['mean']:+.4f} +- {k0['se']:.4f}  1-CZ mean {one_mean:+.4f} +- {one_se:.4f}"
        f"  k0 minus 1-CZ {contrast:+.4f} +- {contrast_se:.4f}"
    )
    print(
        f"{'':13s} epsilon {eps:+.4f} +- {eps_se:.4f} rad (95 percent [{eps - t * eps_se:+.4f}, {eps + t * eps_se:+.4f}]); "
        f"k0 band hit {k0['mean'] >= BAND}; interval contains Tuna angle {contains}; "
        f"signature flag {body['rules']['null_selector_contrast']['sx_overrotation_signature']}"
    )
    both = (TUNA[0] - eps) / math.hypot(TUNA[1], eps_se)
    distance[backend] = both
    alone = (TUNA[0] - eps) / eps_se
    print(
        f"{'':13s} Tuna angle minus epsilon {TUNA[0] - eps:+.4f} rad: {alone:.1f} sigma of the IBM error alone, "
        f"{both:.1f} sigma of both errors"
    )

print("earlier angles (c2_overrotation.txt, piecewise response of the compile):")
pool = dict(angles)
for label, key in (("ibm_fez k0", "ibm_fez earlier"), ("ibm_marrakesh k0", "ibm_marrakesh earlier")):
    eps, se = parse(label)
    pool[key] = (eps, se)
    print(
        f"  {key:22s} epsilon {eps:+.4f} +- {se:.4f} rad: Tuna distance {(TUNA[0] - eps) / math.hypot(TUNA[1], se):.1f} sigma of both errors"
    )

weights = {k: 1.0 / se**2 for k, (_, se) in pool.items()}
total = sum(weights.values())
mean = sum(weights[k] * pool[k][0] for k in pool) / total
se = math.sqrt(1.0 / total)
chi2 = sum(weights[k] * (pool[k][0] - mean) ** 2 for k in pool)
dof = len(pool) - 1
print(
    f"inverse-variance mean over {len(pool)} IBM readings (two new, two earlier): epsilon {mean:+.4f} +- {se:.4f} rad, "
    f"chi2 {chi2:.2f} on {dof} dof (p {stats.chi2.sf(chi2, dof):.2f})"
)
print(
    f"Tuna angle {TUNA[0]:+.4f} +- {TUNA[1]:.4f} minus the IBM mean: {(TUNA[0] - mean) / se:.1f} sigma of the IBM error alone, "
    f"{(TUNA[0] - mean) / math.hypot(TUNA[1], se):.1f} sigma of both errors; 95 percent upper bound of the IBM mean "
    f"{mean + 1.96 * se:+.4f} rad"
)
pooled_distance = (TUNA[0] - mean) / math.hypot(TUNA[1], se)
excluded = all(d > 3 for d in distance.values()) and pooled_distance > 3
print(
    f"IBM now excludes the Tuna angle at 3 sigma of both errors on the new readings and on the pooled mean: {excluded}"
)
print(
    "scope: the 0.57 per rad response is the k0 compile of the written case's model circuit; the earlier angles use the "
    "ibm_fez k0 compile's piecewise response (+0.557 and +0.427 per rad), and no ibm_kingston compile was simulated"
)
