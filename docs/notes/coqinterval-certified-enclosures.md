# CoqInterval: certified numerical premises for count-based inference

Primary tool: Guillaume Melquiond and contributors, **CoqInterval 4.11.5**.
[Project documentation](https://coqinterval.gitlabpages.inria.fr/),
[versioned source archive](https://coqinterval.gitlabpages.inria.fr/releases/interval-4.11.5.tar.gz),
[upstream repository](https://gitlab.inria.fr/coqinterval/interval).
The versioned archive, its `README.md`, `INSTALL.md`, `AUTHORS`, `COPYING`,
`src/Tactic.v`, and selected correctness lemmas were inspected.

## Usable interface and theorem boundary

[P] Import `Interval.Tactic` to use `interval` for inequalities over real
expressions. `interval_intro expression lower` or `upper` introduces a proved
one-sided enclosure. Supported operations include `sqrt`, `ln`, `exp`, and
integer powers. Numeric exponents and documented domain restrictions matter.
`root` requires an equality constraining the root, or creates that equality
as a proof obligation; root enclosure does not supply a statistical
interpretation for the root.

[P] In `src/Tactics/Interval_helper.v`, `eval_bisect_correct` turns a Boolean
successful numerical check into the reified real goal under the reified
hypotheses. `eval_bisect_contains_correct` proves containment in a proposed
interval. `eval_bisect_plain_correct` supplies a containment theorem for the
interval computed by the lookup procedure. These are the relevant soundness
interfaces for a certificate, rather than a printed floating-point estimate.

[I] The terminal-channel argument needs a proved comparison between the
specified concentration radius and rational `21/1000`. A frozen real
expression involving logarithms and square roots is a direct candidate for
`interval`; the concentration and union-bound theorems remain separate.

[I] The fixed-sample Clopper-Pearson gate can avoid trusting a beta-quantile
implementation. Let an untrusted search propose outward rational endpoints,
then certify binomial-tail inequalities. First require integer `n>=1` and
`0<=k<=n`, rational `0<=l<=u<=1`, and rational per-tail error allocation
`0<alpha_tail<1`. Declare the tail and experiment family; the sum of all
allocated tail errors must stay within the chosen family error budget.
For `0<k<=n`, a conservative lower
endpoint `l` can be checked by
`sum(j=k..n) choose(n,j) l^j (1-l)^(n-j) <= alpha_tail`.
For `0<=k<n`, a conservative upper endpoint `u` can be checked by
`sum(j=0..k) choose(n,j) u^j (1-u)^(n-j) <= alpha_tail`.
The domain checks are essential: at `n=2,k=1`, the displayed polynomials
at `l=3` or `u=-2` equal `-3`, so a bare inequality would admit impossible
probability bounds. Prove monotonicity and endpoint direction on `[0,1]`; handle `k=0` with lower endpoint
zero and `k=n` with upper endpoint one. A rational tail checker may use exact
arithmetic; Interval is useful when exact sums become expensive or when
transcendental premises enter. Performance at 8192 shots remains unmeasured.

[I] Remaining probability obligations include the Bernoulli sampling law,
binomial-tail coverage, family allocation, and a union bound. Adaptive
stopping requires an additional simultaneous-in-time theorem. Interval's
numerical soundness does not establish those statistical assumptions or
coverage statements. Bind the final endpoint witnesses to the integer
counts, policy digest, inequality direction, and rational margin predicate.

## Foundations and computational trust

[P] `i_prec` controls emulated precision; the README says the default may use
machine floating-point numbers when available. `i_native_compute` selects
native evaluation instead of VM evaluation. The inspected helper uses
`vm_cast_no_check`/`native_cast_no_check` during tactic computation, including
an abstracted proof check in its ordinary reduction route.

[I] Record the selected arithmetic/evaluation mode and retain independent
`rocq check` output, rather than inferring trust from the tactic returning
success. Audit imported assumptions for the actual theorem and precision
mode. Standard real foundations, the Rocq kernel, arithmetic implementations,
and any execution/extraction boundary are distinct entries. This pass did
not compile the library or print assumptions for an instantiated enclosure.

[P] Flocq is already an explicit dependency. The README recognizes its
`Generic_fmt.round` with `FLT_exp`, as well as its integer-rounding operators.
These interfaces can express a rounding model, but they do not prove that an
arbitrary SciPy beta quantile implements that model. Proposing and checking
rational endpoints needs no claim about the internal correctness of SciPy.

## Version, rights, and reading scope

[P] `INSTALL.md` declares Coq >=8.13.1, MathComp >=1.12, Flocq >=3.2,
Coquelicot >=3.1, and BigNums. These minimum declarations do not establish a
tested dependency combination with the project's Rocq 9.1.1. Compatibility
and numerical performance remain untested in this pass.

The 4.11.5 archive's `COPYING` contains the CeCILL-C software license, and
`README.md` applies that license to the package. The main author is Guillaume
Melquiond; `AUTHORS` also credits Érik Martin-Dorel, Pierre Roux, Thomas
Sibut-Pinote, and the CoqApprox contributors. The software license supplies
software rights under its terms; it does not license unrelated publications.
The source archive is a reproducible primary reference, with its acquisition
hash and byte count recorded separately. The project PDF allowlist does not
turn a software-source license into a PDF redistribution decision.

Reading scope: full README invocation/fine-tuning sections and prerequisites;
license identity and authors; `src/Tactic.v` imports/options; named helper
definitions, soundness statements/proofs, and reduction code. Full numerical
algorithms and transitive arithmetic proofs remain outside this reading pass.

Unchanged source archive: [interval-4.11.5.tar.gz](../source_archives/interval-4.11.5.tar.gz).
Retrieval: https://coqinterval.gitlabpages.inria.fr/releases/interval-4.11.5.tar.gz

Archive SHA-256: `639413394d3012aaa7e78122e4abd4a4dfc459ba6052b5a1a8c98fe2a2485a69`.
