# Nominal-one destination comparison: uncertainty contract

The [three-job case](../../design/tuna-readout-destination-one-admission.md) has a separate primary
endpoint from the deadline-limited six-job case. The [conditional boundedness derivation](destination-response-uncertainty.md)
applies with one nominal preparation, three physical qubits and four early/final cells: 12 response
contrasts and 12 baseline endpoint contrasts. The selected cells describe marginal pairs, rather than
the joint law across all measured qubits.

For job j and shot t, X[j,t] indicates one selected early/final cell. The filtration contains the
complete earlier acquisition history. Write p[j,t] = E[X[j,t] | F[j,t-1]] and
P[j] = sum_t p[j,t]/4096. The targets are D = P[rotated] - (P[before]+P[after])/2 and
R = P[after]-P[before]. The empirical estimators use the same deterministic weights. The baseline
arithmetic average remains the declared reference even when queue delays make wall-clock spacing unequal.

Conditional Hoeffding boundedness gives

    Pr(|sum w*(X-p)| >= r) <= 2 exp(-2*r^2/sum(w^2)).

For D, sum(w^2)=3/(2*4096); for R, sum(w^2)=2/4096. A union bound across 24 contrasts and two tails
at alpha=0.01 gives

    rD = sqrt(3*log(48/0.01)/(4*4096)) = 0.039396318627, rounded upward;
    rR = sqrt(log(48/0.01)/4096)        = 0.045490950328, rounded upward.

The [frozen successor analyzer](../../../scripts/qi_tuna_destination_one_analysis.py) computes both
radii with 60-digit Decimal precision and rounds upward to 12 decimal places. The simultaneous
guarantee allows arbitrary adapted shot dependence. The targets are realized predictable averages;
they differ from stationary means, prepared-state populations and causal treatment effects. The
perfectly correlated Bernoulli example in the derivation explains why thousands of shots can
concentrate around a history-dependent target without creating independent job interventions.

Both practical margins equal 0.10. The margins define an engineering diagnostic, rather than a
calibrated device specification. Intervals intersect the known contrast range [-1,1]. All 12 endpoint
intervals must fit in the closed margin before a response decision qualifies. Then all 12 response
intervals inside the closed margin establish bounded descriptive equivalence; any response interval
strictly outside supports a selected descriptive departure. Overlap or an uncertified endpoint gives
inconclusive within budget. Missing required files give implementation route unavailable; malformed,
partial, charged, misbound or incorrectly ordered acquisitions give protocol inadmissible.

On the simultaneous good event, |R| <= 0.009018099344 for every selected cell guarantees endpoint
admission. Every |D| <= 0.021207362746 guarantees equivalence, while a selected
|D| > 0.178792637254 guarantees departure when endpoints admit. The probability of a wrong
classification together with the corresponding separation conditions is at most 0.01. Conditioning
on a rare realized separation event need not preserve that bound. Missing or failed jobs remain in
the acquisition record; favorable completion selection and replacement jobs are prohibited.

The endpoint screen cannot constrain a coincident intermediate transient. Sensitivity expansions by
gamma=0,0.02,0.05 remain unverified assumptions and leave the primary decision unchanged. Every report
retains unresolved attribution and refuses automatic physical continuation. Acquisition mapping,
analog timing, integration, discrimination, calibration and apparatus memory remain separate
evidence obligations. The three jobs contain only three intervention units. The previously acquired
nominal-zero prefix can support a labeled retrospective comparison; joining the two cases cannot
repair the old six-job primary endpoint or establish a prospectively controlled preparation effect.
