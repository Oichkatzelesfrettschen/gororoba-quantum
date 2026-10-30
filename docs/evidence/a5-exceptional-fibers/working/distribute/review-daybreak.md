I reviewed only `distribute/brief.md` and section 10 of `decision-record.md`. I ran no solvers and made no writes.

1. The falsifiers

The proposed second-prime Hilbert-function comparisons are valid reproducibility checks, but the diagnosis in the brief is too strong.

A differing value establishes only that the first-prime result failed to reproduce under the second-prime input. The difference does not by itself distinguish:

- an exceptional first or second prime;
- producer drift;
- a driver or transport defect;
- genuine characteristic dependence.

The regenerated Q(i) producer receipt makes unnoticed producer drift less plausible only if the replay verifies the producer identity and input digests. Byte-identical driver and input provenance would then move the main suspicion toward an exceptional prime or characteristic dependence. A third suitable prime, or a characteristic-zero argument, is needed to identify which prime is exceptional. Therefore each job should record this falsifier:

> The second-prime value differs from the first-prime value, falsifying two-prime stability for that degree; provenance checks and another characteristic are required to determine the cause.

K1, K2, K3, and G1 are bounded checks of degrees already computed. G2 computes a new degree and therefore has no cross-prime falsifier yet: its immediate checks are internal completion and consistency, followed by a second-prime replay. Section 10 also limits every method-A result to the computed degree; agreement through degree 3 proves nothing about later degrees or the full fiber.

2. Reintroduced stalled families

K1–K3, G1, and G2 use segmented method A. They are not method B, `std(L)`, pivot saturation, or full-graph msolve. Their weakness is priority, not disguised algorithmic identity: they produce finite-degree Hilbert data while section 10 makes arcs, kernel limits, and chart decompositions the main line.

K4 is acceptable only if it literally implements section 10’s projective-chart route. A single global `minAssChar` call with an 11-hour cap is minAss-first in new clothes, contradicting the explicit stop and the stated “in projective charts” step. The cap changes the waiting time, not the algorithm.

Run radical and `minAssChar` chart by chart, with one bounded job per chart or chart pair. Retain `linear_gens` for each resulting prime. The plan estimates 45 minutes per pair; an undivided 11-hour computation abandons that decomposition and hides which chart caused the cost.

3. Better use of the Kaggle slots

The proposed allocation spends five of six slots on method-A coefficients even though section 10 says those coefficients certify only their individual degrees. That is poor alignment with the final plan.

The best allocation is:

- one slot for Iso projective-chart radical and `minAssChar`;
- one slot for W8→N− projective-chart radical and `minAssChar`;
- one slot for E8bar→N− projective-chart radical and `minAssChar`;
- one slot for the X− arc certificate in the reduced \(\mathbf P^{11}\);
- one slot for VB order-1/order-2 arc or kernel-limit work that is ready and independent of the host process;
- one slot for a bounded method-A replay as secondary work.

Dependencies matter. Kernel-limit jobs require completed arc data, and second-prime replay of arcs or decompositions requires first-prime receipts. A slot whose required artifact is unavailable should take a short, already-defined method-A segment rather than inventing another global elimination.

If only four independent chart/arc jobs are ready, K1–K3/G1 are reasonable quota-filling work. G2 has lower evidentiary priority because its new \(h_3\) value neither decomposes the reduced support nor supplies the attaching datum. W8 degree 3 also carries a known 14 GB observation and fits Kaggle memory, but it remains secondary to plan steps 2–6.

4. GitHub Actions and qBraid Lab

Keep the immediate bounded work on Kaggle. Its quota expires first, its hosts provide roughly the same four CPU cores as GitHub Actions with twice the memory and twice the wall-time allowance, and the W8 observation already exceeds the comfort margin of a 16 GB runner.

GitHub Actions is suitable only for a deterministic job known to remain below 16 GB and six hours, such as a small method-A replay or receipt check. It should serve as overflow after the six Kaggle slots are occupied, not replace a Kaggle slot before the reset.

qBraid Lab should take nothing in this round. Its approximately 1.8 vCPU profile is slower, its quota renews later, and starting a session requires a separate approved case. Neither the final plan nor the available evidence identifies a job whose result benefits from that substrate.

Verdict: approve the use of expiring Kaggle compute after replacing K4 with explicit projective-chart jobs and moving most capacity from finite-degree method-A expansion to arc, kernel-limit, and chart-decomposition work. Treat second-prime disagreement as a falsifier of stability, not as a diagnosis of “bad prime,” producer drift, or driver failure.