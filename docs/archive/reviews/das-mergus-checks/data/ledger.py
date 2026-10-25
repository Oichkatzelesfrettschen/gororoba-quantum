from pathlib import Path
import json
OUT=str(Path(__file__).resolve().parents[2] / "2026-10-25-das-mergus-data-claims.json")
PIN="41d5ef03fbe3aef8ac80460731fe301bbd207957"; MAIN="182fb20 (main)"; EC="ec75554a1af800496d99c80ab23022e83c5e20ea"
J0="results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00"
J1="results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01"
EV="docs/evidence/ascella-order-coefficients"
def c(id,loc,st,kind,at,method,fals,ind,verdict,evidence,opp,action):
    return dict(id=id,locator=loc,statement=st,kind=kind,checked_at=at,method=method,falsifier=fals,independent=ind,verdict=verdict,evidence=evidence,opposition=opp,action=action)
reg="docs/state/research_state.json"
census_m="Independent Python census of docs/state/research_state.json, ci/gates.json, docs/state/plans/*.json and git ls-files (not the package's audit_corpus.py); SHA-256 of every claim evidence path."
L=[]
# ---- repository facts
for id,st,pin_v,main_v,loc in [
 ("R01","18,277 tracked files","18,277","19,011","README.md; ch01 census table"),
 ("R02","225 registered claims","225","233","README.md; ch01; ch08"),
 ("R03","414 claim/evidence hash bindings, every one matching its retained SHA-256","414 bindings, 0 mismatches, 0 missing","439 bindings, 0 mismatches, 0 missing","README.md; ch01; ch08"),
 ("R04","274 registered acquisitions: 144 Quantum Inspire, 74 Quandela, 32 IBM, 24 IQM","274 (144/74/32/24)","276 (144/74/32/26)","ch01"),
 ("R05","82 plans: 14 closed, 1 active, 1 paused, 66 inbox","82 (14/1/1/66)","86 (16 closed, 1 active, 1 paused, 67 inbox, 1 planned)","ch01"),
 ("R06","487 gate records","487","491","ch01"),
 ("R07","332 distinct claim-bound evidence files","332","354","ch01"),
 ("R08","20 tracked Rocq source files","20","26","ch01"),
 ("R09","Claim status split 129 established, 64 exploratory, 3 open, 11 proposed, 11 withdrawn, 7 superseded","129/64/3/11/11/7","134/67/3/11/11/7","ch01"),
]:
    L.append(c(id,loc,st,"repo-fact",f"{PIN} and {MAIN}",census_m,f"Any count at {PIN[:7]} differing from the statement",True,"stale",
      f"At {PIN[:7]}: {pin_v} (exact match). At current main: {main_v}.",
      "The count is a snapshot property of the named commit; it describes current main only after every later registry change is ignored.","none"))
L.append(c("R10","ch01 paragraph after census table","No unknown claim dependency, missing cited acquisition, missing named gate, missing document, or dependency cycle","repo-fact",f"{PIN} and {MAIN}",
  "Independent set-membership checks over depends_on, acquisitions, gates and documents; Kahn topological sort for cycles.","Any dangling reference or any node left after the topological sort",True,"confirmed",
  "0 unknown dependencies, 0 unknown acquisitions, 0 unknown gates, 0 missing documents, 0 nodes in cycles at both revisions.","Reference integrity says nothing about the correctness of any claim; the package states this itself.","none"))
L.append(c("R11","ch09 claim census","The appendix lists all 225 registered claims with the registry's status labels","repo-fact",PIN,
  "Parsed the 225 backticked claim rows of ch09 and compared ids and status words with the registry.","A missing, extra or status-mismatched row",True,"confirmed",
  "225 rows, 225 unique ids, set-equal to the registry at 41d5ef0, 0 status mismatches. Current main holds 233 claims, so the inventory is stale against main.","Labels are copied from the registry and carry no independent verdict.","none"))
L.append(c("R12","ch01 source boundary; README source identities","PR #449 final head f0f1788 is merged into main at 41d5ef0","repo-fact",PIN,"git merge-base --is-ancestor f0f1788 41d5ef0","Non-ancestry",True,"confirmed","f0f1788 is an ancestor of 41d5ef0 (merge commit 41d5ef0 'Merge pull request #449').","None.","none"))
L.append(c("R13","ch01 reconciliation table, core-630 row","core-630 failed because #443 introduced an unregistered parallel import that #447 fixed; #446 had already registered three seed files","repo-fact",PIN,
  "git log/merge-base on ed4d793, 3feaa8a (#443), ff3ebdf (#447), ae7fc17 (#446); diff of docs/state/hypercomplex-libraries/libraries.json.",
  "ed4d793 not entering through #443, or #447 not adding that import",True,"unproven",
  "Confirmed half: ed4d793 ('cd_phase_degree: send the polarity batches through the process pool') is an ancestor of 3feaa8a^2 and not of 3feaa8a^1; #447 adds exactly one import row to libraries.json and its message names core-630. Unproven half: the #446 diff adds scripts/ascella_response_geometry.py and os/sys import rows to libraries.json and touches no seed ledger file, so the 'three seed files' registered by #446 were not located.",
  "The #446 branch holds the single commit f086e16 (qi_matched_zero_divisor token-recovery successor). Seed-ledger changes before 41d5ef0 (ci/reproduction_seeds.json, docs/evidence/qrng_seeds/allocations.json) come from other merges (87f9a07, 27c9e0e), none of which is #446; the three-seed-file account was not located.","none"))
L.append(c("R14","ch01 reconciliation; ch04 table 4.1","Both Ascella jobs report 186 s duration","repo-fact",EC,"Read 'duration' in each raw/result.json.","A different duration",True,"confirmed","job-00 186, job-01 186 (raw/result.json top-level duration).","Equal totals with doubled samples do not identify acquisition time; the package says the same.","none"))
L.append(c("R15","ch04 section 5.1","The returned mesh has 132 couplers and 126 heaters","repo-fact","f0f1788","Read couplers/heaters fields of physical-models.json at f0f1788.","Different counts",True,"already-in-repo","physical-models.json records couplers 132, heaters 126.","None.","none"))
# ---- Ascella statistics
L.append(c("S01","README principal results; ch04 4.1","The raw-data analysis independently reproduces all 27 original Ascella endpoints and radii within 1e-12","statistic",EC,
  "Own decoder of raw/result.json (base64+zlib PCVL BSCount per iteration), settings mapped by observation_index with echoed circuit_params checked to 1e-15; endpoint weights rebuilt from the design (five-point transform, sign arms +,-,-,+, mutation weights from scripts/ascella_coherence_analysis.py); Hoeffding radii with m=27, alpha=0.01.",
  "Any endpoint value or radius differing from analysis.json by more than 1e-12",True,"confirmed",
  "All 27 endpoints of both jobs match analysis.json: max value difference 1.1e-16, max radius difference 5.2e-18; mutation difference 0.164550/0.170879 and mutation dark 0.000793/0.000732 exact. All 27 verdicts are 'qualifies' in both records.",
  "Reproduction of retained arithmetic; the endpoints and verdicts are already the registered result.","none"))
L.append(c("S02","ch04 table 4.1","Eligible 524,175 and 1,048,301 events; 6,659 and 13,268 outside modes 0-3; fractions 0.0127038 and 0.0126567; 30 distinct returned circuit/input configurations per job","statistic",EC,
  "Own decoder; eligibility occupation sum 1; configuration key = SHA-256 of decompressed computed_circuit plus computed_input.","Any count differing",True,"confirmed",
  "job-00: 524,288 total, 113 multi-photon, 0 vacuum, 524,175 eligible, 6,659 outside, 0.012703773; job-01: 1,048,576 total, 275 multi, 1,048,301 eligible, 13,268 outside, 0.012656670; 30 configurations each (28 doubles, 2 quadruples).",
  "None.","none"))
L.append(c("S03","ch04 4.1 twelve-mode coefficient table and block-conditioned values","Twelve-mode X/Y sign-odd coefficients as tabulated; block conditioning gives X constant 0.475054/0.475745 and Y sin(2 theta) 0.485083/0.483446","statistic",EC,
  "Own coefficients from decoded counts, both denominators.","Mismatch beyond 1e-6",True,"confirmed",
  "Twelve-mode values equal analysis.json; block-conditioned X0 0.475054/0.475745 and Ys2 0.485083/0.483446. The block-conditioned values are also in job-0x-diagnostics.json endpoint_variants.block_conditioned.",
  "None.","none"))
L.append(c("S04","ch04 4.2 table","Block-conditioned GLS chi-square of the ten sign-odd coefficients: common gain 152.406/355.051 (8 df), linear 138.859/316.065 (6 df), affine 44.450/97.225 (4 df); affine tail p 5.17e-9 and 3.83e-20","statistic",EC,
  "Own GLS with full plug-in multinomial covariance propagated through the 10x64 weight matrix; designs written from the response hierarchy.","Any chi-square differing by more than 1e-3",True,"confirmed",
  "Reproduced to the printed digits: 152.406, 355.051; 138.859, 316.065; 44.450, 97.225; p 5.17e-9, 3.83e-20.",
  "The plug-in Gaussian reference assumes multinomial sampling within each setting; within-job identical configurations do replicate their readout statistic within counting noise (sum 33.0 on 30 and 19.6 on 30), so no overdispersion inflation is warranted.","none"))
L.append(c("S05","README ('rejects a common affine quadrature map'); ch04 4.2 'New result'","Even an unrestricted affine quadrature correction fails; this is a new result","interpretation",f"{EC} and main",
  "Restricted the affine GLS to the six constant/cos/sin(2 theta) coefficients; computed the joint chi-square of the four fourth-harmonic coefficients alone; read the conformance design.",
  "The affine residual carrying weight outside the fourth harmonics, or the repository lacking the fourth-harmonic finding",True,"already-in-repo",
  "The six-parameter affine map saturates the six non-fourth-harmonic coefficients (residual chi-square 0.0 there), so the affine statistic equals the joint fourth-harmonic test exactly: 44.450 and 97.225 on 4 df. docs/design/ascella-signed-coherence-conformance.md line 239 preregistered the coefficient-support question with falsifier 'simultaneous intervals exclude zero', and line 839 records X cos(4 theta) 0.0143 [0.0041, 0.0245] with ideal excluded in job-01's analysis.json.",
  "Any configuration-specific error on the five compiled angles produces fourth-harmonic content, and the five-point grid aliases frequencies congruent mod 5 in 2 theta; the result rules out angle-independent affine calibration and nothing narrower.","none"))
L.append(c("S06","ch04 4.3 table","Block-conditioned direct sign-odd coefficients (constant, c2, s2, c4, s4) and nominal five-endpoint Hoeffding radii as tabulated; sin(2 theta) -0.009602 and -0.010821","statistic",EC,
  "Own sign-odd transform of direct dark D=(n2+n3)/N4; radius sqrt(0.5 ln(1000) sum w^2/N).","Mismatch beyond 1e-6",True,"confirmed",
  "All ten coefficients and radii reproduced (e.g. s2 -0.009602 r 0.006524; -0.010821 r 0.004612).","See S07.","none"))
L.append(c("S07","README ('exploratory direct sign-odd term'); ch04 4.3","The direct readout has an exploratory sign-odd response, dominated by sin(2 theta)","interpretation",EC,
  "Alternative variance model: at each angle the + arms (0,3) share one returned circuit and the - arms (1,2) another, so the within-configuration differences give an empirical per-setting variance with 10 df; t test of each coefficient against that variance. Mode split and correlation with outside-block fraction.",
  "The sin(2 theta) coefficient losing significance under the replicate variance, or tracking the outside-block background",True,"confirmed",
  "Replicate-variance t(10) for sin(2 theta): -7.56 (p 1.9e-5) job-00, -16.54 (p 1.4e-8) job-01; replicate variance is 0.83x and 0.44x the binomial value, so counting noise is not underestimated. The signal sits in mode 3 (s2 -0.00901/-0.01062), not mode 2 (-0.0006/-0.0002); the sign-odd transform of the outside fraction has opposite s2 signs in the two jobs (-0.0022/+0.0050) and D-ideal vs outside fraction has Spearman 0.10/0.17 (n.s.).",
  "Sign is perfectly aliased with compiled configuration: the effect is a difference between two returned meshes per angle, and job-01 re-ran the same 64 compiled circuits, so it replicates a configuration effect rather than testing a sign effect. The coefficient was chosen after inspecting both jobs. The compiled-circuit statistics lie within 2.2e-4 of ideal (registry ascella-signed-coherence-device-diagnostics), so the returned matrices do not predict it. A crossed-compilation acquisition is the falsifier.","new-evidence-candidate"))
L.append(c("S08","ch04 4.3","Sign-correlated theta shift leaves chi2(4) 45.239/39.564; common phi offset leaves 89.217/146.767; effective shift about -0.022 rad","statistic",EC,"Own one-column GLS fits on the direct-odd coefficient vector.","Mismatch",True,"confirmed",
  "45.239/39.564 and 89.217/146.767 reproduced; implied epsilon = asin(4 b)/2 = -0.0206 (job-00) and -0.0219 (job-01).","'About -0.022' matches job-01 only; job-00 gives -0.021.","none"))
L.append(c("S09","ch04 4.3 and 7","The theta shift predicts X0+Xc2 = (1-cos 2 epsilon)/2 >= 0 while the measured relation is negative (job-01 block X0+Xc2 -0.030679, Xc4 0.013974, X(0) -0.016705)","statistic",EC,"Algebra plus own block-conditioned coefficients.","A nonnegative measured X0+Xc2",True,"confirmed",
  "X0+Xc2 = -0.02976 (job-00), -0.030679 (job-01); Xc4 0.013974; sum -0.016705.","None.","none"))
L.append(c("S10","ch04 4.4 table","Between-job equality of configuration-pooled statistics: X 3.329, Y 8.350, direct 25.504 on 10 df; residual correlations 0.9966, 0.9649, 0.8940","statistic",EC,
  "Own pooling by returned configuration within readout, mutation settings excluded, variance v00+v01; repeated with the registered twelve-mode denominator.","Mismatch",True,"confirmed",
  "Block-conditioned: 3.329, 8.350, 25.504 (p 0.0045); correlations 0.9966, 0.9649, 0.8940. Twelve-mode denominator: X 47.73 (p about 1e-6), Y 15.66 (p 0.11), direct 37.29 (p 5e-5).",
  "The table never names its denominator; the package code uses modes 0-3.","none"))
L.append(c("S11","ch04 4.4","Analyzer configuration statistics repeat extremely well between jobs","interpretation",EC,"Same pooled comparison under the registered twelve-mode denominator.","A twelve-mode equality chi-square inconsistent with 10 df",True,"refuted",
  "As stated without a denominator the claim fails: under the registered twelve-mode estimand X equality is 47.73 on 10 df (p about 1e-6). It holds only for the block-conditioned estimand (3.329 on 10).",
  "Outside-block dilution follows execution order and differs between the two orders; conditioning on modes 0-3 removes that order effect, which is why the block-conditioned statistics repeat.","reject"))
L.append(c("S12","ch04 4.4","The direct readout shows a detectable between-job discrepancy","interpretation",EC,"Multiplicity check over the three readouts tested.","Familywise p above the declared level",True,"unproven",
  "Nominal p 0.0045; Bonferroni over three readouts 0.013, which does not pass the 0.01 level the registered endpoints use.","Exploratory; a calibrated familywise level or new data is needed.","none"))
L.append(c("S13","ch04 4.4","Job-01 lag-one outside-count autocorrelation -0.6531; identity Spearman -0.0755","statistic",EC,"Read repeat-comparison.json and recomputed from decoded counts (log(count+1/2)).","Mismatch",True,"already-in-repo",
  "Recomputed -0.653137 and -0.075453; both retained in repeat-comparison.json (sequence, identity) and docs/notes/quandela/strategy.md run row.","None.","none"))
L.append(c("S14","ch04 5.3 rank table","Weighted Jacobian ranks 56/56/64/87 (null 70/70/68/171) at the retained static modes; log likelihood reproduced to about 6e-11","statistic",EC,"Reran mesh_identifiability.py against the pinned checkout.","Rerun disagreement",False,"unproven",
  "Rerun output equals the delivered record to 1e-9 relative. No independent Jacobian was computed.","Numerical ranks depend on threshold and on the fitted point; they are not global identifiability results.","none"))
L.append(c("S15","ch04 5.3; ch08","30 configurations x 3 independent conditioned probabilities bound the data rank by 90, leaving at least 168 kernel directions for 258 parameters","model",EC,"Arithmetic: 30*(4-1)=90; 258-90=168; 258-87=171.","Arithmetic error",True,"confirmed","90, 168 and 171 follow exactly.","None.","none"))
L.append(c("S16","ch04 5.2 table","The PR #449 model table is a faithful transcription of physical-models.json at f0f1788","repo-fact","f0f1788","Nearest-value match of every tabulated number against all floats in the retained record.","A tabulated number with no match within rounding",True,"confirmed",
  "All 36 spot-checked numbers (statistics, LOCO scores, predicted X0+Xc2) match within rounding, e.g. 663.2305, 238.3299, 7.0314, 800.3830.","None.","none"))
L.append(c("S17","ch04 6.1","The omitted-configuration score uses counting variance only and ignores fitted-prediction variance","interpretation","f0f1788 and main","git merge-base: 7b5df53 is not an ancestor of 41d5ef0; read configuration-holdout.json on main.","Main still scoring left-out configurations by counting variance alone",True,"stale",
  "True at f0f1788/41d5ef0. Main's configuration-holdout.json (commit 7b5df53, after 41d5ef0) scores training-only folds in counting plus fitted-prediction variance and supersedes the left-out column of physical-models.json (evidence README).",
  "None; the critique was correct at the snapshot.","none"))
L.append(c("S18","ch04 6.2","Starting each fold from the full-data mode leaks held-out information","interpretation","f0f1788 and main","As S17; read the 'start' field.","Main folds starting from the full-data mode",True,"stale",
  "Main's configuration-holdout.json and heater-drive-holdout.json record start 'zero, training configurations only'.","None.","none"))
L.append(c("S19","ch04 7","Detector-efficiency counterexample at r=2 gives grid coefficients (0.4494382, -0.4943820, 0, 0.04494382, 0)","model","n/a","Own evaluation of x_r on the five-point grid.","Different coefficients",True,"confirmed","0.4494382, -0.49438202, 0, 0.04494382, 0.","Refutes an analytic shortcut only; the package says so.","none"))
L.append(c("S20","README; ch04 8.1","A frozen two-parameter phase-command proxy reaches the X0+Xc2 interval (-0.0210704 in [-0.048306,-0.013053]) but fails the full response (487.660 / 200.073 on 10; LOCO 365.917/77.287, 355.800/75.484); beta (-0.00961065, -0.00902995)","statistic",EC,"Reran phase_command_proxy.py against the pinned checkout.","Rerun disagreement in selected fit or scores",False,"unproven",
  "Selected fit, discrepancies and LOCO summaries reproduce to 1e-6 relative; fold-level optimizer internals (evaluation counts, gradient norms, e.g. fold 25 start 0: 38 vs 12 evaluations) differ from the delivered record under the same library versions, so the README's 'identical except runtime metadata' does not hold across hosts. The interval [-0.0483, -0.0131] is in the conformance design line 968.",
  "Rerun only; no independent likelihood implementation.","none"))
L.append(c("S21","ch04 8.1","A two-parameter shared model can reproduce the famous single relation without explaining the data, so that relation cannot identify a per-configuration mechanism","interpretation","f0f1788 and main","Compared with retained static families and main's drive family.","Repository lacking an earlier model that matches the relation while failing transfer",True,"already-in-repo",
  "The retained static families already predict X0+Xc2 -0.0217 to -0.0261 inside the interval while failing omitted configurations (physical-models.json). Main's drive-linear heater family (heater-drive-holdout.json) reaches standardized held-out 36.1/24.8 against the proxy's 355.8/75.5.",
  "The proxy is a much weaker family than the repository's existing drive model; its failure adds little.","none"))
L.append(c("S22","ch04 8.1","The proxy contract SHA-256 is 3f75f870...1313 and was frozen before the first fit","repo-fact","package","sha256sum of phase-proxy-contract.json; script constant.","Hash mismatch",True,"unproven",
  "Hash matches the script constant. Nothing in the package timestamps the freeze before fitting; the package itself calls this computational ordering, not preregistration.","None.","none"))
L.append(c("S23","README; ch04 8.1; ch07","Applied electrical drive levels remain unobserved","repo-fact","main","Read the registry boundary of the drive-dependent heater claim.","A retained applied-drive record",True,"confirmed",
  "Registry boundary: 'the drive is the returned phase in [0, 2 pi) ... because the passive phase that sets each heater's wrap point is absent from the returned circuit'.","None.","none"))
# ---- chapter 07
L.append(c("C01","README; ch07","State-dependent event selection can violate a conditional sum rule with fixed valid measurements and perfect preparations (S=diag(1,1/2), E=diag(0,1/2): p+=p-=1/3, residual -1/3)","model","n/a","Exact Fraction arithmetic.","Residual 0",True,"confirmed",
  "p+=p-=1/3, pf=0, pg=1, residual -1/3 exactly; 0 <= E <= S <= I holds.","Standard post-selection nonlinearity. docs/notes/quandela/bdsc-acceptance-diagnostics.md already models conditional distributions with acceptance effect D and 0 <= G <= D and shows the reported deficit's sign and size, so the mechanism is already in the repository.","none"))
for id,st,ev in [
 ("C02","BDSC diagnostic: 96 instances, 48 matched pairs with identical compiled circuits, heterogeneity 553 on 45, 45.8 on 45 on target support, common shift about -0.0048","Registry statements at 41d5ef0 carry 553 on 45, 48 identical pairs and 45.8 on 45."),
 ("C03","Mode-5 veto reduces heterogeneity to 58.0 on 45","Registry: 'falls from 553 to 58.0 on 45 degrees of freedom (p 0.09)'."),
 ("C04","Stationarity case 66.1 on 45, inconclusive","Registry: '66.1 on 45 degrees of freedom (p 0.022...)'."),
 ("C05","Drift series: mean von Neumann ratio 1.674, exact p 0.056 over 5040 orderings; class mean 0.3928 to 0.4042; all 56 sum residuals negative, mean -0.199","Registry carries each number; 56 = 4 groups x 2 sums x 7 runs."),
 ("C06","Tuna-17 pilot 27 circuits; readout reference 0.0735 to 0.0453 exceeding 0.02 stop","Numbers present in the registry; context read at grep level."),
 ("C07","IQM Garnet double difference -0.0538 +- 0.0124 at phi 0.1; -0.132 +- 0.026 at 0.3 with scaling assumption","Numbers present in the registry; context read at grep level."),
 ("C08","Folded-QPE coherent arm beats feed-forward by 5.8 to 10.9 points","Registry: '+5.8 to +10.9 points of terminal accuracy'."),
]:
    L.append(c(id,"ch07",st,"repo-fact",PIN,"Search of research_state.json and the linked notes at 41d5ef0.","Number absent or attached to a different quantity",True,"already-in-repo",ev,"Transcription; no recomputation from raw data.","none"))
L.append(c("C09","ch07 IBM paragraph","-1.130 rad over 4.392 us gives |df| about 4.10e4 Hz; alias spacing about 227.7 kHz","statistic","results/live/2026-10-15T030748.903241Z","Arithmetic from the retained coherence-analysis.json values.","A value that does not round to 4.10e4 Hz",True,"confirmed",
  "coherence-analysis.json: rotation -1.1302658 rad, idle_rate_rad_per_us -0.2573465, hence exposure 4.3920 us and |df| = 0.2573465e6/(2 pi) = 40,958 Hz, which rounds to 4.10e4 Hz; alias spacing 1/4.392e-6 s = 227.69 kHz. The rounded inputs 1.130 and 4.392 alone give 40,948 Hz (4.09e4); the chapter's figure follows the unrounded source. docs/notes/topics/relativistic-metrology-scale.md line 58 reads '-1.130 rad, a 41.0 kHz detuning'.",
  "The principal-branch magnitude does not identify the detuning source; the package says so.","none"))
L.append(c("C10","ch04 8.2-8.3; ch07 experiment table","A crossed design with execution parity as a factor separates setting, compilation, order and budget","proposal","n/a","Tested whether outside-block counts carry a fixed parity effect.","A significant even/odd difference in outside fraction",True,"unproven",
  "Parity means do not differ in either job (Mann-Whitney p 0.49 and 0.50) although lag-1 is -0.66/-0.65: the high/low alternation slips phase several times per job (job-00 pattern 1001010101010110101011001...).",
  "A fixed parity term is the wrong nuisance model; the design should cross the alternation phase or the predecessor transition, and record per-iteration timestamps.","none"))
# ---- pasted summary
L.append(c("Pa1","pasted (a)","Ascella holds 128 compressed iteration records over two jobs","repo-fact",EC,"Own decoder.","Different count",True,"confirmed","64 results_list entries per job, each with ':PCVL:zip:' BSCount, computed_circuit and computed_experiment.","None.","none"))
L.append(c("Pa2","pasted (a)","Job-01 lag-one statistic -0.653137 in execution order","statistic",EC,"Lag-1 autocorrelation of log(count+1/2) outside-block counts.","Mismatch",True,"already-in-repo","-0.653137; retained in job-01-diagnostics.json serial and repeat-comparison.json sequence (preregistered, supported).","None.","none"))
L.append(c("Pa3","pasted (a)","Job-01 lag-one statistic +0.280039 in design order","statistic",EC,"Same statistic with job-01 reordered by design_index.","Mismatch",True,"confirmed",
  "+0.280039. Its asymptotic two-sided p under exchangeability (sd 1/8) is 0.025, so it is itself not null at 0.05, uncorrected.",
  "Weak residual structure among design neighbors in job-01 (28 of 63 design-adjacent pairs share execution parity, so it is not a parity artifact); one uncorrected exploratory statistic.","none"))
L.append(c("Pa4","pasted (a)","Cross-job Spearman -0.075453 by setting identity","statistic",EC,"Spearman of outside counts matched by setting name.","Mismatch",True,"already-in-repo","-0.075453 (asymptotic p 0.55); retained as repeat-comparison.json identity (preregistered, not supported). Removing each job's parity mean leaves -0.089.","None.","none"))
L.append(c("Pa5","pasted (a)","Cross-job Spearman -0.390040 by positional join","statistic",EC,"Spearman of outside counts matched by execution position.","Mismatch",True,"confirmed",
  "-0.390040 (asymptotic p 0.0014).","The positional join pairs different settings; its significance shows that both orders share position-locked structure, not any setting effect.","none"))
L.append(c("Pb1","pasted (b)","60 first/last pairs (30 per job), 120 occurrences, 8 middle occurrences excluded","statistic",EC,"Grouping by decompressed computed_circuit + computed_input.","Different counts",True,"confirmed","Each job has 28 doubles and 2 quadruples: 30 pairs, 4 middles per job.","See Pb5.","none"))
L.append(c("Pb2","pasted (b)","Conditional hypergeometric two-sided probability-ordered test with Holm at 0.05 rejects 40/60 (24/30 job-00, 16/30 job-01)","statistic",EC,"Exact test with Python integers (math.comb weights, Fraction tail), Holm over 60.","Different rejection count",True,"confirmed","40/60; 24 job-00, 16 job-01 (per-job Holm over 30: 24 and 17). Largest rejected p 7.05e-4.","See Pb5.","none"))
L.append(c("Pb3","pasted (b)","Largest change 4/8192 -> 586/8189","statistic",EC,"Max absolute log ratio over pairs.","Different pair",True,"confirmed","theta3-direct-arm0 (position 36) 4/8192 -> theta3-direct-arm3 (position 39) 586/8189, job-00.","Positions 36 and 39 have opposite parity inside one alternation run.","none"))
L.append(c("Pb4","pasted (b)","Two pairs have different requested parameter tuples despite identical returned configuration records","repo-fact",EC,"Compared rounded circuit_params within each group.","No differing tuple",True,"confirmed","theta0-x-arm0 vs theta0-y-arm3 in each job (the theta=0 X and Y analyzers compile to one mesh).","None.","none"))
L.append(c("Pb5","pasted (b): configuration reading of the test, not stated in the summary","Reading the 40/60 rejections of the independent-binomial (common p per returned configuration) null as evidence that a returned configuration fails to repeat its outside-block rate; the hypergeometric arithmetic and the rejection of the equal-p null stand","model",EC,
  "(i) Null family: the same exact test and the realized Holm cutoff on within-job pairs of different configurations at the same gaps; (ii) execution covariate: predict each log rate by the mean of its lag-2 neighbors (same alternation phase, different settings), estimate quasi-Poisson dispersion, rerun an overdispersed log-Wald first-vs-last test with Holm; break-even dispersion; (iii) parity split in job-01; (iv) in-block readout statistic replicate test.",
  "Different-configuration pairs rejecting much less often than configuration pairs, or rejections surviving a dispersion fitted to execution order",True,"refuted",
  "Different-configuration pairs at the same gaps reject at 116/159 (73%) job-00 and 452/759 (60%) job-01, against 24/30 and 16/30 for configuration pairs. The lag-2 predictor explains 77% and 65% of log-rate variance; dispersion is 71 and 248; the overdispersed test rejects 0/30 in each job, and the first rejection needs dispersion below 24.0 (job-00) and 33.7 (job-01). Job-01 same-parity and opposite-parity pairs reject alike (8/14, 8/16). In job-00 all 30 pairs straddle opposite parity (gaps 1 or 3, plus 7 and 51). Configuration-mate residuals after the predictor have Spearman 0.11 and 0.26 (n.s.). The in-block readout statistics of the same pairs agree within counting noise (33.0 on 30, 19.6 on 30).",
  "The 40/60 count measures execution-order overdispersion of the outside-block rate, the same process repeat-comparison.json already records (sequence supported, identity not supported).","reject"))
for id,st,v in [("Pc1","638 retained IBM PUBs","638 pub_*.json files under results/live/*/raw/<job>/ across 36 jobs"),
                ("Pc2","4,586 classical-register descriptions","4,586 register entries summed over PUBs"),
                ("Pc3","31,145,280 stored register entries","31,145,280 bitstrings summed over registers (36,226,688 bits)"),
                ("Pc4","2,116,928 aligned PUB positions","2,116,928 = sum of per-PUB num_shots; every register in every PUB has len(bitstrings) == num_shots")]:
    L.append(c(id,"pasted (c)",st,"repo-fact",f"{PIN} and {MAIN}","Independent walk of results/live/**/raw/*/pub_*.json.","Different count",True,"confirmed",v+"; identical at 41d5ef0 and main.","None.","none"))
doc=dict(schema="delivery-claim-ledger-v1",delivery="DAS MERGUS companion package (chapters 01, 04, 07, 08, 09; analysis/statistics; analysis/audit_corpus.py) and the pasted review summary claims (a)-(c)",reviewed_utc="2026-10-25T10:00:00Z",claims=L)
json.dump(doc,open(OUT,"w"),indent=1,ensure_ascii=False); open(OUT,"a").write("\n")
import collections; print(len(L),collections.Counter(x["verdict"] for x in L),collections.Counter(x["action"] for x in L))
