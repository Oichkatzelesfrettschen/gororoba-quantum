# Walk-control discrepancy: compilation artifact, not physics

Date: 2026-10-15. Analysis of `results/live/2026-10-13T025444.603480Z/collect.json` (ripple campaign bundle).

## TL;DR

The walk-control hardware-vs-replay discrepancy is not a physics mystery — it is a compilation
artifact. The walk circuits (including the "readout" SPAM checks and the "depth sweep") all
execute **144–252 physical CZ gates even when logically empty**, because the native synthesis
emits full Gray-code scaffolding for zero-angle phase gates. The hardware is not disagreeing with
the model about quantum walks; it is drowning in gate noise from gates that do nothing. The
replay's calibration noise model underestimates the true error by ~8x, and the residual structure
is not depolarizing at all.

## Evidence

- `_native_walk_circuit` (`gororoba_quantum/ripple_experiments.py:100`) expands every `p`/`mcphase`
  into Gray-code parity rotations with physical `SX`+`CZ`, **regardless of bound angle**. Only the
  `RZ` angles (virtual, zero-cost) carry the parameter.
- Rebuilt template with readout0 bindings: **144 CZ + 328 SX**, depth 942 — for a circuit that
  should be "prepare |0000>, measure."
- Actually executed (isa.qpy pub_55, qubits [1,2,3,4]): **252 CZ + 491 SX**, depth 857.
- Noiseless Statevector sim of the executed circuit: P(0000) = 0.9999999999999964 — logically
  perfect, so the failure is 100% physical noise, 0% wrong circuit.
- **Depth sweep is physically meaningless**: hw P(0000) is flat 0.03–0.12 across depths 0–4 while
  replay varies 0.03–0.62. All depths share identical physical gates; only virtual RZ differs.
- With 252 CZs, even 1%/CZ gives 0.99^252 ≈ 0.08 ≈ hw. Modest gate errors fully explain the
  suppression. (fig1)

## Ranked hypotheses

1. **Zero-angle scaffolding dominates (primary, structural).** See evidence above.
2. **True gate error ~8x calibration (quantitative).** Depolarizing fit on the exact executed
   circuit (Aer, 20k shots): 0.2%/CZ reproduces replay (0.54); 2.0%/CZ reproduces hw (0.064).
   Calibration model (~0.25% CZ) matches replay; hardware needs ~2%. Lane asymmetry (lane0
   hw=0.064 vs lane1 hw=0.131 on different physical qubits) supports qubit-dependent error.
   (fig3)
3. **Non-depolarizing systematic error (structural).** Affine fit hw_d = (1−λ)·ideal_d + λq fails
   (λ>1; least-squares (1−λ) goes negative for some depths). hw distributions have structure:
   lane0 readout0 peaks at outcomes 12 (0.29), 8 (0.14), 4 (0.11) — specific qubits excited, not
   uniform spread. Chi-square rejects uniform at p~1e-259. Candidates: coherent over-rotation
   over 252 CZs, leakage, crosstalk. Not yet discriminated. (fig2)
4. **Readout misassignment (ruled out as primary).** Even 8%/qubit gives P(all 4 correct) ≥ 0.72.
   Cannot produce 0.064.
5. **Crosstalk from packed neighbors (weak).** Walk readout shares pub_55 with 7 atlas readout
   members, but zero cross-boundary 2-qubit gates and trivial neighbors. Not the driver.

## Most surprising finding

The campaign's simplest circuit — the readout SPAM check, the thing everything else is calibrated
against — was never a SPAM check. It executed 252 entangling gates. And the "walk depth sweep,"
the experiment's central dial, never swept anything physical. The repo was measuring the noise
floor of its own compiler output and calling the flat line a physics result. The falsified
terminal-channel model was trying to explain a discrepancy that lives one layer down, in
synthesis.

## Proposed diagnostic (cheap, decisive)

**Scaffolding A/B**: on the same 4 physical qubits, same calibration window, run
(a) readout0 via the current symbolic template (252 CZ) and
(b) readout0 via a pruned circuit (`QuantumCircuit(4,4); measure`, 0 CZ), 1024 shots each.
If (b) gives P(0000)≈0.95+ and (a) gives ≈0.06, scaffolding is proven the culprit — fix by pruning
zero-angle gates in `_native_walk_circuit` (or bind-then-optimize before transpiling), then re-run
the walk sweep to see if hw tracks replay.
**Follow-up**: 2-qubit RB or Bell-state fidelity on the same qubits to pin true CZ error (2% vs
0.25%) — discriminates hypotheses 2 vs 3.

## Honest limits

- The 252-vs-144 CZ gap (executed vs rebuilt template) is unexplained — possibly transpiler
  decomposition or a version subtlety; order of magnitude is what matters.
- Bit-ordering of the 16-dim outcome vector wasn't fully pinned, so the "which physical qubits are
  excited" reading of the peaks is provisional (doesn't affect the hw-vs-replay gap, which uses
  identical ordering).
- No per-shot timestamps in the raw job data, so drift analysis wasn't possible.

## Artifacts in this directory

- `fig1_depth_sweep.png` — flat hw vs structured replay across depths
- `fig2_readout_dist.png` — readout0 full outcome distributions
- `fig3_noise_fit.png` — effective noise fit showing the ~8x gap
- `analyze.py`, `figures.py` — analysis and figure-generation scripts
