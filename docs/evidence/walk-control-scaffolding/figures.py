import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

D = '/home/hatch/workspace/gororoba-audit/results/live/2026-10-13T025444.603480Z/'
d = json.load(open(D+'collect.json'))
fm = d[0]['family_measurements']
OUT = '/home/hatch/workspace/quantum-audit/walk-control/'

# Fig 1: hw vs replay P(0000) across depths — flat hw vs structured replay
fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
for ax, (lane, pair) in zip(axes.flat, [(0,(25,31)), (0,(9,22)), (1,(25,31)), (1,(9,22))]):
    depths, hws, rps = [], [], []
    for depth in range(5):
        k = f'ripple_walk_lane{lane}_pair{pair[0]}_{pair[1]}_depth{depth}_packed'
        depths.append(depth)
        hws.append(fm[k]['replica_probabilities'][0][0])
        rps.append(fm[k]['replayed_replica_probabilities'][0][0])
    ax.plot(depths, hws, 'o-', color='crimson', label='hardware', ms=8)
    ax.plot(depths, rps, 's--', color='steelblue', label='replay (calibration noise)', ms=8)
    ax.set_title(f'lane{lane} pair{pair[0]}_{pair[1]}: P(0000) vs depth')
    ax.set_xlabel('walk depth'); ax.set_ylabel('P(0000)')
    ax.legend(); ax.grid(alpha=0.3)
fig.suptitle('Walk depth sweep: hardware is flat, replay is structured\n(physical gates identical across depths — only virtual RZ angles change)', fontsize=12)
fig.tight_layout(); fig.savefig(OUT+'fig1_depth_sweep.png', dpi=120)

# Fig 2: full distribution for readout0 lane0: hw vs replay vs uniform
fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(16)
hw = np.array(fm['ripple_walk_lane0_readout0']['replica_probabilities'][0])
rp = np.array(fm['ripple_walk_lane0_readout0']['replayed_replica_probabilities'][0])
w = 0.25
ax.bar(x-w, hw, w, label='hardware P(0000)=0.064', color='crimson')
ax.bar(x, rp, w, label='replay P(0000)=0.540', color='steelblue')
ax.bar(x+w, np.ones(16)/16, w, label='uniform', color='gray', alpha=0.5)
ax.set_xlabel('outcome'); ax.set_ylabel('probability'); ax.set_xticks(x)
ax.legend(); ax.grid(alpha=0.3)
ax.set_title('readout0 lane0 (prepare |0000>, measure): full distributions')
fig.tight_layout(); fig.savefig(OUT+'fig2_readout_dist.png', dpi=120)

# Fig 3: effective CZ error fit
fig, ax = plt.subplots(figsize=(8, 5))
p = np.array([0.002, 0.005, 0.010, 0.015, 0.020])
sim_p0 = np.array([0.6290, 0.3372, 0.1551, 0.0960, 0.0760])
ax.semilogx(p, sim_p0, 'o-', color='darkgreen', ms=8, label='Aer depolarizing sim (252 CZ circuit)')
ax.axhline(0.0645, color='crimson', ls='--', label='hardware: 0.0645')
ax.axhline(0.540, color='steelblue', ls='--', label='replay (calibration): 0.540')
ax.set_xlabel('per-CZ depolarizing error'); ax.set_ylabel('P(0000)')
ax.legend(); ax.grid(alpha=0.3)
ax.set_title('Effective noise: hw needs ~2% CZ error vs ~0.25% calibrated (8x gap)')
fig.tight_layout(); fig.savefig(OUT+'fig3_noise_fit.png', dpi=120)
print("figures saved")
