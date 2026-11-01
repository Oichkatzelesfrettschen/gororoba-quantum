# Ascella two-photon associator predecessor and sentinel-leakage campaign

This is the preregistered design document for the prospective, cost-bounded phase-request
predecessor-dependence and spatial-sentinel benchmark on Quandela Ascella (`qpu:ascella`).
It unifies the algebraic nonassociativity of octonions, two-photon interference on an integrated
photonic mesh, prospective predecessor carryover conditioning, and chip-wide spatial sentinel monitoring.

The implementation is grounded in the repository's Cayley–Dickson specification (`gororoba_quantum/cd_core.py`),
the photonic template decomposition (`scripts/hypercomplex_cases.py`), the Quandela platform execution
framework (`scripts/qd_platform.py`), and the evidence-closure paired-intervention protocol
([docs/runbooks/evidence-closure.md](../runbooks/evidence-closure.md)).

Executable scripts:
- [`scripts/ascella_associator_predecessor.py`](../../scripts/ascella_associator_predecessor.py)
- [`tests/scripts/test_ascella_associator_predecessor.py`](../../tests/scripts/test_ascella_associator_predecessor.py)

---

## 1. Literature reconciliation and adversarial audit

An adversarial review was conducted via Codex using `gpt-daybreak-blue-latest` to confront the proposed
campaign with published literature, physical platform specifications, and prior art across
the sibling checkouts `../math` and `../gororoba-quantum-documents` of the gororoba workspace, and external
publications.
The audit report is recorded in `scratch/codex_review/review_report.md`.

### Falsifications and necessary framing corrections

1. **Heater voltages vs requested phases:**
   Published Ascella hardware documentation ([Maring et al., Nature Photonics 2024](https://doi.org/10.1038/s41566-024-01403-4);
   repository transcription [`docs/notes/papers/2306.00874.md`](../notes/papers/2306.00874.md)) establishes that
   the platform solves a coupled nonlinear calibration system $\boldsymbol{\phi} = A \mathbf{V}^{\circ 2} + \mathbf{b}$,
   where off-diagonal elements encode thermal crosstalk and $\mathbf{b}$ contains passive fabrication offsets.
   The user API accepts phases rather than direct DAC voltages or heater currents. Consequently, requesting
   $\phi = 0$ does not imply zero dissipated power, and requesting $\phi = 2\pi$ does not guarantee higher dissipation
   if the server-side compiler normalizes phases into $[0, 2\pi)$ or selects a low-voltage branch.
   **Remedy:** The experiment is strictly defined as a **phase-request predecessor-dependence benchmark**,
   measuring the end-to-end response of the cloud compiler and hardware system, rather than an unmediated physical
   thermal dissipation proof.

2. **Optical phase wrapping as an optical-twin control:**
   Under classical and quantum wave optics, a phase shift of $2\pi$ is an exact identity: $e^{i 2\pi} = 1$.
   Perceval client validation preserves exact $2\pi$ phases on components (`perceval/utils/parameter.py`),
   and Perceval's unitary computation confirms $\|U(2\pi) - U(0)\| < 10^{-12}$.
   Condition Wrapped ($P_{\text{wrapped}}$) therefore presents the exact same optical transfer matrix as Condition Cold ($P_{\text{cold}}$).
   Any statistically significant deviation between targets following $P_{\text{wrapped}}$ versus $P_{\text{cold}}$
   specifically detects software-stack branch differences, compiler state caching, or DAC voltage selection.

3. **Thermal time constants vs inter-iteration switching:**
   Integrated thermo-optic phase shifters on silica/SiN typically exhibit thermal relaxation time constants
   $\tau \approx 8.5\,\mu\text{s}$ ([Milanizadeh et al., 2019](https://doi.org/10.1109/JSTQE.2019.2927576)).
   Retained Ascella execution data show that a 64-iteration job took 186 seconds ($\approx 2.9\,\text{s}$ per iteration).
   Unless slow packaging/substrate thermal modes exist, millisecond-scale settling delays between iterations
   would allow localized heater junctions to thermalize completely. The experiment tests for residual packaging drift,
   drift in the laser/source or detector subsystems, and DAC-level carryover.

4. **12-mode spatial sentinel array and threshold bunching:**
   Ascella employs 12 single-photon threshold detectors that cannot resolve photon number. Coincidence counts on
   modes 0..3 are sensitive to port-dependent losses, higher-order multi-photon emissions ($g^{(2)} = 1.9\%$),
   and scattered optical leakage outside the logical subspace.
   **Remedy:** The experiment continuously monitors all 12 modes. Modes 4..11 serve as a spatial sentinel array
   to measure uncommanded optical leakage, and predecessor transmission is actively verified during predecessor iterations.

5. **Ascella credit billing rule:**
   Retained Quandela Cloud billing records show that jobs are charged per job as:
   $$\text{Charge} = 1 + 10^{-6} \max_i(\text{shots}_i)\quad\text{credits}$$
   rather than summing shots across iterations. For a 32-iteration job with 131,072 shots per iteration,
   the total charge is exactly $1 + 10^{-6} \times 131,072 = 1.131072\text{ credits}$.

---

## 2. Mathematical foundation

### Cayley–Dickson octonion associator in two-photon interference

The octonions $\mathbb{O}$ form an 8-dimensional nonassociative normed division algebra over $\mathbb{R}$.
Left multiplication by a unit octonion $v$, denoted $L_v x = vx$, is an $8 \times 8$ real orthogonal matrix.
Because $\mathbb{O}$ is nonassociative, $L_a L_b \neq L_{ab}$ in general:
$$[L_a L_b - L_{ab}] x = a(bx) - (ab)x = [a, b, x]$$
where $[a, b, x]$ is the algebra associator.

We choose unit octonions:
$$a = \frac{e_6 + e_7}{\sqrt{2}}, \qquad b = \frac{e_5 + e_7}{\sqrt{2}}$$
Their product in `gororoba_quantum/cd_core.py` is:
$$ab = \frac{-e_0 - e_1 - e_2 + e_3}{2}$$
Both $L_a L_b$ and $L_{ab}$ preserve the 4-dimensional subspace $\operatorname{span}(e_0, e_1, e_2, e_3)$.
Restricted to this subspace, each route defines a $4 \times 4$ real orthogonal block.

### Logical mode mapping and two-click coincidence observable

Using the algebra-to-logical permutation $\sigma = \{2 \mapsto 0, 0 \mapsto 1, 3 \mapsto 2, 1 \mapsto 3\}$,
two input photons enter algebra modes 2 and 3, corresponding to logical modes 0 and 2.
Logical modes 0 and 2 are physical connected source modes on `qpu:ascella`.

By the two-photon permanent formula, for an input state $|1, 0, 1, 0\rangle$:
- Under route $L_a L_b$, photons exit in pairs $P_+ = \{03, 12\}$ with probability $1/4$ each.
- Under route $L_{ab}$, photons exit in pairs $P_- = \{02, 13\}$ with probability $1/4$ each.
- In both routes, the remaining $1/2$ probability amplitude bunches onto individual modes ($\{00, 11, 22, 33\}$),
  which threshold detectors collapse into single-click events.

The normalized two-click contrast observable is:
$$D = \frac{N(P_+) - N(P_-)}{N_{\text{focal}}}$$
where $N_{\text{focal}}$ is the total number of two-click events across all six logical pairs.

For indistinguishable photons ($V = 1.0$):
$$D(L_a L_b) = +1.0, \qquad D(L_{ab}) = -1.0$$
$$\Delta_{\text{oct}} = D(L_a L_b) - D(L_{ab}) = 2.0$$

For distinguishable photons ($V = 0.0$):
$$D(L_a L_b) = 0.0, \qquad D(L_{ab}) = 0.0, \qquad \Delta_{\text{oct}} = 0.0$$

For a partial visibility mixture $V$:
$$\Delta_{\text{oct}}(V) = \frac{2V}{V + 1.5(1 - V)}$$
At Ascella's measured HOM visibility $V = 87.48\%$, $\Delta_{\text{oct}} \approx 1.647$.

### Quaternion associative null control and in-situ closure

To provide a mechanism-destroying control, unit quaternions are chosen:
$$a_{\text{quat}} = \frac{e_1 + e_2}{\sqrt{2}}, \qquad b_{\text{quat}} = \frac{e_1 + e_3}{\sqrt{2}}$$
Because the quaternions $\mathbb{H}$ are associative, $L_a L_b = L_{ab}$ identically.
Therefore:
$$\Delta_{\text{quat}} = D(L_a L_b) - D(L_{ab}) = 0.0 \quad \text{for all } V$$
Furthermore, under both routes of the quaternion control, $D = -f(V)$.
This yields the exact in-situ closure relation:
$$C = \Delta_{\text{oct}} + 2 \operatorname{mean}(D_{\text{quat}}) = 0.0 \quad \text{for all } V$$
Any departure from $C = 0$ indicates route-dependent instrumental bias or calibration distortion.

---

## 3. Predecessor conditioning and counterbalanced schedule

### Predecessor interventions

Predecessor settings apply nominal phase requests across the 28 phase shifters of the template circuit,
with all 6 beam splitters set to $\theta = 0$ (direct transmission):
1. **$P_{\text{cold}}$ (Quiescent baseline):** All $\phi = 0.0 \implies U = I_{12}$.
2. **$P_{\text{wrapped}}$ (Optical twin):** All $\phi = 2\pi \implies U = I_{12}$ ($\|U(2\pi) - U(0)\| < 10^{-12}$).
3. **$P_{\text{hot}}$ (High phase request):** All $\phi = \pi \implies U = -I_{12}$.

### Paired predecessor-target sequencing

Following the protocol in `docs/runbooks/evidence-closure.md`:
> *"In every paired invocation the unchanged target is the second iteration."*

The job executes 16 pairs (32 iterations total), structured for exact algebraic quadratic drift cancellation
and uniform Cold-baseline anchor reconstruction across the entire run:
- Iteration $2p$: Predecessor setting (runs for 524,288 shots, applying commanded phase request).
- Iteration $2p + 1$: Fixed Target setting (runs for 524,288 shots immediately following predecessor).

| Pair | Predecessor | Target Block | Target Route | Block Role |
|:---:|:---:|:---:|:---:|:---|
| 0 | Hot ($\pi$) | Associator | $L_{ab}$ | Active Intervention (Hot Carryover) |
| 1 | Cold ($0$) | Associator | $L_a L_b$ | **Cold Baseline Anchor 1** |
| 2 | Wrapped ($2\pi$) | Associator | $L_a L_b$ | Active Intervention (Wrapped Optical Twin) |
| 3 | Cold ($0$) | Associator | $L_{ab}$ | **Cold Baseline Anchor 2** |
| 4 | Hot ($\pi$) | Associator | $L_a L_b$ | Active Intervention (Hot Carryover Replicate) |
| 5 | Cold ($0$) | Associator | $L_{ab}$ | **Cold Baseline Anchor 3** |
| 6 | Wrapped ($2\pi$) | Associator | $L_{ab}$ | Active Intervention (Wrapped Replicate) |
| 7 | Cold ($0$) | Associator | $L_a L_b$ | **Cold Baseline Anchor 4** |
| 8 | Hot ($\pi$) | Control | $L_{ab}$ | Active Intervention (Control Hot) |
| 9 | Cold ($0$) | Control | $L_a L_b$ | **Cold Baseline Anchor 5** |
| 10 | Wrapped ($2\pi$) | Control | $L_a L_b$ | Active Intervention (Control Wrapped) |
| 11 | Cold ($0$) | Control | $L_{ab}$ | **Cold Baseline Anchor 6** |
| 12 | Hot ($\pi$) | Control | $L_a L_b$ | Active Intervention (Control Hot Replicate) |
| 13 | Cold ($0$) | Control | $L_{ab}$ | **Cold Baseline Anchor 7** |
| 14 | Wrapped ($2\pi$) | Control | $L_{ab}$ | Active Intervention (Control Wrapped Replicate) |
| 15 | Cold ($0$) | Control | $L_a L_b$ | **Cold Baseline Anchor 8** |

### Algebraic non-linear drift cancellation & Joint WLS Model

1. **Pooled Thue–Morse moment cancellation vs Condition-Specific Carryovers:**
   Within each block, target routes $L_a L_b$ and $L_{ab}$ are assigned according to the Thue–Morse sequence:
   - For Block 1 (Associator, Pairs 0..7):
     $$\sum_{t \in L_a L_b} t = 1 + 2 + 4 + 7 = 14, \qquad \sum_{t \in L_{ab}} t = 0 + 3 + 5 + 6 = 14$$
     $$\sum_{t \in L_a L_b} t^2 = 1 + 4 + 16 + 49 = 70, \qquad \sum_{t \in L_{ab}} t^2 = 0 + 9 + 25 + 36 = 70$$
   - For Block 2 (Quaternion Control, Pairs 8..15):
     $$\sum_{t \in L_a L_b} t = 9 + 10 + 12 + 15 = 46, \qquad \sum_{t \in L_{ab}} t = 8 + 11 + 13 + 14 = 46$$
     $$\sum_{t \in L_a L_b} t^2 = 81 + 100 + 144 + 225 = 550, \qquad \sum_{t \in L_{ab}} t^2 = 64 + 121 + 169 + 196 = 550$$
   While the pooled contrast across all conditions eliminates quadratic polynomial drift to zero,
   an adversarial review proved that condition-specific naive differences retain linear and quadratic
   drift contamination ($4\beta_1 + 8\beta_2$ for Hot vs Cold).

2. **Preregistered Joint Weighted Least Squares (WLS) Model:**
   To eliminate condition-specific drift without circularity or unequal-yield distortion, the primary analysis
   fits a preregistered joint WLS regression across all 16 target observations:
   $$y_i = D_i = \frac{N_+(i) - N_-(i)}{N_{\text{focal}}(i)}$$
   $$\mathbf{y} = X \boldsymbol{\theta} + \boldsymbol{\epsilon}, \qquad W = \operatorname{diag}\left(\frac{N_{\text{focal}}(i)}{\max(1 - D_i^2, 0.05)}\right)$$
   where the design matrix $X$ ($16 \times 8$) simultaneously identifies:
   - $\beta_0$: Intercept (Cold Associator $L_{ab}$ baseline)
   - $\Delta_{\text{assoc}}$: Associator route difference ($L_a L_b - L_{ab}$)
   - $\alpha_{\text{ctrl}}$: Control block offset
   - $\Delta_{\text{ctrl}}$: Control route difference ($L_a L_b - L_{ab}$)
   - $\gamma_{\text{hot}}$: Hot predecessor carryover shift
   - $\gamma_{\text{wrapped}}$: Wrapped predecessor carryover shift
   - $\tau_1, \tau_2$: Linear and quadratic polynomial drift coefficients along elapsed physical time.

   The joint model has full column rank ($8/8$, condition number $\approx 25.6$), propagates the complete parameter
   covariance $\Sigma = \max(1, \text{RSS}/\nu)(X^T W X)^{-1}$, and provides exact standard errors for all parameters.

---

## 4. Preregistered decision rules and endpoints

1. **Octonion Associator Signal Detection:**
   $$\hat{\Delta}_{\text{assoc}} > 0.5 \quad \text{and} \quad \text{CI}_{95,\text{lower}} > 0.5$$
   Confirms two-photon interference visibility on the compiled mesh at 95% confidence.

2. **Quaternion Null Control Admission:**
   $$|\hat{\Delta}_{\text{ctrl}}| < 0.05 \quad \text{and} \quad \text{CI}_{95} \subset [-0.05, 0.05]$$
   Confirms that associative multiplication produces zero contrast within mutation tolerance.

3. **In-situ Visibility Closure Admission:**
   $$\hat{C} = \hat{\Delta}_{\text{assoc}} + 2(\hat{\beta}_0 + \hat{\alpha}_{\text{ctrl}} + 0.5\hat{\Delta}_{\text{ctrl}}) = 0.0$$
   Standard error is propagated through the full joint covariance matrix $\operatorname{SE}(\hat{C}) = \sqrt{\mathbf{c}^T \Sigma \mathbf{c}}$.
   Admitted if $|\hat{C}| < 0.05$ and $0 \in \text{CI}_{95}$ (consistent with zero within 95% confidence).

4. **Predecessor Carryover Equivalence (TOST):**
   Evaluates Two One-Sided Tests (TOST) against equivalence margin $\delta = 0.020$:
   - **`EQUIVALENT`**: The entire 95% two-sided confidence interval falls strictly inside $[-\delta, +\delta]$.
   - **`SIGNIFICANT_CARRYOVER`**: The point estimate exceeds $\delta$ and is statistically significant ($p < 0.05$).
   - **`INCONCLUSIVE`**: The point estimate is below $\delta$ but the confidence interval extends beyond $\pm\delta$ (insufficient shots/precision).

5. **Abrupt Step-Change / Shock Quarantine:**
   Standardized residuals against nominal shot-noise variance are evaluated:
   $$z_i = \frac{|y_i - \hat{y}_i|}{\sigma_{\text{shot},i}}$$
   If $\max_i z_i > 3.5$, an abrupt hardware shock or laser disruption is detected, and the run is quarantined
   as `QUARANTINED_ABRUPT_STEP`.

6. **Spatial Sentinel Leakage:**
   Tally clicks in modes 4..11, separated by predecessor and target roles:
   $$\hat{L}_{\text{role}}(\text{cond}) = \frac{N_{\text{sentinel}}(\text{role}, \text{cond})}{N_{\text{total}}(\text{role}, \text{cond})}, \qquad \operatorname{SE} = \sqrt{\frac{\hat{L}(1 - \hat{L})}{N_{\text{total}}}}$$
   Reported with binomial standard errors and 95% confidence intervals.

---

## 5. Execution parameters and resource budget

- **Processor:** `qpu:ascella` (12 modes, 132 Rx couplers, 126 phase shifters, 12 threshold detectors).
- **Template circuit:** Fixed 34-parameter triangular mesh on modes 0..3; identity on modes 4..11.
- **Iterations:** 32 (16 paired predecessor-target trials).
- **Samples per iteration:** 8,192 samples ($N_{\text{total}} = 262,144$ samples).
- **Shots per iteration:** 655,360 shots ($80 \times 8,192$ shots; aggregate cap $20,971,520$ shots).
- **Bounded Timing Model:**
  $$T(N) = T_{\text{overhead}} + N \times t_{\text{iter}}$$
  With $T_{\text{overhead}} \approx 30\,\text{s}$ and $t_{\text{iter}} \approx 3.0\,\text{s}$, the bounded duration
  range across retained rehearsals is $[93\,\text{s}, 186\,\text{s}]$, with platform execution ceiling of **300 seconds**.
- **Credit ceiling:** Under the matching preflight platform tariff ($1 + 10^{-6} \times \max_i(\text{shots}_i)$),
  the ceiling is exactly **1.655360 credits**.
- **Execution status:** Completed on `qpu:ascella` (Job `e13e5ed0-ea33-4d13-85e0-52115e8268d8`).
  Physical execution duration: 104 seconds; physical laser pulses: 16,127,893 shots;
  samples collected: 262,144 two-click events; credits charged: exactly 1.655360 credits.
  All receipts and raw records retained in `results/quandela/cases/ascella_associator_predecessor/job-00/`.
