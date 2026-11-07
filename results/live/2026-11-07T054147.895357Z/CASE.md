# Written case: whole-operand nullity on ibm_kingston (primary account)

Status: awaiting the owner's approval. This binding dry run belongs to the case in
[`../2026-11-07T054149.796663Z/CASE.md`](../2026-11-07T054149.796663Z/CASE.md), which holds the questions, the
design, the model values, the preregistered decision rules and the limits for both devices. The rows below are this
run's own.

| Item | Value |
|---|---|
| Account | primary (`GOROROBA_IBM_ACCOUNT` empty), 12 s remaining at 05:41 UTC |
| Backend, calibration | ibm_kingston, 2026-11-06T21:03:52-08:00 |
| Binding dry run | `2026-11-07T054147.895357Z`, source tree clean at 64f3f42ab |
| Placements | 16, replica scores 0.72 to 0.84 |
| Group, PUBs, shots | `pathion_wide_coset`, 145 PUBs of 1,792 shots, repetition delay 20 us |
| Executions, block reads | 259,840 executions, 4.16 million block reads |
| Worst-case charge | 10.66 s at 9.2 us residual (10.37 s at 8.1 us); 11 s billed against 12 s remaining |
| Ceiling, reserve | 12 s, 0 s |
| Check | `pathion_wide_coset_check.py 16 12` admits the plan |
| Billing risk | per-PUB charge term not excluded by the retained jobs: -1.1 +- 1.8 ms fitted, 2.6 ms at two sigma, 0.4 s at 145 PUBs against a 1.3 s margin to the ceiling |

Command, from the repository root after approval:

    GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_wide_coset_check.py 16 12' -- \
      --groups pathion_wide_coset --backends ibm_kingston --shots 1792 --rep-delay 2e-5 --replica-floor 0.5 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#1 \
      --max-total-execution-seconds 12 --max-execution-seconds 12 --reserve-seconds 0 \
      --min-remaining-seconds 1 --max-pending 100 --out ../results/live
