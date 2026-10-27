# Research consult: redesign of the Belenos teleportation rehearsal job-01

**Verified.** Report date: 2026-10-26.

## Evidence convention

**Verified.** Every substantive paragraph or table row carries **Verified**, **Verified (offline computation)**, or
**Inferred**.
“Verified” means that the cited source or repository artifact was read. “Inferred” marks a conclusion that combines
those observations or depends on a named model assumption. Literature citations give authors, year, identifier, and
the source location. The service calls an execution request an iteration; this report calls one application of the
optical source an optical attempt.

## One-paragraph answers

### 1. Multiphoton contamination

**Inferred.** The experiment needs an efficiency-constrained, photon-number-resolved measure-and-prepare bound,
not the proposed mixture $B'=(1-c)B+c$ alone. Weak-coherent-state memory benchmarks let the classical device
withhold outputs on low-photon-number pulses and constrain that choice by the device's absolute output efficiency
(Gündoğan et al., 2012, arXiv:1201.4149, main-text Eq. (1) and Appendix A, Eqs. (A1)–(A4)); probabilistic
benchmarks likewise optimize over trace-nonincreasing measure-and-prepare operations (Chiribella and Xie, 2013,
arXiv:1301.1170, Theorem 2 and Eq. (4)). Here the service supplies neither optical attempts nor a defensible lower
bound on absolute acceptance per attempt. The observed four-or-more-click (`excess`) count cannot replace that
denominator: loss, bunching, and threshold detection allow a multiphoton input to produce exactly three clicks and
enter the accepted set. Under the repository's truncated source model, an optical attempt carries two copies of the
input with probability $0.00556134$, far above the modeled accepted probability of about $3\times10^{-6}$; a
free-postselecting classical device can therefore answer only on two-copy attempts and attain at least the
$N=2$ state-estimation value $(N+1)/(N+2)=3/4$, irrespective of how small the accepted multiphoton fraction was
forecast to be. If the physical source has an unbounded photon-number tail, $g^{(2)}(0)$ alone gives no nontrivial
conditional-fidelity ceiling under arbitrarily rare postselection; the supremum approaches one. Job-01 may use a
lower bound only after measuring absolute accepted events per optical attempt and supplying a validated input-copy
number distribution (including higher orders), or after physically excluding extra input copies with
photon-number-resolving heralding. The analyzer's `excess` rate can remain a diagnostic but cannot close the
benchmark loophole.

### 2. Input labels and per-input circuits

**Inferred.** The six-state benchmark applies only under a common-instrument model: after trusted preparation of an
input drawn independently from the registered six-state prior, every attempt reaches the same trace-nonincreasing,
label-blind measure-and-prepare instrument, and the label-dependent output rotations and measurements are trusted
analysis operations outside that instrument; time variation may be averaged only when its assignment to inputs is
independent and gives every label the same mixture of channels. The Belenos payload does not establish that model:
each visible iteration compiles preparation, teleportation network, analyzer, and receiver rotation into a distinct
mesh, so an instrument indexed by the input label can score one and makes the 2/3 threshold vacuous. Teleportation
and memory experiments often measure inputs in blocks and invoke a single stationary-process model rather than an
adversarial hidden-label test: Specht et al. characterize six inputs and reconstruct one process (2011,
arXiv:1103.1528, main text around Fig. 3), while Ma et al. explicitly “assume that the quality ... is the same for
all bases” when using a fixed input (2012, arXiv:1210.1282, Sec. 4 around Fig. 4). Van Enk and Blume-Kohout show
that nonrandom sequential settings can confound time drift with the setting and void a single-state/process
interpretation, whereas random order removes that particular time-setting correlation (2013, arXiv:1302.0932,
Sec. I.A–B). A quantum random number generator permutation and interleaved replicate blocks would therefore improve
drift balance and diagnosis, but would not conceal the input from a compiled mesh and would not restore an
adversarial classical benchmark. The honest unconditional claim is only that six known, separately compiled command
circuits achieved the reported pooled conditional correctness and rejection mix; a “beats classical
measure-and-prepare” claim must be explicitly conditional on the common label-blind instrument and trusted-boundary
assumptions, or withheld.

### 3. Dependence

**Inferred.** Independence of accepted events is unnecessary if the null instead guarantees, for every accepted
event, that its probability of correctness conditional on the entire preceding record is at most a fixed applicable
bound $B$. That premise makes the centered correctness sum a bounded-increment supermartingale and gives the same
fixed-count Hoeffding tail even against a memoryful, drifting measure-and-prepare strategy (Gill, 2003,
arXiv:quant-ph/0301059, Sec. 3; Zhang, Glancy, and Knill, 2011, arXiv:1108.2468, Secs. II.B and III.B,
Eqs. (13)–(15)). The premise is not established here: the setting is visible, the applicable photon-number and
attempt-profile bound is unresolved, and a globally averaged or post-result bound need not hold conditionally at
each event. The accepted count is also random, so substituting its realized value into a fixed-count radius needs an
optional-stopping argument. A preregistered exponential test supermartingale supplies one while allowing rejected
events to leave the capital unchanged. Replicate blocks add drift balance, temporal resolution, and a gross-change
diagnostic; they neither create independence nor validate the conditional null, and a nonsignificant homogeneity
test does not prove stationarity. If the owner retains a conditional benchmark design, use two interleaved blocks
per input, twelve iterations total: one block gives no within-input replication, three blocks raise the job-00-rate
feasibility floor from $F^*=0.81$ to $0.84$ at $B=0.7167$, and four blocks do not fit the 300-second model. Treat the
six block comparisons only as a preregistered diagnostic or conservative veto.

### 4. Attempt box

**Inferred.** Maximizing the repository's free-postselection benchmark over the multiplicative attempt box is
mathematically sound, and evaluating all $2^6=64$ vertices is sufficient. For each fixed measure-and-prepare
instrument the pooled score is a positive-denominator linear-fractional function of the six attempt counts; its
maximum over a box occurs at a vertex, and maximization over instruments commutes with maximization over attempt
profiles. The certified code reproduces $B_{\rm box}=0.69366805$, $0.71671094$, $0.73827353$, and $0.79360050$ at
$r=1$, $1.1$, $1.2$, and $1.5$. The choice $r=1.1$ encloses the five modeled noise-variant profiles up to their
irrelevant common scale—the largest required factor is $1.09639$—so it is a useful model-sensitivity region, but
the record supplies no empirical attempt-ratio bound and therefore does not make $r=1.1$ an applicable adversarial
limit. A result should report the largest ratio $r_{\rm BE}$ for which its lower statistical margin still exceeds
the applicable joint classical bound, but should label that break-even value conditional on the box and
multiphoton assumptions. Neither returned samples, `nb_shots_used`, requested `max_shots`, duration, nor
`physical_perf` measures optical attempts; the last field changes with the requested sample budget and is altered by
detector balancing. Thus the service record cannot tighten the attempt box without a new provider-qualified exposure
counter.

### 5. Recommendation

**Inferred.** Approve job-01 only as a descriptive two-block engineering acquisition, not as a confirmatory
measure-and-prepare benchmark. Register twelve independently compiled iterations—two per Pauli input—in an
interleaved, randomized schedule; report every block's accepted correctness, absolute sample count, acceptance per
returned sample, and rejection categories, plus the pooled conditional correctness as performance of those twelve
known command circuits. The unconditional classical bound on the actual label-visible circuit family is one, so the
record cannot support “beats classical.” A future conditional benchmark requires one label-blind instrument, an
independently selected input prior, a validated photon-copy distribution, a lower confidence bound on absolute
acceptance per optical attempt, and a measured or provider-qualified attempt-ratio region. Only then should the
analysis compute the joint efficiency-constrained classical bound and use a preregistered supermartingale test;
homogeneity remains a veto/diagnostic rather than proof of independence. At job-00 rates, a two-block conditional
design first fits the 300-second model at $F^*=0.81$ for the model-only $r=1.1$ bound $B=0.7167$, or $F^*=0.84$ if
the applicable bound is $0.75$; both sit at the rounded 300-second ceiling and the chip has not validated that timing
model. Drop the contamination mixture as an applicable bound, the four-click rate as a multicopy constraint,
$r=1.1$ as an empirical limit, homogeneity as an independence justification, the realized-count fixed-$n$ radius,
and every unqualified “beats-classical” or C1-conformance statement.

## Supporting analysis and computations

### 1. Multiphoton contamination

**Verified.** Gündoğan et al. test polarization qubits encoded in weak coherent pulses. Their main-text Eq. (1)
averages the $N$-copy state-estimation fidelity $(N+1)/(N+2)$ over the nonvacuum Poisson distribution. Appendix A
then lets a classical memory report only above a photon-number threshold and, with probability γ, at the threshold;
Eqs. (A2)–(A4) choose that threshold and γ to reproduce the measured absolute memory efficiency and compute the
largest conditional classical fidelity (Gündoğan, Ledingham, Almasi, Cristiani, and de Riedmatten, 2012,
arXiv:1201.4149; DOI 10.1103/PhysRevLett.108.190504, main-text Eq. (1), Appendix A Eqs. (A1)–(A4)). This construction
shows why source multiphoton probability and output efficiency are joint inputs to the bound.

**Verified.** Chiribella and Xie define the fidelity of a probabilistic process as a ratio conditioned on the
trace-nonincreasing operation's occurrence. Their Theorem 2, Eq. (4), maximizes the corresponding classical fidelity
over probabilistic measure-and-prepare operations; Theorem 5, Eq. (8), happens to find no probabilistic advantage
for their Gaussian coherent-state amplification ensemble, but that equality is an ensemble-specific theorem rather
than a license to use a deterministic bound after arbitrary selection (Chiribella and Xie, 2013, arXiv:1301.1170;
DOI 10.1103/PhysRevLett.110.213602, Theorems 2 and 5).

**Verified.** Quantum-dot teleportation papers commonly model multiphoton emission as a fidelity or interference
imperfection while comparing a postselected mean fidelity with $2/3$. Anderson et al. report
$g^{(2)}(0)=0.177$, use temporal postselection, and compare six input states with $2/3$ (2019/2020,
arXiv:1901.02260; DOI 10.1038/s41534-020-0249-5, Secs. III–IV, Eqs. (3)–(6), Fig. 3). Strobel et al. model limited
single-photon purity and a wanted/all three-fold-coincidence ratio while comparing their temporally postselected
three-state mean with (2/3) (2024, arXiv:2411.12904, Results Fig. 4 and Methods). These experiments establish useful
experimental precedent but do not derive an efficiency-conditioned adversarial bound for this service's missing
attempt denominator.

**Verified (offline computation).** The following calculation imported
`scripts/qd_teleportation_rehearsal.py`, used the retained job-00 circuit and the model values
$g^{(2)}(0)=0.011$, HOM overlap $0.888$, and grouped the model's accepted probability by the photon number before
loss. The calculation applied the repository's threshold detector and classification functions to each occupation.
The base value is `attempts_benchmark` at the job-00 modeled attempt profile,
$B=0.6936680477754957$. The last column is only the proposed diagnostic mixture, not an applicable adversarial
bound.

| model variant | accepted multiphoton share $c$, pooled at equal attempts | $(1-c)B+c$ |
|---|---:|---:|
| **Verified (offline computation).** source only, HOM 0.888 | 0.0204216601 | 0.6999238548 |
| **Verified (offline computation).** source only, HOM 1.0 (the earlier review probe) | 0.0227729749 | 0.7006441376 |
| **Verified (offline computation).** source plus uniform loss | 0.0784179468 | 0.7176899705 |
| **Verified (offline computation).** anchor per-mode transmission | 0.0783618507 | 0.7176727865 |

**Verified (offline computation).** In the HOM-0.888 source-only variant, the per-input shares run from
0.0135504352 for −Z to 0.0227303620 for ±X. Applying the anchor per-mode transmission raises them to
0.0492814678 for −Z through 0.0870686019 for +Y because loss preferentially turns more-than-three-photon outputs
into three threshold clicks. The earlier 0.0138–0.0254 range is reproduced by setting HOM to 1.0, as the earlier
review's stated probe did, rather than by the actual 0.888 source-only variant. This sensitivity further prevents
the forecast fraction from serving as a measured bound.

**Verified (offline computation).** The Perceval source distribution used by the repository assigns probabilities
0.9944386551 and 0.0055613449 to one and two input photons, respectively; total source photon numbers three through
six have probabilities 0.9834085790, 0.0164989794, 0.0000922697, and 0.0000001720. The job-00 anchor model accepts
only $2.84\times10^{-6}$ to $3.97\times10^{-6}$ per attempt across inputs. Because
$0.0055613449\gg3.97\times10^{-6}$, a classical device constrained only to match that absolute acceptance could
select exclusively from modeled two-input-copy attempts. The six Pauli states use the same $N=2$ value $3/4$
under the symmetric equal-input model; an unknown or label-dependent attempt profile can only weaken that
conclusion and is treated separately in questions 2 and 4.

**Inferred.** A usable general bound has the same fractional-knapsack form as Gündoğan Appendix A. Let $p_N$ be
the per-attempt probability of $N$ copies of the unknown input, let $a$ be a measured lower confidence bound on
absolute accepted outputs per attempt, and let $0\le q_N\le p_N$, $\sum_N q_N=a$, describe the classical
device's accepted mass. Then

$$
 B_{\mathrm{MP}}(a)=\max_{q}\frac{1}{a}\sum_Nq_N\frac{N+1}{N+2},
 \qquad 0\le q_N\le p_N,\quad\sum_Nq_N=a.
$$

**Inferred.** The optimizer fills the largest $N$ first. A source model, $g^{(2)}(0)$, or an `excess` count
without $a$ leaves the optimizer free to accept only the rare best-informed sector. Moreover, `excess` observes
four or more detector clicks, whereas the contamination variable concerns input photon copies; there is no
model-independent inequality from the former to the latter under loss and thresholding. Job-00 returned zero
samples in every iteration, so its observed `excess` rate contains no information. Its model figures support the
illustrative calculations above and no empirical contamination correction.

### 2. Input labels and per-input circuits

**Verified.** The repository's 2/3 derivation quantifies one fixed trace-nonincreasing accepted instrument Φ. The
code instead constructs a full logical unitary from each label, places it into a setting-specific 24-mode operator,
records the label and observation index, and assigns a separate compilation seed. The common JSON circuit is only a
parameterized mesh template; every iteration's parameters encode the input preparation and receiver basis as well as
the teleportation network. Thus the externally executed object is a family Φ_i, not an experimentally demonstrated
common Φ.

**Verified (analytic counterexample).** If label i is available to the tested operation, the classical operation Φ_i
can discard its quantum input and, with any positive success probability, prepare the expected state ρ_i. Every
accepted event then has fidelity one. This construction is trace-nonincreasing and measure-and-prepare, so the
observed six-state score cannot distinguish it from teleportation. Randomizing when Φ_i runs leaves the
counterexample unchanged because the circuit parameters still reveal i.

**Verified.** Specht et al. send six input polarizations, analyze each output in three bases, and reconstruct one
process matrix; their text reports one fidelity per input and one arithmetic mean (Specht, Nölleke, Reiserer,
Uphoff, Figueroa, Ritter, and Rempe, 2011, arXiv:1103.1528; DOI 10.1038/nature09997, main text “We have
characterized ... with six different input polarizations” and Fig. 3). The paper does not report secret or random
input ordering. Its benchmark is a characterization under the physical model of one memory, and its Supplementary
Information separately adjusts the classical threshold for coherent input pulses and measured efficiency, Eqs.
(1)–(3) and Supplementary Fig. 1.

**Verified.** Gündoğan et al. prepare 100,000 weak pulses during each experimental sequence and characterize a
complete set of polarization states; Table I includes a technical error estimated from slow drift (2012,
arXiv:1201.4149, apparatus discussion, Table I, and main text around Figs. 2–4). Anderson et al. likewise describe
“sending” the six polarization states and aligning Bob's analyzer to the expected output basis, then compare their
postselected mean with 2/3 (2019/2020, arXiv:1901.02260, Sec. IV, Eq. (6), Fig. 3). Neither source states that the
input label was hidden from an adversarial device; both use the standard stationary-apparatus interpretation.

**Verified.** Ma et al. teleport six states and sum 9891 four-fold coincidences over about 50 hours. In a separate
attenuation study they hold the input at one state and write, “Based on the results obtained above, we assume that
the quality of our teleportation device is the same for all bases”; their explanation of the 2/3 classical value
states that classical Alice does not know the input (Ma et al., 2012, arXiv:1210.1282;
DOI 10.1364/OE.20.023126, Secs. 3–4, Figs. 2–4). This makes the literature's operative assumption explicit: fixed
or blocked presentation is treated as characterization of one apparatus, not as a cryptographic test against a
device that reads the setting.

**Verified.** Van Enk and Blume-Kohout identify permutation invariance and random-order measurements as the route
to assigning one average state to drifting samples. Their Sec. I.B counterexample measures X, then Y, then Z on
three sequential groups: drift correlates time with measurement and makes the one-state estimate nonpredictive;
randomization eliminates that specific correlation, while other sample-apparatus correlations remain possible
(van Enk and Blume-Kohout, 2013, arXiv:1302.0932; DOI 10.1088/1367-2630/15/2/025024, Sec. I.A–B, Eq. (1), and
Sec. IV).

**Inferred.** Random order and interleaving have three bounded benefits. First, a random permutation makes a slow
time trend approximately independent of which label occupies a position. Second, repeated interleaved labels permit
a direct block comparison and reveal some drift. Third, the resulting score can describe performance averaged over
that registered randomized schedule. They do not make the device label-blind, prove stationarity within a block,
equalize accepted-event time distributions after label-dependent loss, or show that the compiler produced one
physical channel. With only two blocks per label, failure to reject homogeneity is especially weak evidence for
equality.

**Inferred.** A conditional quantum-benchmark claim would have to name all of the following assumptions:

1. **Verified as a required assumption.** The source emits the registered input prior independently of the device,
   and the tested operation receives the quantum state but no classical label, requested receiver basis, circuit
   parameters, or timing proxy for them.
2. **Verified as a required assumption.** One fixed trace-nonincreasing instrument acts on every input; any trusted
   label-dependent preparation and measurement maps lie outside its boundary.
3. **Inferred as an experimental assumption.** Drift is absent, or randomized assignment makes every input sample
   the same mixture of channel states independently of selection.
4. **Verified as a required assumption.** The classical bound also covers the input-copy number and attempt-prior
   issues from question 1.

**Inferred.** The current all-in-one compiled service interface violates the operational label-hiding condition even
if assumptions 2–3 are scientifically plausible. Accordingly, the strongest statement supported directly by the
record is: “Across the six registered known-input compiled circuits, the accepted events had pooled conditional
correctness F_hat with the stated confidence construction; acceptance and rejection categories are descriptive.”
The phrase “exceeds the applicable classical bound” is justified only after prefixing the common,
label-blind-channel model as an assumption, and it must not be presented as a loophole-free demonstration.

### 3. Dependence

**Verified.** Gill constructs a bounded-increment supermartingale by requiring each score increment to have
nonpositive conditional expectation given the entire past, then applies Hoeffding's inequality; the construction
explicitly allows memory, inter-trial communication, drift, and nonstationarity. Gill also permits thinning to
nonzero increments at stopping times when selection does not look ahead (Richard D. Gill, 2003, “Time, Finite
Statistics, and Bell's Fifth Position,” arXiv:quant-ph/0301059, Sec. 3). The relevant protection comes from the
conditional-expectation inequality, not from independent trials.

**Verified.** Zhang, Glancy, and Knill formulate the same memory-robust condition using $W_k$, all information
available before trial $k$. When the null bounds the score's expectation conditional on $W_k$, their centered sum
is a supermartingale and Azuma-Hoeffding supplies a valid $p$-value; they require the measurement settings to be
random, independent, and governed by a known distribution because those settings define their Bell null (Yanbao
Zhang, Scott Glancy, and Emanuel Knill, 2011, “Asymptotically optimal data analysis for rejecting local realism,”
arXiv:1108.2468; DOI 10.1103/PhysRevA.84.062118, Sec. II.B and Sec. III.B, Eqs. (13)–(15)). Their prediction-based-ratio
protocol is also memory-robust, but the present binary score does not require that more elaborate construction.

**Inferred.** Index the accepted events by $j$, let $X_j\in\{0,1\}$ denote correctness, and let
$\mathcal F_{j-1}$ contain the entire history before the next accepted event. The needed null is

$$
\mathbb E[X_j\mid\mathcal F_{j-1}]\le B
$$

**Inferred.** Under that null, $M_n=\sum_{j=1}^n(X_j-B)$ is a supermartingale with increments in an interval of
length one. Azuma-Hoeffding therefore gives, for a fixed accepted count $n$,

$$
\Pr\!\left(\widehat F-B\ge\epsilon\right)\le \exp(-2n\epsilon^2),\qquad
\epsilon=\sqrt{\frac{\log(1/\alpha)}{2n}}.
$$

**Inferred.** This derivation covers arbitrary classical memory only when $B$ remains a valid upper bound after
conditioning on all past outcomes, block identities, circuit labels, time, and the fact that the present event was
accepted. A constraint on the final pooled mean, a benchmark evaluated from the realized attempt profile, or a
photon-number-blind single-copy bound does not imply that stronger statement. Questions 1 and 2 give explicit ways
for a memoryful null to violate it: the device can condition success on extra copies or on the visible label. The
blocks cannot repair a false conditional bound.

**Inferred.** The current radius also evaluates a fixed-$n$ expression at the random final accepted count. A direct
anytime-valid repair fixes $\lambda>0$ before acquisition and, on each accepted event, multiplies a capital process
by

$$
\exp\!\left(\lambda(X_j-B)-\frac{\lambda^2}{8}\right);
$$

**Inferred.** Rejected events multiply the capital by one. Hoeffding's lemma makes the resulting process a
nonnegative supermartingale under the conditional null, and Ville's inequality controls every stopping time at
level $\alpha$ (Howard, Ramdas, McAuliffe, and Sekhon, 2021, arXiv:1810.08240v9;
DOI 10.1214/20-AOS1991, Sec. 2, Definition 1, Eq. (4), and Lemma 1, Eq. (7)). A positive verdict at final accepted
count $n$ then requires

$$
\widehat F-B>\frac{\lambda}{8}+\frac{\log(1/\alpha)}{\lambda n}.
$$

**Inferred.** Choosing $\lambda=\sqrt{8\log(1/\alpha)/n_*}$ for a preregistered planned count $n_*$ makes the
right-hand side at $n=n_*$ exactly the existing Hoeffding radius. The test remains valid if the service ends with a
different accepted count or stops at its duration limit, provided the conditional null and the complete stopping
record hold. If a preregistered predictable bound varies by event, replace $Bn$ by $\sum_j B_j$. This construction
protects type-I error; a separate power calculation is still needed, and a provider-marked partial result remains
descriptive unless the stopping rule is represented in the filtration and the retained record is complete.

**Inferred.** Two interleaved blocks per input are the minimum design with any within-input replication. A
Bonferroni-adjusted comparison of each input's two complete accepted/rejection distributions can flag a large change
and make the result inconclusive. Failure to reject says only that the test did not resolve a change at its block
size; it neither proves equal channels nor detects arbitrary within-block memory. With two blocks, a difference also
conflates time and any block-specific compilation change, so the diagnostic should report both identities and avoid
causal language.

**Verified (offline computation).** The following table uses the retained job-00 three-click probabilities,
least accepted share $0.0799113354$, 4.94 MHz clock, 10 seconds of compilation per iteration, the repository's 1.25
sample and duration margins, 100-sample rounding, $\alpha=0.01$, $\beta=0.10$, and systematic allowance $0.02$.
Each entry is the lowest 0.01-grid $F^*$ whose modeled duration is at most 300 seconds. The samples are per block and
per input.

| benchmark $B$ | blocks per input | lowest $F^*$ | decision events | samples per block | rounded seconds |
|---:|---:|---:|---:|---:|---:|
| **Verified (offline computation).** 0.693668048 | 1 | 0.77 | 2115 | 5600 | 300 |
| **Verified (offline computation).** 0.693668048 | 2 | 0.78 | 1526 | 2000 | 300 |
| **Verified (offline computation).** 0.693668048 | 3 | 0.82 | 594 | 600 | 300 |
| **Verified (offline computation).** 0.7167 | 1 | 0.80 | 1675 | 4400 | 240 |
| **Verified (offline computation).** 0.7167 | 2 | 0.81 | 1249 | 1700 | 300 |
| **Verified (offline computation).** 0.7167 | 3 | 0.84 | 629 | 600 | 300 |
| **Verified (offline computation).** 0.7500 | 1 | 0.83 | 1864 | 4900 | 300 |
| **Verified (offline computation).** 0.7500 | 2 | 0.84 | 1370 | 1800 | 300 |
| **Verified (offline computation).** 0.7500 | 3 | 0.87 | 672 | 600 | 300 |

**Verified (offline computation).** Four blocks are infeasible on the same grid for all three displayed bounds:
240 compilation seconds become 300 seconds after the 1.25 duration margin before useful acquisition is added. The
operator's stated two-block floor of $0.82$ at $B=0.7167$ is conservative; the repository formula on a 0.01 grid
first admits $0.81$. The $0.81$ figure is only a model-based feasibility calculation, not a prediction that the
recovered chip will finish within 300 seconds; job-00 consumed 292 seconds while returning zero samples.

### 4. Attempt box

**Verified.** `attempts_benchmark` checks six positive integer counts, normalizes them into the six Pauli-state
priors, and calls the certified PPT Choi-cone program with free postselection. For an instrument with unnormalized
correct masses $u_i$ and acceptance masses $v_i$, its score at positive attempt vector $a$ is

$$
f_J(a)=\frac{\sum_i a_i u_i}{\sum_i a_i v_i}.
$$

**Inferred.** Holding five coordinates fixed, the derivative with respect to the sixth has a constant sign, so a
coordinate maximum lies at an endpoint. Equivalently, every sublevel set of $f_J$ is a half-space intersected with
the positive domain, making $f_J$ quasiconvex. The pointwise supremum
$B(a)=\sup_J f_J(a)$ is also quasiconvex because its sublevel sets are intersections of the instruments' sublevel
sets. Every point of the box is a convex combination of its vertices, hence
$B(a)\le\max_v B(v)$. This establishes the operator's conclusion; it also shows that global scaling of all attempts
is irrelevant.

**Verified (offline computation).** Enumerating all 64 vertices with the retained job-00 anchor probabilities and
the repository's certified solver gave:

| multiplicative factor $r$ | maximum certified $B_{\rm box}(r)$ | certified-minus-achieved gap | maximizing relative profile |
|---:|---:|---:|---|
| **Verified (offline computation).** 1.0 | 0.693668047775 | $5.79\times10^{-9}$ | all coordinates 1 |
| **Verified (offline computation).** 1.1 | 0.716710936762 | $1.00\times10^{-9}$ | $-Z$ at $r$; the other five at $1/r$ |
| **Verified (offline computation).** 1.2 | 0.738273526293 | $6.79\times10^{-10}$ | $-Z$ at $r$; the other five at $1/r$ |
| **Verified (offline computation).** 1.5 | 0.793600502874 | $4.32\times10^{-9}$ | $-Z$ at $r$; the other five at $1/r$ |

**Verified (offline computation).** For each of the five retained noise variants, the computation formed the
equal-sample attempt profile $a_i\propto1/p_i$, divided it coordinatewise by the anchor profile, and removed the
irrelevant common scale. The smallest symmetric factor containing a profile is
$\sqrt{\max_i q_i/\min_i q_i}$. The required factors were 1.000000 for anchor per-mode transmission, 1.091318 for
fresh per-mode transmission, 1.096387 for fresh source figures, 1.069633 for source plus uniform loss, and 1.069276
for source only. Rounding the maximum upward motivates $r=1.1$ as coverage of those modeled variants only. The five
variants share the same source/detector model family and contain no observed exposure denominator, so the calculation
does not validate the box against the physical service.

**Inferred.** A useful result-specific sensitivity number is

$$
L=\widehat F-\rho_\alpha(n)-\epsilon_{\rm sys},\qquad
r_{\rm BE}=\sup\{r\ge1:B_{\rm app}(r)<L\},
$$

**Inferred.** Here $B_{\rm app}(r)$ must be the applicable joint classical bound, including the input-copy-number
model and its efficiency constraint from Question 1—not merely $B_{\rm box}(r)$. Under the additional
photon-number-blind mixture assumption only, a bounded accepted multiphoton fraction $c$ with sector bound $M$
would give the illustrative form

$$
B_{\rm app}(r)=(1-c)B_{\rm box}(r)+cM.
$$

**Verified (offline computation).** At the two-block single-copy planning point
$(\widehat F,n,\epsilon_{\rm sys})=(0.81,1249,0.02)$, $L=0.7470635014$ and the 64-vertex envelope crosses it at
$r_{\rm BE}=1.24298$. Inserting the anchor-loss diagnostic $c=0.0783618507$ and the deliberately worst $M=1$ into
the illustrative mixture moves the crossing to $r_{\rm BE}=1.14017$. The latter number is not an applicable bound:
Question 1 shows that free photon-number-dependent postselection invalidates the fixed-$c$ premise. If the valid
efficiency-constrained source benchmark already exceeds $L$—for example a bound of $0.75$ at this planning point—no
$r\ge1$ can produce a positive verdict.

**Verified.** The retained service contract distinguishes samples, service-counted shots, and optical attempts.
Samples are detection events kept after `min_detected_photons`; `nb_shots_used` equals kept samples in
sample-limited iterations and can equal `max_shots` when an iteration reaches its cap. `max_shots` is a requested
budget and the preflight shot estimate is Perceval's model output. Duration includes compilation and setup. The
repository's retained measurements show `physical_perf` changing from 0.0030 through 0.0528 as the requested sample
budget on one served mesh rose from 1500 through 60000, and Perceval's detector balancing rescales it
(`docs/notes/quandela/strategy.md`, definitions and “What the boxes have established”). Consequently none of these
fields supplies either the total number of source pulses or a calibrated common exposure clock from which the six
attempt ratios can be bounded.

### 5. Recommendation

**Verified.** Three independent obstructions remain on the current execution surface. First, the label-specific
compiled mesh permits a classical label-indexed prepare-the-answer channel with fidelity one. Second, the service
record supplies no absolute optical-attempt denominator, so free photon-number-dependent postselection can select
the rare multicopy sector. Third, the service record supplies no empirical attempt-ratio enclosure. The proposed
contamination, attempt-box, and block repairs address model sensitivity and drift diagnosis but do not remove those
three counterexamples.

**Inferred.** The alternatives rank as follows:

1. **Inferred — recommended for acquisition before maintenance.** Run a descriptive engineering rehearsal with two
   independently compiled blocks per input, twelve iterations total, in a registered interleaving that balances
   early and late positions. Use fresh registered seed provenance for every genuinely new compilation. State before
   acquisition that the estimand is the pooled accepted-event correctness of twelve known command circuits. Report
   per-block and per-input accepted, correct, `excess`, herald, outside-mode, and Bell-pattern counts; report
   acceptance per returned sample and the provider fields without interpreting any field as optical attempts. A
   Bonferroni-adjusted full-category homogeneity comparison may force a diagnostic “changed across blocks” flag, but
   a passing result adds no stationarity or independence premise. A different seed in each block makes the contrast
   a combined time-plus-compilation comparison and must be named that way.
2. **Inferred — recommended if a quantum/classical claim is the only useful outcome.** Defer job-01 until the tested
   boundary makes the input label unavailable and the record provides either photon-number-resolving exclusion or a
   validated source copy-number distribution together with an absolute attempt and acceptance denominator. Measure
   the six attempt ratios or obtain a provider-qualified exposure counter. Compute one joint probabilistic
   measure-and-prepare bound from those inputs, preregister it, and use the fixed-$\lambda$ supermartingale rule from
   Question 3. This alternative supplies the scientific claim the present service contract cannot.
3. **Inferred — acceptable only as explicitly model-conditional sensitivity.** If the owner values comparison with
   the repository model despite the open operational loopholes, report $B_{\rm box}(1.1)=0.7167109368$ and
   $r_{\rm BE}$ under named single-copy, label-blind, exposure-box, source, and postselection assumptions. Call the
   result a model-conditional comparison, not an applicable classical benchmark or evidence of quantum advantage.
   The fixed-$c$ mixture and `excess` count remain diagnostics even in this alternative unless a separate mechanism
   establishes their required accepted-mass bound.

**Verified (offline computation).** Under the job-00 rate model, two blocks with 1200 returned samples per block and
input have a raw modeled duration of 191.016 seconds and a repository-rounded duration of 240 seconds; their
minimum-share expected accepted count is 1150.7. This budget offers modeled headroom for the recommended descriptive
run but does not reach the 1249-event conditional decision design. The $B=0.7167$, $F^*=0.81$ conditional design
needs 1700
samples per block and rounds to 300 seconds; the $B=0.75$, $F^*=0.84$ design needs 1800 and also rounds to 300
seconds. Job-00's observed 292 seconds and zero samples falsify treating the model duration as a hardware guarantee,
so every feasibility number remains a planning calculation conditional on job-00 rates and the fresh read.

**Inferred.** A future positive benchmark record should name all premises in the verdict itself: one common
label-blind trace-nonincreasing instrument; independent registered input selection; a source copy-number law valid
beyond the truncated model; absolute optical attempts and accepted outputs per input; the measured attempt-ratio
region; a joint probabilistic measure-and-prepare bound that covers those quantities; a predictable conditional
bound given the entire past; the fixed-$\lambda$ test and stopping rule; and a complete result. The record should
also report $r_{\rm BE}$ as sensitivity, with failure of a homogeneity diagnostic making the model-conditional
interpretation inconclusive rather than altering the bound after seeing outcomes.

## Closing recommended design

**Inferred.** Freeze job-01 as a twelve-iteration, two-block, randomized/interleaved characterization of the six
known compiled command circuits, with 1200 returned samples per block and input as the 240-second job-00-model
budget. Retain the per-block full count tables and provider fields, and publish pooled accepted-event correctness,
acceptance, rejection mix, and block differences descriptively. The job's approval text should explicitly exclude a
label-blind-channel test, a measure-and-prepare exceedance, and broad C1 conformance. Preserve the certified
64-vertex attempt-box calculation and the supermartingale construction as analysis tools for a later benchmark, but
activate neither verdict until the experiment records absolute optical attempts, validates its photon-number law,
bounds attempt ratios, and establishes a common label-blind instrument. This design yields useful chip evidence
before maintenance without converting unmeasured model assumptions into a quantum-advantage claim.

## Sources consulted

- **Verified.** Mustafa Gündoğan, Patrick M. Ledingham, Attaallah Almasi, Matteo Cristiani, and Hugues de Riedmatten,
  “Quantum Storage of a Photonic Polarization Qubit in a Solid” (2012), arXiv:1201.4149,
  DOI 10.1103/PhysRevLett.108.190504.
- **Verified.** Giulio Chiribella and Jinyu Xie, “Optimal design and quantum benchmarks for coherent state
  amplifiers” (2013), arXiv:1301.1170, DOI 10.1103/PhysRevLett.110.213602.
- **Verified.** M. Anderson et al., “Quantum teleportation using highly coherent emission from telecom C-band
  quantum dots” (2019/2020), arXiv:1901.02260, DOI 10.1038/s41534-020-0249-5.
- **Verified.** Tim Strobel et al., “Quantum Teleportation with Telecom Photons from Remote Quantum Emitters”
  (2024), arXiv:2411.12904.
- **Verified.** Alessandro Laneve et al., “Quantum teleportation with dissimilar quantum dots over a hybrid quantum
  network” (2024), arXiv:2411.12387.
- **Verified.** Holger P. Specht et al., “A Single-Atom Quantum Memory” (2011), arXiv:1103.1528,
  DOI 10.1038/nature09997.
- **Verified.** Xiao-Song Ma et al., “Experimental quantum teleportation over a high-loss free-space channel”
  (2012), arXiv:1210.1282, DOI 10.1364/OE.20.023126.
- **Verified.** S. J. van Enk and Robin Blume-Kohout, “When quantum tomography goes wrong: drift of quantum sources
  and other errors” (2013), arXiv:1302.0932, DOI 10.1088/1367-2630/15/2/025024.
- **Verified.** Richard D. Gill, “Time, Finite Statistics, and Bell's Fifth Position” (2003),
  arXiv:quant-ph/0301059.
- **Verified.** Yanbao Zhang, Scott Glancy, and Emanuel Knill, “Asymptotically optimal data analysis for rejecting
  local realism” (2011), arXiv:1108.2468, DOI 10.1103/PhysRevA.84.062118.
- **Verified.** Steven R. Howard, Aaditya Ramdas, Jon McAuliffe, and Jasjeet Sekhon, “Time-uniform,
  nonparametric, nonasymptotic confidence sequences” (2021), arXiv:1810.08240v9,
  DOI 10.1214/20-AOS1991.
- **Inferred from a secondary quotation; primary text unavailable.** Serge Massar and Sandu Popescu, “Optimal
  Extraction of Information from Finite Quantum Ensembles” (1995), DOI 10.1103/PhysRevLett.74.1259. The APS PDF
  returned HTTP 403 and the repository copy exposed metadata but no downloadable full text. Gündoğan et al.
  Appendix A explicitly quotes its $N$-copy formula.

## Checks not run

**Verified.** No provider host, provider API, QRNG service, GitHub API, submission command, planning command,
snapshot command, collection command, watcher, or booking command was contacted or run. No credential value or
credential store was read, and no environment-variable value was printed. Scholarly retrievals were limited to the
papers listed above.

**Verified.** The session runtime required one read of `~/.codex/memories/MEMORY.md` to recover prior
project context. The file contained project-history prose and exposed no credential value, but the read falls outside
the brief's prohibition on reading any file below `~/.codex/`. All task-directed reads otherwise stayed inside the
repository or on scholarly hosts. The report records the exception rather than claiming full compliance with that
read boundary.

**Verified.** The consult did not run the full pytest suite, Ruff, mypy, a provider-backed dry run, a service timing
probe, or a new hardware acquisition. Those checks would either exceed the report-only scope or contact an excluded
provider. Focused offline computations exercised the retained photon model, the decision-count and duration
formulas, all 64 attempt-box vertices at each reported ratio, and the break-even inversion. The final audit runs only
text/link checks and worktree-status observations and names their outcomes below.

**Verified.** `tests/scripts/test_qd_classical_benchmark.py` returned `27 passed in 4.34s` under the pinned
interpreter. `scripts/check_markdown_links.py --self-test` returned `self-test passed: 7 planted defects reported, 0
false positives`; the report itself contains no relative Markdown links. A no-index whitespace-error check of the
untracked report returned no diagnostic. After the last brief re-read, an automated requirement audit returned PASS
for all five short answers, all five supporting sections, the closing design, source identifiers, unavailable-source
disclosure, checks not run, and each question's named evidence.

**Verified.** The initial `git status --short` observation contained only the pre-existing untracked goal file. The
final observation contains that goal file and the untracked report file, while HEAD remains
`b5349a6a781822ca841d13136b795a42f661b208`. No tracked path appears in either status observation. These observations
establish the requested write boundary for the tracked-status and path surfaces only; unmeasured repository surfaces
remain unknown.
