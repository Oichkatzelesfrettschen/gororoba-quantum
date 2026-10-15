import json, numpy as np, sys
from scipy import stats

D = '/home/hatch/workspace/gororoba-audit/results/live/2026-10-13T025444.603480Z/'
d = json.load(open(D+'collect.json'))
e = d[0]
fm = e['family_measurements']

def tv(p, q):
    return 0.5*np.abs(np.asarray(p)-np.asarray(q)).sum()

uniform = np.ones(16)/16
print("=== TV distance from uniform (hw vs replay) ===")
print(f"{'name':55s} {'TV_hw_unif':>10s} {'TV_rp_unif':>10s} {'TV_hw_rp':>10s}")
for k in sorted(fm):
    if 'walk' in k and 'readout' not in k:
        hw = np.array(fm[k]['replica_probabilities'][0])
        rp = np.array(fm[k]['replayed_replica_probabilities'][0])
        print(f"{k:55s} {tv(hw,uniform):10.4f} {tv(rp,uniform):10.4f} {tv(hw,rp):10.4f}")

print("\n=== readout members ===")
for k in sorted(fm):
    if 'walk' in k and 'readout' in k:
        hw = np.array(fm[k]['replica_probabilities'][0])
        rp = np.array(fm[k]['replayed_replica_probabilities'][0])
        print(f"{k:55s} {tv(hw,uniform):10.4f} {tv(rp,uniform):10.4f} {tv(hw,rp):10.4f}")

# chi-square test: is hw consistent with uniform? (1024 shots)
print("\n=== chi2 test hw vs uniform (1024 shots, 15 dof) ===")
for k in sorted(fm):
    if 'walk_lane0' in k and 'readout0' in k:
        hw = np.array(fm[k]['replica_probabilities'][0])
        chi2, p = stats.chisquare(hw*1024, uniform*1024)
        print(f"{k}: chi2={chi2:.1f} p={p:.2e}")
