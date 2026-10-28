# Pais Superforce and patent claims: decomposition, falsifiers and the QPU-testable mechanism

Salvatore Cezar Pais's central claim is the Superforce: the Planck force c^4/G, read as "the ruling force of
unification" that "gives birth to Energy Density, hence generates Matter" and that a material's permittivity and
permeability can engineer (OSF preprints yh84c, April 2023, and 9kebt, July 2023). The section
[The Superforce](#the-superforce) decomposes it; the patents that follow rest on a separate equation and are
decomposed after it.

The three granted Navy patents of Salvatore Cezar Pais (2018-2019) rest on one
equation, the magnitude of a charged rotor's Poynting vector, read as a
radiated power and then as a lever on the quantum vacuum. Standard
electrodynamics, QED and general relativity refute the field-generator,
inertial-mass and gravitational-wave mechanisms with the patents' own inputs,
and the Navy's three-year, $508,000 test of the "Pais effect" ended in
September 2019 with the statement that the effect "could not be proven". The
superconductor and fusion filings carry no measurement and are not decomposed
here. A QPU cannot test inertia, gravitational waves or a field generator. It
can test the extraction claim inside the mechanism: an operation confined to
one region, acting on a ground state, cannot lower that region's energy unless
a measurement record from elsewhere steers it, and then by less than the
measurement injected. The two-qubit quantum energy teleportation (QET)
protocol measures that boundary on a device. [P] marks a source statement, [I]
a repository deduction, [E] a value the scripts compute. Sources and retrieval
hashes: [pais-patent-web-sources.md](../papers/pais-patent-web-sources.md).

## The Superforce

[pais-superforce-preprints.md](../papers/pais-superforce-preprints.md) takes both preprints statement by
statement; [scripts/pais_superforce_bounds.py](../../../scripts/pais_superforce_bounds.py) computes every number
below from CODATA constants and the cited measurements, raising when a stated inequality fails.

- **Unification is an identity of the unit definitions.** [I] The preprints' two equalities, (1/alpha) F_EM =
  c^4/G and G m_P^2/L_P^2 = c^4/G at the Planck length, are both hbar c/L_P^2, which is c^4/G by the definition of
  L_P and m_P. The charge cancels from the first, so it contains no electromagnetic or strong input.
- **The measured strong force falls 53 times short.** [E] The premise F_SN/F_EM = 1/alpha is alpha_s = 1. The
  measured alpha_s(m_Z) = 0.1180 runs to alpha_s(M_Pl) = 0.0189 at three loops (0.0191 at one loop), so the strong
  force at L_P is c^4/G divided by 52.9.
- **The Schrodinger step inserts what it finds.** [E] hbar^2/(2 m L^3) reaches c^4/(2G) only at the Planck mass and
  length; an electron at its reduced Compton wavelength gives 1.75e-45 of it, which is 8.8e-46 of c^4/G (the value
  [persona-corpus-claims-falsification.md](persona-corpus-claims-falsification.md#re-derivation-of-the-earlier-notes)
  recomputes; this line earlier printed the c^4/G ratio against the c^4/(2G) referent).
- **The cosmic "coincidence" is the Friedmann equation.** [E] Critical density inside the Hubble radius gives
  M_H c^2/R_H = c^4/(2G) for every Hubble rate; the measured flatness Omega_K = 0.001 +- 0.002 is the only content
  of the July version's Eq. 1.
- **The proton pressure is QCD, 39 decades down.** [E] Pais's 1e35 Pa is 1.66 times m_p c^2 over the proton volume.
  Times the proton's cross-section it is 2.2e5 N, 1.8e-39 of c^4/G.
- **Engineering by permittivity is refuted three ways.** [I] Writing c/n into the coupling makes active
  gravitational mass scale as n^4.
  - [E] Kreuzer's 5e-5 null on fluorine against bromine would then require the two materials to match in index to
    1.25e-5, and the lunar 4e-12 null on aluminum against iron to 1e-12.
  - [E] c/n would also be the invariant speed in water, yet electrons above 0.254 MeV (the index of water at 400 nm) outrun it and emit Cherenkov
    light.
- **The constant is a ceiling, not an agent.** [I] c^4/G is 4 times Gibbons' maximal tension c^4/(4G) of
  classical GR. Its independence of hbar marks it as classical.

No quantum processor measures G, so every Superforce falsifier is a measured coupling or a gravitational null
already in hand. The vacuum-energy part of the program, local energy extraction, is what the QET ladder below
tests on hardware.

## The record

- [P] US 10,135,366 B2 (electromagnetic field generator), US 10,144,532 B2
  (craft using an inertial mass reduction device), US 10,322,827 B2 (high
  frequency gravitational wave generator), US 2019/0058105 A1
  (piezoelectricity-induced room-temperature superconductor) and
  US 2019/0295733 A1 (plasma compression fusion device). The field-generator
  patent prints Eq. 1 below with gamma^2, the craft patent prints it without
  gamma^2 as the non-relativistic form, and the gravitational-wave patent
  carries only the vibration form of Eq. 2; none reports a measurement.
  Equation locators are in the per-patent notes linked from
  [pais-patent-web-sources.md](../papers/pais-patent-web-sources.md).
- [P] The craft application was rejected and then granted after the Naval
  Aviation Enterprise chief technology officer attested operability and
  cited Chinese research.
- [P] NAWCAD tested the High Energy Electromagnetic Field Generator from
  October 2016 to September 2019 for $508,000, about $462,000 of it salaries,
  and concluded that the "Pais Effect" could not be proven.
- [P] The craft patent's only experimental support, Eq. 5, is the Hayasaka
  and Takeuchi gyroscope weight loss (PRL 63, 2701, 1989). Faller et al.
  (PRL 64, 825), Quinn and Picard (Nature 343, 732) and Nitschke and Wilmarth
  (PRL 64, 2115) reported nulls in 1990, and Luo et al. (PRD 65, 042005, 2002)
  a free-fall null.

## Decomposition of the equations

[scripts/pais_claim_bounds.py](../../../scripts/pais_claim_bounds.py) computes
every number in this section from the patents' inputs and CODATA constants
(`scipy.constants`), raising when a stated inequality fails;
[its test](../../../tests/scripts/test_pais_claim_bounds.py) runs in the
`tests` check.

**Eq. 1 is a circulating flux, not a radiated power.** [P] The patents write
`S_max = f_G gamma^2 (sigma^2/eps0)[R_r omega + R_v nu + v_R]` and evaluate it
at sigma = 50000 C/m^2, R = 2 m, 30000 RPM to about 1e24 W/m^2. [E] With
f_G = 1 the value is 1.77e24 W/m^2, and a steady rotating sheet's
`E B / mu0 = sigma^2 v / (4 eps0)` is exactly Eq. 1 over four, so Eq. 1 is the
magnitude of the static field's `E x B / mu0`. [I] An axisymmetric charge
spinning at constant rate has time-independent charge and current
densities, so its fields are static, `div S = -du/dt = 0`, and it radiates
nothing. Eq. 1 is a momentum density times c^2. [E] An accelerating spin
radiates only as a magnetic dipole through the moment's second derivative
(a charged spherical shell has `m = Q R^2 omega / 3` and no electric dipole):
spinning the worked example up to 30000 RPM in 1 s radiates of order 2.7e-13 W, the scale
`mu0 (Q R^2 omega / (3 tau^2))^2 / (6 pi c^3)`. The power depends on the ramp: a uniform ramp has `m'' = 0`
between its ends, and a sin^2 ramp averages 3.3e-12 W with a peak of 6.7e-12 W, so every smooth one-second
spin-up stays below 1e-11 W.

**Eq. 2 integrates an acceleration that a vibration cannot sustain.** [P] The
vibrating case is `S_max = f_G gamma^2 (sigma^2/eps0) R_v nu^2 t_op` (the craft
and gravitational-wave patents print it without gamma^2), and the
gravitational-wave patent adds `R_v nu^3 t_op^2`. [I] `R_v nu^2 t_op` is
acceleration times operating time, a speed growing without bound, while a
vibration of amplitude R_v keeps `|v| <= 2 pi nu R_v`. [E] At 1 um, 1 GHz and
t_op = 1 s the implied speed exceeds the bounded one by 1.6e8. A charged sheet
vibrating in its own plane (a tangential surface current `sigma v`) radiates
`sigma^2 v^2 / (4 eps0 c)` per face, the circulating flux times v/c; at the
patents' own vacuum field limit (sigma = eps0 x 1e9 V/m) Eq. 2 exceeds that
radiated flux by 3.0e13. A spherically symmetric breathing shell, the
piezoelectric mode of claim 1, radiates nothing, because Gauss's law fixes
its exterior field.

**The input charge exceeds the patents' own limit.** [E] sigma = 50000 C/m^2
gives a surface field of 5.6e15 V/m, 5.6e6 times the 1e9 V/m vacuum limit the
same patent states, and an electrostatic pressure of 1.4e20 Pa. The largest
charge the stated limit admits is 8.9e-3 C/m^2, for which Eq. 1 gives
5.6e10 W/m^2. The fusion filing's dynamic fusors hold "at least one Coulomb";
1 C on a 2 m sphere gives 2.2e9 V/m, and staying under 1e9 V/m needs a radius of
at least 3.0 m.

**Every Maxwell field adds positive gravitating mass.** [E] For any E and B,
`u^2 - |S/c|^2 = (eps0/2)^2 [(E^2 - c^2 B^2)^2 + 4 c^2 (E.B)^2]` (relative
residual 2.0e-12 on a deterministic lattice of fields), so `u >= |S|/c`. [I]
The Maxwell stress tensor is traceless, so the active gravitational mass
density `(rho c^2 + p_1 + p_2 + p_3)/c^2` equals `2u/c^2 >= 0`: no classical
electromagnetic configuration produces the "negative pressure (hence
repulsive gravity)" the craft patent claims. [E] The worked example's exterior
field stores 1.4e22 J, which adds 1.6e5 kg of inertia to the craft.

**The vacuum barely notices the claimed fields.** [E] The Schwinger field
`m_e^2 c^3/(e hbar)` is 1.32e18 V/m. At the example's 5.6e15 V/m the leading
pair-production rate is 10^-268 per m^3 per s, and the Euler-Heisenberg
correction to the field energy density is 2.8e-9 of it; at the patents' 1e9
V/m limit that correction is 8.8e-23. [I] These ratios bound a standing-wave
cavity field as well as a static one, because both rest on E/E_S; Schwinger
1951 adds that a single plane wave, whose two invariants vanish, produces no
pairs at any intensity. Eq. 3's `2 gamma (dm/dt) c^2 = S_max A_S` assumes all
the flux converts to pairs; the rate above makes the conversion zero to
every printed digit.

**Eq. 4 equates a field pressure with a regulator.** [P] The craft patent sets
`S_max/c = hbar nu^4/(8 pi^2 c^3)`, the zero-point energy density integrated to
a cutoff. [E] At 1e24 W/m^2 the implied angular cutoff is 1.6e19 s^-1, a
10.6 keV photon. [I] The cutoff-integrated zero-point density depends on the
regulator and is not Lorentz invariant; the observable vacuum quantities are
renormalized differences such as Casimir energies, and the patent derives no
coupling between a classical flux and that density.

**Negative energy: 42 orders short in free space, sub-atomic plates in a
cavity.** [P] Ford and Roman bound the Lorentzian-sampled energy density of the
free massless scalar in Minkowski space below by `-3 hbar/(32 pi^2 c^3 t0^4)`
([gr-qc/9607003](../papers/gr-qc-9607003.md)); the electromagnetic bound scales
the same way. [E] Shedding 10 kg from 10 m^3 needs -9.0e16 J/m^3; sampled over
1 ns (the patents' GHz drive) the free-field bound is -3.7e-26 J/m^3, 42.4
orders short, and over 1 s 78.4 orders short. [I] The craft is a resonant
cavity, and a boundary evades the free-field bound, so the boundary case asks
which ideal parallel plates store that density: [E] the Casimir density
`-pi^2 hbar c/(720 a^4)` reaches -9.0e16 J/m^3 at a gap of 8.3 pm, 0.16 Bohr
radii, where no conductor exists.

**The gravitational-wave arithmetic is consistent; its inputs are not.** [P]
Ejlli et al. write the graviton-photon mixing as `kappa B/2` with
`kappa^2 = 16 pi G` in rationalized Lorentz-Heaviside units (Appendix A,
[s10052-019-7542-5.md](../papers/s10052-019-7542-5.md)). [I] The conversion
probability over length L, `4 pi G B^2 L^2/(mu0 c^4)` in SI, follows from their
Eqs. A.6 and A.7; the paper prints no SI form. [E] A 10 T field
over 1 m converts 8.3e-36. The patent's B0 = 1e10 T is 2.27 times the QED
critical field `m_e^2 c^2/(e hbar)` = 4.41e9 T, stores 4.0e25 J/m^3 (a mass
density of 4.4e8 kg/m^3), and its input flux of 1e33 W/m^2 is 0.43 of the
Schwinger intensity `c eps0 E_S^2/2`. With those inputs the claimed 1e10 W
follows from a 1.1 mm path over 1 m^2, so the conversion formula is not where
the claim fails. [I] The SI form carries the 1/mu0 the patent says JASON
omits; whether JASON printed natural units was not checked, because the
report was not retrieved. The weak-field mixing formula is itself unqualified
above the critical field. The patent's Eq. 3, `E_T = m R_v^2 Omega^2
exp(2 Omega t)` under "negative damping", grows without an energy source.

**Not decomposed.** The superconductor filing describes no resistance or
magnetization measurement, and the fusion filing's compression and
confinement figures were not checked against a Lawson analysis; both are
evidence gaps rather than refutations.

## What a QPU can and cannot test

[I] Every relativistic or astronomical phase on these devices sits six or more
orders of magnitude below the smallest measured instability
([relativistic-metrology-scale.md](relativistic-metrology-scale.md)), and the
transmon's gate-level drive offers no charged rotor, cavity wall or field
output. No acquisition on any provider tests inertial mass, gravitational-wave
emission or the field generator; a run framed that way spends quota on a
question the analytic bounds above already answer.

[I] Quantum fields do carry negative energy density: squeezed vacuum and
moving boundaries produce it without any measurement
([vacuum_field_run_opportunities.md](../vacuum_field_run_opportunities.md)),
quantum inequalities bound it and positive density nearby compensates it.
What a drive cannot do is extract energy: a ground state is passive, so no
operation lowers its total energy, and an operation confined to region B
cannot lower B's integrated local Hamiltonian unless a measurement record from
outside B steers it. The patents' premise, net energy taken from the vacuum by
an abrupt drive, is the extraction claim, and the QET protocol tests its
boundary. The energies are expectation values of an encoded spin Hamiltonian,
so the run tests the device's realization of the theorem and its feed-forward
channel, not field stress-energy.

## The passivity ladder of the two-qubit QET model

[scripts/qet_passivity_controls.py](../../../scripts/qet_passivity_controls.py)
extends the exact reference [qet_two_qubit_reference.py](../../../scripts/qet_two_qubit_reference.py)
(Hotta's minimal model, [1002.0200](../papers/1002.0200.md); hardware precedent
[Ikeda 2023](../papers/2301.02666.md));
[its test](../../../tests/scripts/test_qet_passivity_controls.py) runs in the
`tests` check. Bob's local energy is `L = <H_B + V>`, whose ground-state value
is zero.

[I] Floors. Bob's operations leave `<H_A>` unchanged and the total energy
never falls below the ground energy. Alice's nonselective X_A measurement
commutes with H_B and V, so an operation that ignores her record acts as on the
unmeasured state, and on a prepared state rho it ends at `L >= -<H_A>_rho`:

| Operation on B after Alice's measurement | Floor on L | h = k = 1 value [E] |
|---|---|---|
| any record-independent channel (unitary, reset, damping) on the ground state | `-<H_A>_g = 0` | 0 |
| optimal record-steered rotation | `-E_B` | -0.114748 |
| any record-steered operation | `-E_A` | -0.707107 |

[E] Ideal arms at h = k = 1: feedback lowers L by E_B = 0.114748; reversed
feedback raises it by 0.332; fixed-sign rotations and record-independent
rotations by pi/4, pi/2 and pi never lower it; the fixed arms binned by
(record, sign) read +, -, -, + with contrast `(E_m - E_x)/2` = 0.223607; a
record flipped with probability q lowers L by `(1 - q) E_m + q E_x`, zero at
q* = 0.2566. The product-state mutation, |00> in place of the ground state with
the same angle and Hamiltonian, keeps an information excess of 0.581, because
Alice's record still gives the sign of X_A in the coupling V, while its channel
floor margin falls from +0.115 to -0.247: the lowering below the vacuum value
needs the ground state's entanglement, and the excess alone shows only that
the record was used.

[E] Confounds, the reason a single endpoint fails:

| Preparation error | Drop from the run's reference | L below its vacuum value | Record-independent best below vacuum |
|---|---|---|---|
| none | 0.1147 | 0.1147 | 0 |
| RY-angle error 0.05 rad | 0.0436 | 0.1036 | 0.0600 |
| idle Z phase 0.5 rad on B | 0.1510 (record-independent alone 0.1731) | -0.0221 | 0 |
| amplitude damping 0.05 | 0.1381 | 0.0820 | -0.0561 |

[I] An angle error moves energy from B's terms into H_A and puts L below its
vacuum value with no information; an idle Z phase on B, which detuning during
the measure-to-branch wait produces, is a rotation a record-independent Bob
undoes, so a drop from the run's own reference is no evidence (ZZ coupling is a
global phase on the 00/11 pair and needs its own model); amplitude damping
inflates that drop. Two endpoints survive:

- **Information excess against unitaries:** the lowest L any
  record-independent unitary on B reaches on the same preparation, minus the
  feedback arm's L. [E] That minimum is a Kabsch problem: after a rotation R
  of B's Bloch frame, `L = const + tr(R M)` with `M = -h s z^T + 2k c x^T`, s B's
  Bloch vector and `c_j = <X_A sigma_j^B>`; M has rank at most two, so the
  minimum is `const - (sigma_1 + sigma_2)` from its singular values, and it
  matches a five-start Euler-angle search to 1e-8 on every grid case. A q = 1/2
  record makes the feedback arm a mixture of record-independent unitaries, so
  its excess is at most zero on every preparation the grid covers. Amplitude
  damping inflates the excess (0.138 at 0.05), so it certifies that the record
  was used and estimates E_B only through a noise model.
- **Channel floor margin:** `-<H_A>_rho` minus the feedback arm's L, sound
  against every record-independent channel including reset and damping; it
  needs `<Z_A>` from a reference circuit that omits Alice's X measurement.
  [E] Ideal value 0.1147; 0.0966 under damping 0.05; 0.0295 under an angle
  error 0.05.

[E] The estimator decides soundness. Substituting Alice's reported bit for
X_A gives an excess of 0.115, 0.121, 0.133 and 0.411 at record-flip
probabilities 0, 0.01, 0.03 and 0.5: a broken readout manufactures the
signal. Reading X_A again at the end of every circuit, with a 2 percent
symmetric assignment error, gives 0.100, 0.096, 0.087 and -0.106, because the
estimate is then the expectation of an operator `O_B + X_A O'_B` on the
physical state, which passivity binds; on every grid preparation the
remeasured estimator shows no excess with a q = 1/2 record.

## Falsification experiments

Ranked by decisiveness per second of quota. None has a written case or
approval; each needs the dry run, analysis and case of
[qpu-submission.md](../ibm_quantum/qpu-submission.md) first.

1. **Analytic falsifiers (zero quota).** [E] The decomposition above. A
   reproducible measurement of radiated power from a steadily spinning
   axisymmetric charge, or of a classical Maxwell field with negative active
   mass, would refute it; NAWCAD's three-year test reported neither.
2. **QET passivity ladder on Heron r2 (two qubits, dynamic).** [I] Alice
   measures X_A mid-circuit, and every arm branches on her bit, so all arms
   share the 201-cycle (804 ns) capture-to-receive latency and the 2.1 us
   (Fez) to 2.6 us (Kingston) measure-to-branch idle of
   [heron-r2-readout-resonator.md](../ibm_quantum/heron-r2-readout-resonator.md#6-quantities-and-answers).
   Every circuit ends with an X measurement of A and a Bob measurement in the
   listed basis. Circuits at h = k = 1:

   | Arm | Bob rotation | Bob bases | Circuits |
   |---|---|---|---|
   | reference | none | X, Y, Z | 3 |
   | feedback | `-r phi*` | X, Z | 2 |
   | reversed | `+r phi*` | X, Z | 2 |
   | fixed plus, fixed minus | `-phi*`, `+phi*` in both branches | X, Z | 4 |
   | Z_A reference | no Alice measurement; A read in Z | Z | 1 |
   | product-state mutation | reference, feedback and Z_A reference on \|00> | X, Y, Z; X, Z; Z | 6 |
   | readout calibration | \|11> through the floor arm's measure, idle branch and readouts | Z | 1 |

   Endpoints: the channel floor margin (preregistered positive on the ground
   state, negative on the product state), the information excess, the binned
   +, -, -, + table, and the
   feed-forward flip `q_eff = (L_fb - L_match)/(L_mismatch - L_match)` with
   L_match and L_mismatch from the fixed arms binned by the recorded bit.
   Binning both sides by the same record cancels readout and preparation
   error to first order, so q_eff measures whether the branch executes the
   rotation the bit selects. [E] A 5-sigma detection of the ideal excess needs
   7785 shots per setting and arm; the 19 circuits take about 148000 shots, and
   every disjoint pair the placer packs into the same shots adds a replica at no
   extra charge. The product-state floor arm doubles as the \|00> readout
   calibration, so the summary also reports a readout-corrected margin; readout
   error lowers the raw margin, which stays the conservative primary.
   The device question that justifies hardware under the routing rule is
   q_eff: it measures measure-and-feed-forward fidelity on the stack whose
   N = 21 feedback contrast read +0.0027 against a predicted +0.0344
   ([n21_feedforward_backends.md](n21_feedforward_backends.md)), with readout
   assignment, latency idle and branch dephasing as named alternatives.
   Falsifiers: an excess at or below zero with the fixed arms at their
   predicted values falsifies the feed-forward channel; a record-independent
   arm whose L falls below the measured `-<H_A>` beyond its interval falsifies
   the state description of the readout. Twirling and dynamical decoupling
   stay off, as every circuit carries feed-forward. Before a case: the dry run
   confirms that an `if_else` with identical branches keeps its broadcast
   (else the fixed arms lose the latency match), and the estimator model
   takes the live assignment errors of both qubits.
3. **Replication on IQM Garnet with `cc_prx`.** [I] `cc_prx` rotates only when
   the stored bit is 1, so Bob's `-r phi*` becomes an unconditional `+phi*`
   followed by a conditional `-2 phi*`; published examples use angle pi only,
   so a garnet:mock compile and one priced shot batch qualify the angle first
   ([n21_feedforward_backends.md](n21_feedforward_backends.md#what-iqm-cc_prx-and-measure_ff-express)).
   A second stack separates a Heron-specific feed-forward loss from a
   protocol error.
4. **Distance decay on a 16-plus-qubit chain.** [I] Extraction against
   Alice-Bob distance on a heavy-hex path tests whether the information
   excess tracks the ground-state correlation; ground-state preparation
   fidelity dominates it, so it waits on an exact free-fermion reference
   checked against exact diagonalization at 12 to 14 qubits.

## Hardware results on ibm_kingston

Three jobs on 14 calibration-qualified pairs (backup instance, 110 s in total; claims
`kingston-qet-ladder-margin-and-feedforward`, `kingston-qet-window-phase-static` and
`kingston-qet-compensated-information-excess` in [the registry](../../state/RESEARCH_STATE.md)):

- [E] **[The ladder](../../../results/live/2026-10-25T203822.040562Z/FINDINGS.md).** Feed-forward executes the
  selected branch (`q_eff` median -0.05), but the channel floor margin is -0.160 +- 0.052 against +0.057 predicted.
  The shortfall tracks the prepared parity at a correlation of 0.961.
- [E] **[The frame diagnostic](../../../results/live/2026-10-25T225332.266272Z/FINDINGS.md).** The parity loss is a
  static phase on B over the measure-to-branch idle, with or without Alice's readout. The service scheduler puts
  that idle inside the preparation CX. Completing the CX first moves the phase onto `<X_A X_B>`. A fit gives B
  detunings of -54 to +11 kHz and A-B ZZ of 1.5 to 14 kHz. An echo cannot be placed in the window, because the
  scheduler plays a branch target's pre-branch gates at the receive.
- [E] **[The compensated ladder](../../../results/live/2026-10-25T233207.284563Z/FINDINGS.md).** With Bob's
  record-independent `rz` fixed per pair from that pair's reference arms, the information excess is
  +0.107 +- 0.006 (lower bound +0.096) against the ideal 0.115: the measured record lowers Bob's energy below every
  record-independent unitary on the same state. The channel floor margin stays at -0.073 +- 0.015, because the
  prepared state's best uninformed local energy already sits 0.18 above the vacuum value. At a 50 us repetition
  delay the job charged 81 us per shot against 276 us at 250 us.
- [O] **The scheduled-idle replay.** `scripts/scheduled_idle_replay.py` writes each run's service-scheduled idle
  in as delays and computes the exact law under the execution Target (`idle-replay.json` in each run directory).
  Unpadded and padded exact values, against the measurement:

  | Endpoint | unpadded | padded | measured |
  |---|---|---|---|
  | ladder channel floor margin | +0.057 | +0.001 | -0.160 |
  | ladder information excess | +0.105 | +0.099 | +0.019 |
  | frame as-run parity `<Z_A Z_B>` | 0.982 | 0.960 | 0.863 |
  | frame as-run window phase, rad | 0.010 | 0.010 | 0.267 |
  | compensated selected information excess | +0.105 | +0.112 | +0.107 |
  | compensated selected margin | +0.057 | +0.028 | -0.073 |

  Incoherent idle closes about a quarter of each margin gap and creates no window phase. The phase that empties the
  uncompensated information excess is coherent and lies outside the Target's T1 and T2. Once each pair's own
  reference arms compensate it, the measured information excess agrees with the model padded or not (0.112 and
  0.105 against 0.107), an endpoint the incoherent idle barely moves. The
  remaining margin shortfall of 0.10 sits in the reference arm's uninformed energy, where preparation and the
  measured assignment errors carry it (on the ladder, A's `p(0|1)` reads 0.030 against 0.014 in the padded model).

[I] For the Pais question, no arm in any of the three jobs lowered Bob's energy below the floor that binds
record-independent operations. The information-driven lowering appears at 93 percent of ideal, but always from a
state that preparation and idle error left above the vacuum value.

[O] The same replay settles the retained N = 21 Kingston feedback null
([scheduled-idle findings](../../../results/live/2026-10-18T090603.530638Z/IDLE_REPLAY_FINDINGS.md)). The leaf
qubits idle 57 to 62 us of a 70 us circuit, and the padded exact contrast is -0.0007 against the unpadded +0.0310,
inside the measured [-0.0129, +0.0184]. The two cases split the idle error cleanly. On N = 21, a deep routed circuit,
the incoherent part alone removes the contrast. On QET, a shallow two-qubit circuit with a 2.8 us window, the
coherent phase dominates, and N = 21's residual law distance of 0.013 TV is the candidate for it.

## Uncertainty

[I] That the field-generator, inertial-mass and gravitational-wave devices
produce none of the claimed effects: very high confidence, resting on the
Maxwell identities, the vacuum-field ratios and the NAWCAD result; a
reproducible measurement of radiation from a steady axisymmetric charge would
lower it. The information excess of +0.107 on Kingston is measured, not
inferred; it would fall if a non-unitary record-independent channel on B
(for example a reset timed by the record's schedule) beat the Kabsch floor,
which the negative channel floor margin leaves open.
