"""Empirical check: transpile a ripple atlas template symbolically, bind bright
vs dark angles, verify physical gate structure is identical."""
import sys
sys.path.insert(0, '/home/hatch/workspace/gororoba-quantum-work/gororoba_quantum')
import parallel
parallel.ordered_map = lambda f, items, min_items=2: [f(x) for x in items]

from ripple_experiments import _definitions
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
import math

groups, config = _definitions()

# Grab one atlas template circuit (symbolic, with Parameter)
template = None
for g in groups:
    for sm in g.members:
        m = sm.member if hasattr(sm, 'member') else sm
        if m.name.startswith('ripple_atlas') and '_phase0_' in m.name:
            template = m.circuit
            break
    if template is not None:
        break

print(f"template qubits: {template.num_qubits}, params: {template.parameters}", flush=True)
print(f"template ops (logical): {dict(template.count_ops())}", flush=True)

# Transpile symbolically (as live_run._compile does, but with a generic backend)
# Use optimization_level=3 to give the optimizer maximum chance to diverge
t = transpile(template, optimization_level=3)
print(f"\ntranspiled (symbolic) ops: {dict(t.count_ops())}", flush=True)
print(f"transpiled depth: {t.depth()}", flush=True)

# Now bind bright (0) vs dark (pi) and compare physical structure
param = list(template.parameters)[0]
bright = t.assign_parameters({param: 0.0})
dark = t.assign_parameters({param: math.pi})

cb, cd = dict(bright.count_ops()), dict(dark.count_ops())
print(f"\nbound bright ops: {cb}", flush=True)
print(f"bound dark   ops: {cd}", flush=True)
print(f"bright depth: {bright.depth()}, dark depth: {dark.depth()}", flush=True)
print(f"\nop counts identical: {cb == cd}", flush=True)
print(f"depth identical: {bright.depth() == cd and True}", flush=True)

# Also check: do the bound circuits differ ONLY in rz angles?
# Compare instruction sequences ignoring parameter values
def structure_key(qc):
    return [(inst.operation.name, tuple(qc.find_bit(q).index for q in inst.qubits)) for inst in qc.data]

sb, sd = structure_key(bright), structure_key(dark)
print(f"instruction structure identical: {sb == sd}", flush=True)
print(f"n instructions: {len(sb)}", flush=True)
