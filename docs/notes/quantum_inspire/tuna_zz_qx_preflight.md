# Compact QX preflight for the Tuna-17 ZZ proposal

**Status: proposed, generated offline, not submitted.** This is the concrete
QX preflight design for the [Tuna-17 conditional-Ramsey cross-check](tuna_zz_map.md).
The hardware case is retained as a complete design reference and is not
recommended for acquisition unchanged: its 139 batches imply at least
4.6 hours of hardware pauses, and the later Tuna records make the 20/40 us
points and calibration stability material concerns. A revised hardware
case needs corresponding revised twins. This preflight's 425,984 emulator
shots are a separate proposed acquisition, requiring its own authorization.
The completed ten-circuit
[QX control of the acquired bipartite map](../../../results/quantum_inspire/coupler_zz_qx_analysis.json)
belongs to that earlier case and does not validate these new payloads.
The subsequently retained zero-divisor QX twins likewise exercise their
own circuits and are not substitutes for this case's conformance criteria.

`scripts/qi_zz_map_qx.py` transforms the reviewed Tuna circuits into 416 QX
twins. Each packing uses only its active pair endpoints, relabeled in sorted
physical-qubit order onto 2–8 qubits, within the QX limit of 10 in the
[retained catalogue](../../evidence/quantum_inspire/catalogue.json).
The transformation removes only the inactive wires' explicit waits. Every
active gate, wait duration, register-wide barrier and measurement survives.
Initialization and measurement apply to the compact register. An unexpected
instruction or non-wait operation on an omitted wire is an error.

Each circuit records its Tuna source path and SHA256, the physical-to-QX map,
the original edge endpoints and its exact compact register width. The QX
plan and all batch manifests bind the complete Tuna plan, backend catalogue
and QX builder hashes. Batch boundaries and acquisition order match the
hardware proposal. A batch spanning two packings can contain different
register widths: its `nqubits` is the maximum, and every circuit declares
its own exact width.

| Proposed QX resource | Count |
|---|---:|
| Circuits | 416 |
| Batches | 139: 138 of three, one of two |
| Shots per circuit | 1,024 |
| Total emulator job shots | 425,984 |
| Compact register width | 2–8 qubits |
| Hardware jobs executed by this preflight | 0 |

These counts are **additional** to the hardware proposal. No account cost,
queue duration or execution-time quote has been inferred.

## Fixed ideal criteria

At ideal zero detuning, explicit waits do not generate the physical phase
being sought on Tuna. Every readout calibration bit must equal its prepared
value. Every Ramsey neighbor must equal its prepared value, and every
X-quadrature probe must read zero. **Any deterministic mismatch fails the
preflight.** Qubit zero is the rightmost raw-string character, as in the
retained QX acquisitions and the
[repository's decoder regression](../../../scripts/qi_crosstalk_teleport_cases.py).

Every Y-quadrature probe has ideal probability one half. Across the complete
series there are 576 such marginals. For each, the accepted deviation is

\[
|\widehat p_1-1/2|\leq
\sqrt{\frac{\log(2\cdot576/0.01)}{2\cdot1024}}.
\]

This Hoeffding bound and a union bound limit the ideal false-failure
probability to at most 1% for the family, assuming independent shots within
each job. Independence between different qubits' marginals is unnecessary.
The check concerns marginals; it does not establish the full joint output
distribution or independent errors.

The offline result reader requires every planned job, digest-bound v2
submission receipts, completed service records, exact shot denominators,
per-circuit register widths, unique acquisition job identifiers, and
agreement between ordered raw shots and retained service histograms.
An incomplete or conflicting acquisition produces no analysis report. A
complete acquisition may produce `passes: false`; the report keeps the
specific failed circuit criteria and does not submit anything.

## Reproduce and inspect

```bash
python scripts/qi_zz_map_qx.py --check results/quantum_inspire/cases/zz_map_qx
python scripts/qi_zz_map_qx.py --self-test
python -O scripts/qi_zz_map_qx.py --self-test
```

The self-test checks sparse-wire relabeling, preservation of global waits
and barriers, rejection of discarded operations, the fixed ideal criteria,
rightmost-bit decoding, and rejection of raw shots that conflict with their
retained histogram. It does not run a quantum simulator or contact QI.

After an authorized QX acquisition, collect each reviewed batch into a
separate `RUNS_ROOT/batch-NNN/` directory with its manifest, circuit files,
receipt, service results and raw shots, then run:

```bash
python scripts/qi_zz_map_qx.py --analyze RUNS_ROOT \
  --plan results/quantum_inspire/cases/zz_map_qx/plan.json \
  --out NEW_REPORT.json
```

The output path must be new. A passing QX report supports ideal native-gate
and wiring conformance for the compact twins. It does not validate Tuna's
compiled physical schedule, calibrations, spectator effects, idle ZZ or
coupler settings, or establish that the six-delay hardware design is
practical. The hardware acquisition recommendation remains the one in the
linked design note. Any later authorized hardware sequence proceeds one
batch at a time, with collection, sanity review and the prescribed pause
between batches.
