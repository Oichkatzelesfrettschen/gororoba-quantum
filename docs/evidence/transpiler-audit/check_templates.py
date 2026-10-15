import sys, re, statistics
from collections import defaultdict
sys.path.insert(0, '/home/hatch/workspace/gororoba-quantum-work/gororoba_quantum')
# Force sequential execution (process pool broken in this env)
import parallel
parallel.ordered_map = lambda f, items, min_items=2: [f(x) for x in items]
from ripple_experiments import _definitions

groups, config = _definitions()
print(f"n_groups: {len(groups)}", flush=True)

name_to_info = {}
for g in groups:
    for sm in g.members:
        m = sm.member if hasattr(sm, 'member') else sm
        name_to_info[m.name] = (id(m.circuit), dict(m.binding) if m.binding else {})

print(f"n_members: {len(name_to_info)}", flush=True)

circ_to_names = defaultdict(list)
for name, (cid, binding) in name_to_info.items():
    circ_to_names[cid].append((name, binding))

print(f"n_unique_templates: {len(circ_to_names)}", flush=True)
shares = [len(v) for v in circ_to_names.values()]
print(f"members per template: min={min(shares)}, max={max(shares)}, mean={statistics.mean(shares):.1f}", flush=True)

# Bright/dark pairs: phase0 vs phase4 for same (lane, kite, edge)
pair_check = defaultdict(dict)
for name, (cid, binding) in name_to_info.items():
    if '_phase' in name and name.startswith('ripple_atlas'):
        mm = re.match(r'(ripple_atlas_lane\d+_kite\d+_edge\d+_\d+)_phase(\d+)_atlas', name)
        if mm:
            key, phase = mm.group(1), int(mm.group(2))
            pair_check[key][phase] = (cid, binding)

n_pairs = 0
n_match = 0
mismatches = []
binding_diffs = []
for key, phases in pair_check.items():
    if 0 in phases and 4 in phases:
        n_pairs += 1
        cid0, b0 = phases[0]
        cid4, b4 = phases[4]
        if cid0 == cid4:
            n_match += 1
            # record the binding values to confirm they differ only in angle
            binding_diffs.append((b0, b4))
        else:
            mismatches.append(key)

print(f"\nbright/dark pairs (phase0 vs phase4): {n_pairs}", flush=True)
print(f"sharing identical circuit object: {n_match}", flush=True)
print(f"mismatches: {len(mismatches)}", flush=True)
if mismatches:
    print("mismatches:", mismatches[:5], flush=True)
if binding_diffs:
    b0, b4 = binding_diffs[0]
    print(f"\nexample bindings phase0: {b0}", flush=True)
    print(f"example bindings phase4: {b4}", flush=True)
    # Check all pairs differ ONLY in the phase parameter value
    all_keys_same = all(set(x.keys()) == set(y.keys()) for x, y in binding_diffs)
    print(f"all pairs bind the same parameter keys: {all_keys_same}", flush=True)
