# Consult: the A_5 exceptional fibers after every success and every failure

Read-only. Do not edit, run heavy jobs, or touch the network. Write your answer as your final message.

## What is measured and why

Read first, in order:
1. docs/local/a5-failed-runs/purpose.md - target: the exceptional fiber Proj F(I), F(I) = sum_d I^d/m I^d, of the
   Pfaffian kernel-coordinate ideal I = (G) on a nullity-8 closure Y = V(J) at a boundary-orbit point; roadmap item 6
   (attaching maps) needs these limit sets.
2. docs/local/a5-failed-runs/decision-record.md - the authority: reconciliation, falsifiers F1-F7, steps S0-S7, and
   every result bullet appended through 2026-10-29 (read all of section 5 onward).
3. docs/local/a5-failed-runs/lab-map.md - every compute resource, limit and observed failure mode.
4. docs/PYTHON.md and docs/runbooks/compute-flags.md - interpreters, environments, flag review and memory rule.

Supporting detail: build/part-a-report.md, build/part-b-report.md, build/codex-review.md, picture-codex.md,
review-codex.md, review-claude.md, kaggle-tpu/review-codex.md, templates/*.sing, probes/*.py, and in the worktree
~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/ the files fiber_cone_driver.py,
fiber_certificates.py, fiber_inputs.py, nullity16_rees_fibers.py and README.md (section "The nullity-16 Rees fibers").

## State in one table (verify each against the decision record)

| Pair | Degree-certified h_d (F_32009) | Full fiber (method B / candidate ideal) |
| --- | --- | --- |
| X- (= X+ by t9 -> -t9) | 15, 51, 122 | method B: stalled after pivot, 3 h and 12 h (12 h run near its cap, 9.2 GB) |
| Iso | 17, 85, 265 | method B: stalled after pivot G_16, 6 h, about 10 GB |
| E8bar->N+ | 21, 83 | method B on Azure: stalled after pivot G_19, 10 h, 72 GB |
| E8bar->N- | 21, 83 | method B on Azure: stalled after pivot G_19 |
| W8->N- (= N+) | 24, 156 | method B on Azure: cut off at 25 min by a VM outage |
| E8bar->VB | 10, 34, 80 (driver-reproduced) | method B 2 h stalled after pivot G_3; candidate ideal std(L) in 18 vars timed out / 3 GB |
| nullity-16 rows | B9, V, VB, Va complete (P^2, conic, points) | the ten nullity-8 rows time out at modular_rees_fiber (300 s) |

Every completion route so far dies in one step: the Groebner basis of the Rees-type ideal (saturation by the pivot g,
or std(L) for the candidate ideal), after the pivot is chosen. Degree-by-degree method A succeeds wherever run.

## Questions

Answer each with a concrete, checkable procedure (commands, Singular/M2/msolve code sketches, expected cost and the
result that would falsify it), ranked by expected value per compute hour on the resources of lab-map.md.

1. Diagnosis. Why does the Rees saturation stall while method A succeeds? Name the mechanism (degree of the
   saturation, number of slice variables, coefficient growth, ordering) using the logged sizes, not generalities.
2. Reformulations that avoid the full saturation and still certify the fiber scheme or its support: for example a
   degree-truncated std with a Hilbert-function stop (and what bound makes it a proof), Rees algebra by Jacobian dual
   or syzygy methods, presenting F(I) via the special fiber of a Sagbi/initial algebra, linear-type or
   relation-type bounds from the h_d already measured, a linear section reducing variables, elimination over a
   generic line through the base point, msolve or M2 alternatives, or multimodular/Hensel lifting. Say which apply
   to these rings and why.
3. Can the measured h_d sequences plus the degree-2 relation ideals (K2: dimension, degree, primes in the decision
   record) already decide the reduced fiber support for any pair? State exactly what extra fact closes the gap.
4. Dense-family route: design the arc sampler (genuine limit points of G along curves into the base point) and the
   dimension certificate that would let fiber_certificates.py report support-equal rather than a lower bound.
5. Compute plan: assign each surviving procedure to host, Azure FX4mds_v2 (one per region, 82 GiB), Kaggle CPU or
   TPU VM (queue risk), or GitHub Actions, with memory caps and time limits that the logged failures justify.
6. What to stop doing: which runs or tools the evidence says will not converge at any affordable size.

Keep the answer under 250 lines. Mark each claim observed (with the file it comes from) or inferred.
