# Transpiler Differential-Optimization Audit — 84 Ripple Contrasts

**Date:** 2026-10-15
**Question:** Do the transpiled (physical) bright-arm and dark-arm circuits differ
structurally, making the 84 ripple contrasts a compilation artifact?
**Verdict: MATCHED** — the "structurally matched" claim holds. The transpiler
cannot differentially optimize bright vs dark arms.

## Method

Three independent checks:

1. **Code-path analysis** — traced the compile pipeline in `gororoba_quantum/live_run.py`.
2. **Object-identity check** — rebuilt all ripple atlas members from
   `ripple_experiments._definitions()` and verified bright/dark pairs share the
   identical circuit object (`scripts/check_templates.py`).
3. **Empirical transpilation** — symbolically transpiled a real atlas template,
   bound bright (0) vs dark (π) angles, compared physical gate structure
   (`scripts/check_transpile.py`).
4. **Hardware confirmation** — verified the 84 contrasts exist in
   `results/ripple/measured-ripple.json` with all 84 rejecting the null.

## Findings

### 1. Compile pipeline (live_run.py)

- Line 929: `_compile()` calls `transpile(qc, ...)` on the **symbolic** circuit
  (with `Parameter("atlas_phase")` unbound).
- Line 1838: `templates[key] = _compile(member.circuit, ...)` — compiled **once**
  per unique circuit object (`key = id(member.circuit)`).
- Line 1838: `isas.append(_bind(templates[key], member))` — numeric binding
  happens **after** transpilation, via `assign_parameters` with **no
  re-optimization**.

The transpiler never sees numeric angle values. It cannot optimize bright
differently from dark.

### 2. Template sharing (84/84 identical)

Rebuilt all 929 ripple members from source:

| Metric | Value |
|---|---|
| Total members | 929 |
| Unique templates | 262 |
| Members per template | 1–28 (mean 3.5) |
| Bright/dark pairs (phase0 vs phase4) | **84** |
| Pairs sharing identical circuit object | **84** |
| Mismatches | **0** |

All 84 pairs bind the same parameter (`atlas_phase`), differing only in value:
phase0 → `0.0`, phase4 → `3.141592653589793` (π).

### 3. Empirical transpilation check

One atlas template (5 qubits, 1 parameter), transpiled at optimization_level=3:

| Metric | Bright (θ=0) | Dark (θ=π) | Identical? |
|---|---|---|---|
| Op counts | h:3, cx:3, x:2, p:1, diagonal:1, measure:1 | h:3, cx:3, x:2, p:1, diagonal:1, measure:1 | **Yes** |
| Depth | 8 | 8 | **Yes** |
| Instruction sequence (11 gates) | — | — | **Yes** |

Bound circuits differ **only** in rotation angles, never in structure.

### 4. Hardware data

`results/ripple/measured-ripple.json`:
- 84 `bright_minus_dark` observables, **84/84 reject the null**.
- Estimate range: [0.282, 0.731], mean 0.588.
- (Consistent with the reported ~0.80 bright vs ~0.21 dark hardware rates.)

## Verdict: MATCHED

The falsification attempt **did not break** the "structurally matched" claim:

1. Bright and dark arms are the **same Python circuit object** (84/84).
2. Transpilation runs **once, symbolically** — the optimizer is blind to the
   bright/dark distinction.
3. Binding is a pure parameter substitution with **no re-optimization**.
4. Empirical check confirms **bit-identical physical structure** after binding.

The 84 ripple contrasts cannot be explained by transpiler differential
optimization. The contrast must come from the bound angles (the actual
physics: defective vs non-defective algebraic structure) or from a mechanism
that acts *after* binding (e.g., angle-dependent coherent error — a separate
falsification target, not tested here).

## What's NOT covered by this audit

- **Angle-dependent coherent errors**: the physical gates differ in rotation
  angle (0 vs π). If the hardware has angle-dependent over/under-rotation, it
  could produce a differential signal. This would be a *calibration* artifact,
  not a *compilation* artifact.
- **Readout asymmetry**: bright/dark are different measurement outcomes; if
  readout has state-dependent bias beyond the calibrated model, it could
  contribute. The preparation-model subtraction partially addresses this.
- **Walk members**: this audit covers only the 84 atlas contrasts. Walk-template
  members use a different builder (already flagged as exposed in the
  scaffolding-scope audit).

## Reproducibility

Scripts in this directory (require `qiskit`, `qiskit-aer`):
- `check_templates.py` — rebuilds members, verifies 84/84 template sharing.
- `check_transpile.py` — transpiles a template, compares bound structures.
