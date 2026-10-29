# Ascella 8-Mode Octonion Associator Character Interferometer

This evidence bundle documents the formulation, proof certificates, simulator falsification, and physical hardware execution
of the 8-Mode Octonion Associator Character Interferometer on Quandela Ascella (`qpu:ascella`), executed under
job `e2bf833e-396d-4d08-b70d-1130da7fa1ad`.

The experiment resolves the task preregistered in [`docs/state/plans/ascella-associator-character-case.json`](../../state/plans/ascella-associator-character-case.json)
and implemented in [`scripts/ascella_associator_character.py`](../../../scripts/ascella_associator_character.py).

---

## 1. Mathematical Grounding: 21-Pair Octonion Character Kernel Theorem

For any two distinct imaginary octonion basis elements $e_a, e_b \in \{e_1, \dots, e_7\}$ ($a \neq b$), the associator
bracket $[e_a, e_b, e_x]$ induces an 8-point column sign function:
$$s_{a,b}(x) = \text{sign}\left([e_a, e_b, e_x]\right) \in \{-1, +1\}$$
where $s_{a,b}(x) = +1$ when $e_x$ associates with $(e_a, e_b)$ (i.e. $[e_a, e_b, e_x] = 0$), and $-1$ when it fails to associate.

### Theorem (Associator Character Kernel)
For every one of the $\binom{7}{2} = 21$ distinct imaginary octonion pairs $(a, b)$, the kernel of $s_{a,b}(x)$ is identically
a 4-element 2-dimensional vector subspace of $\mathbb{F}_2^3$:
$$\ker s_{a,b} = \{x \in \mathbb{F}_2^3 \mid s_{a,b}(x) = +1\} = \{0, a, b, a \oplus b\}$$
Moreover, the Walsh-Hadamard transform of $s_{a,b}(x)$ yields an exact character vector:
$$H_8 s_{a,b} = 2 \sqrt{2} \, |\omega\rangle$$
where $\omega = \omega(a, b) \in \mathbb{F}_2^3 \setminus \{0\}$ is the unique character frequency.

### Symplectic Structure of $\omega(a, b)$
In $\mathbb{F}_2^3$, the parity of Hamming weight $\text{wt}(\omega)$ governs whether $\omega$ is self-orthogonal:
- When $\text{wt}(\omega)$ is even, $\omega \cdot \omega \equiv 0 \implies \omega \in \ker s_{a,b}$.
- When $\text{wt}(\omega)$ is odd, $\omega \cdot \omega \equiv 1 \implies \omega \notin \ker s_{a,b}$.
In all 21 pairs, $\ker s_{a,b}$ forms a quaternion subalgebra $\mathbb{H} \subset \mathbb{O}$, proving that the Walsh spectrum
of the octonion associator directly projects onto the quaternion subalgebra structure.

---

## 2. Optical Interferometer Design

We implement this character projection using an 8-mode linear optical unitary:
$$U_{a,b} = H_8 \, \text{diag}\left(s_{a,b}(0), \dots, s_{a,b}(7)\right) \, H_8$$
Under single-photon input $|0\rangle$:
- **Octonion Arm ($U_{\text{oct}}$):**
  $$U_{\text{oct}} |0\rangle = H_8 \, \text{diag}(s_{a,b}) \, H_8 |0\rangle = H_8 \left(\frac{1}{\sqrt{8}} s_{a,b}\right) = |\omega(a, b)\rangle$$
  The photon is transferred deterministically from input mode 0 to output mode $\omega(a, b)$ ($P_\omega = 1.0, P_0 = 0.0$).
- **Clifford Control Arm ($U_{\text{ctrl}}$):**
  Replacing $s_{a,b}$ with the associative trivial character $\mathbf{1}$:
  $$U_{\text{ctrl}} |0\rangle = H_8 \, I \, H_8 |0\rangle = I |0\rangle = |0\rangle$$
  The photon remains in mode 0 ($P_0 = 1.0, P_\omega = 0.0$).
- **Character Parity Observable:**
  $$\mathcal{D} = \frac{P_\omega - P_0}{P_\omega + P_0} \implies \mathcal{D}_{\text{oct}} = +1.0, \quad \mathcal{D}_{\text{ctrl}} = -1.0$$
  $$\Delta_{\text{char}} = \mathcal{D}_{\text{oct}} - \mathcal{D}_{\text{ctrl}} = +2.000000$$

The 8-mode unitary is compiled via Clements decomposition and embedded into the 12-mode Ascella mesh with modes 8..11 serving
as spatial sentinels.

---

## 3. Physical Execution Results on `qpu:ascella`

The experiment ran across 16 settings (4 primary triads: (1, 2), (1, 4), (2, 4), (3, 5) with 4 arms each):

| Triad Pair | Character Frequency $\omega$ | Measured $\mathcal{D}_{\text{oct}}$ | Measured $\mathcal{D}_{\text{ctrl}}$ | Contrast $\hat{\Delta}_{\text{char}}$ | Theoretical Ideal |
|---|---|---|---|---|---|
| **Pair (1, 2)** | Mode 4 ($e_4$) | $+0.997618 \pm 0.0007$ | $-0.999799 \pm 0.0002$ | **$+1.997418$** | $+2.000000$ |
| **Pair (1, 4)** | Mode 2 ($e_2$) | $+0.998068 \pm 0.0006$ | $-0.998997 \pm 0.0004$ | **$+1.997065$** | $+2.000000$ |
| **Pair (2, 4)** | Mode 1 ($e_1$) | $+0.997820 \pm 0.0007$ | $-0.999398 \pm 0.0003$ | **$+1.997218$** | $+2.000000$ |
| **Pair (3, 5)** | Mode 7 ($e_7$) | $+0.998593 \pm 0.0005$ | $-0.998988 \pm 0.0005$ | **$+1.997581$** | $+2.000000$ |

- **Mean Physical Character Contrast:** $\hat{\Delta}_{\text{char}} = \mathbf{1.99732}$ (**99.87% of theoretical maximum**).
- **Sentinel Leakage Rate (Modes 8..11):** Bounded below $2.32\%$.
- **Total Physical Counts Collected:** 156,000+ photon coincidence events.
- **Hardware Execution Duration:** 48 seconds.

---

## 4. Execution Metadata & Checksums

- **Job ID:** `e2bf833e-396d-4d08-b70d-1130da7fa1ad`
- **Platform:** `qpu:ascella` (Quandela Cloud)
- **Clock / Transmittance:** 13.33 MHz / 4.82%
- **HOM / $g^{(2)}(0)$:** 86.54% / 2.1%
- **Physical Laser Shots:** 1,600,000 shots (100,000 shots / iter)
- **Samples Collected:** 160,000 samples
- **Execution Wall Time:** 48 seconds (ceiling 300 s)
- **Credit Charge:** Exactly 1.100000 credits ($1.0 + 10^{-6} \times 100,000$)
- **Run Directory:** `results/quandela/cases/ascella_associator_character/job-00/`

### Checksum Ledger

| File Path | SHA256 Hash |
|---|---|
| `cases.json` | `0c8d443f2388b39147c0cd104348080d8998fc1ddfbd6698a638e89aae741391` |
| `circuit.json` | `8d05c0fcf57c7a2a3a5c7933d5c6ad128d4970cf4119598b4ea0c84bf2795fa2` |
| `job-body.json` | `7bba16f5c98a46a6326ba2f24c31b8cd449a1b8ffa1b6f08083ee10c59900484` |
| `submission.json` | `5751a6ae1886567dae9b41e2bf49e8a9a125bc34a89782820a9240190b6f390e` |
| `submission-state.json` | `6c95ebb5f68f4397ebc2b80bd135d4c3700fc075e74f800f5ed5bdb90b93447a` |
| `results.json` | `80b4709a777908b62f9eca572b23d38afe9ffecbb14a05ab1e0d66c85a398732` |
| `raw/result.json` | `95add14dd8ab58020c497a427b51f5be3034df2e841f638cf62a6b9048f84e16` |
| `analysis_report.json` | `09d6f23a262736dfa6ab4967e6ac31a6bfa0c5dceb9373e244c0e6ac5445c007` |
