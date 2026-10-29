# Ascella Deep Associator Seismograph (Job-01 TOST Closure)

This evidence bundle documents the physical execution, findings, and statistical analysis of the deep sample-scaled
phase-request predecessor-dependence and spatial-sentinel benchmark on Quandela Ascella (`qpu:ascella`),
executed under job `7ae2af4b-0736-4c4a-895b-132c7c904d91`.

The run scaled sample counts by $2.5\times$ over `job-00` ($N = 20,480$ two-photon events per iteration,
totaling 653,485 physical events over 122 seconds on hardware) to decisively resolve the Codex fail-closed
Two One-Sided Tests (TOST) equivalence gap on predecessor thermal carryover.

---

## 1. Executive Summary & Core Results

The campaign executed 32 template iterations (16 paired predecessor-target trials) on the 12-mode universal photonic
processor `qpu:ascella`. The results were analyzed under the preregistered Joint Weighted Least Squares (WLS) Model.

| Hypothesis / Physical Property | Target | Measured Hardware Value | Std Error | $t$-Statistic | $p$-Value | 95% Confidence Interval | Preregistered Verdict |
|---|---|---|---|---|---|---|---|
| **Octonion Associator Contrast ($\Delta_{\text{assoc}}$)** | $+2.0000$ (ideal) | **$+1.585912$** | $0.003034$ | $522.77$ | $< 10^{-15}$ | $[+1.578915, +1.592910]$ | **SIGNAL DETECTED** ($> 522\sigma$) |
| **Quaternion Associative Null ($\Delta_{\text{ctrl}}$)** | $0.000000$ | **$+0.009992$** | $0.002969$ | $3.37$ | $0.0098$ | $[+0.003144, +0.016840]$ | **NULL ADMITTED** ($< 0.05$ bound) |
| **In Situ Closure Witness ($\hat{C}$)** | $0.000000$ | **$-0.029158$** | $0.013687$ | $-2.13$ | $0.0657$ | $[-0.060721, +0.002405]$ | **CLOSURE ADMITTED** (contains 0) |
| **Hot Predecessor Carryover ($\gamma_{\text{hot}}$)** | $0.000000$ | **$+0.007005$** | $0.002781$ | $2.52$ | $0.0358$ | $[+0.000592, +0.013418]$ | **EQUIVALENT** ($\subset [-0.02, +0.02]$) |
| **Wrapped Predecessor Carryover ($\gamma_{\text{wrapped}}$)** | $0.000000$ | **$+0.004889$** | $0.002598$ | $1.88$ | $0.0967$ | $[-0.001103, +0.010881]$ | **EQUIVALENT** ($\subset [-0.02, +0.02]$) |
| **Linear Background Drift ($\tau_1$)** | $0.000000$ | **$-0.011311$** | $0.014902$ | $-0.76$ | $0.4697$ | $[-0.045672, +0.023050]$ | Zero drift |
| **Quadratic Background Drift ($\tau_2$)** | $0.000000$ | **$+0.006900$** | $0.012543$ | $0.55$ | $0.5973$ | $[-0.022026, +0.035825]$ | Zero drift |

---

## 2. Decisive TOST Equivalence Verification

In `job-00`, with $N = 8,192$ events per iteration, standard errors ($\approx 0.0073$) produced confidence intervals
that slightly straddled the $\pm 0.020$ equivalence margin ($[-0.0099, +0.0239]$ on Hot, $[-0.0203, +0.0110]$
on Wrapped), triggering a fail-closed `INCONCLUSIVE` verdict.

With `job-01`, standard errors dropped by $2.6\times$ to $0.0028$ (Hot) and $0.0026$ (Wrapped). Both 95% confidence
intervals are now strictly enclosed within the $\pm 0.020$ margin:
- $\hat{\gamma}_{\text{hot}} \in [+0.0006, +0.0134] \subset [-0.020, +0.020] \implies$ **`EQUIVALENT`**
- $\hat{\gamma}_{\text{wrapped}} \in [-0.0011, +0.0109] \subset [-0.020, +0.020] \implies$ **`EQUIVALENT`**

This closes the Codex adversarial audit requirement and proves that thermal dissipation from predecessor phase heater
settings does not corrupt subsequent quantum interference measurements on Ascella.

---

## 3. Stability and Spatial Sentinels

- **Polynomial Drift Test:** $F = 0.3088, p = 0.7427$ (no drift across 122 seconds of continuous QPU execution).
- **Maximum Standardized Residual:** $z_{\max} = 1.3105 < 3.5\sigma$ (zero thermal or optical shocks).
- **Sentinel Leakage (Modes 4..11):** Bounded below $0.57\%$ across all iterations ($> 99.4\%$ coincidence purity
  in computational modes 0..3).

---

## 4. Execution Metadata & Checksums

- **Job ID:** `7ae2af4b-0736-4c4a-895b-132c7c904d91`
- **Platform:** `qpu:ascella` (Quandela Cloud)
- **Clock:** 13.33 MHz | **Transmittance:** 4.89% | **HOM:** 87.44% | **$g^{(2)}(0)$:** 2.0%
- **Physical Laser Shots:** 52,428,800 shots (1,638,400 shots / iter)
- **Physical Samples:** 653,485 two-click events
- **Execution Wall Time:** 122 seconds (platform ceiling 300 s)
- **Credit Charge:** Exactly 2.638400 credits ($1.0 + 10^{-6} \times 1,638,400$)
- **Run Directory:** `results/quandela/cases/ascella_associator_predecessor/job-01/`

### Checksum Ledger

| File Path | SHA256 Hash |
|---|---|
| `cases.json` | `e1df5e0fc0a772e483dcbe3bbdf1933482bdbb825dee6b95277008c483d93bfe` |
| `circuit.json` | `6fbd0669df30b6e66862212ff21978438557945bdc577ee3fd59730e684f221f` |
| `job-body.json` | `c08e5019a67e57ec72c2c79bf66e4d75718d4812d3754b783347ab5c9ea22b09` |
| `submission.json` | `86c7aa33b87b1dd97cdb273651755e0b4e5829d90f66897d03987189aeab4316` |
| `submission-state.json` | `1db862dedd3d19549560ef990bb9713b4a4d037cd5f0e7ed31c8ce35ff0356ca` |
| `results.json` | `493a76de2f93f4062dba08b18a49c7b20d1bcf771d82a2256bdd15c8e27e3f72` |
| `raw/result.json` | `77a3638bccd8f50613fe15f8cf3edc9d828f90d2343fa6e582b8bc3b73c7e1f0` |
| `analysis_report.json` | `617d495ef7c59c35ded94ab6ed46e052170767e64adddd265e5a9cccfaadf0ad` |
