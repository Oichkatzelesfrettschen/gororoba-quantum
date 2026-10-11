# Factoring and the Cayley-Dickson ladder

Cayley-Dickson structure does not carry Shor's algorithm for RSA-2048 on these
devices, and no folding of zero-divisor chunks changes that. Two independent
reasons:

- The reference construction (Gidney 2025) needs 5,755 times the hardware's
  physical qubit count and about seven orders of magnitude more gate volume than
  these devices run, before any error-correction overhead. It is the cost of
  one construction, not a proven lower bound, and its author sees no route to
  another order of magnitude in qubits.
- No product of basis left multiplications is a nontrivial modular multiplier,
  at any dimension: every product is a signed XOR translation, and a
  multiplier x -> a x mod N fixes 0, which a nontrivial translation never does.
  The products also form a 2-group of exponent 4, while order finding needs
  ord_N(a), which for a random base modulo an RSA semiprime is on the scale of
  N; the at most 16 bases with ord_N(a) <= 4 are a fraction about 2^-2044 of
  the units.

Cayley-Dickson dimension 2048 = 2^11 is an 11-qubit index register; RSA-2048 is
a 2048-bit modulus. The numbers coincide and the scales do not.

The algebra connects to the hidden-subgroup family over F_2^n, where design C
at dim 8 already is Bernstein-Vazirani, and to certified non-Clifford benchmarks of the
gate class that dominates factoring cost. The checks behind each claim are
named inline; literature notes live under literature/notes/.

`HYBRID_SHOR.md` carries the implemented host/QPU architecture, Boolean
coefficient derivation, exact bounded synthesis, compiler evidence, admission
falsifiers, and roadmap.

## Reference baseline

Gidney 2025 (arXiv:2505.15917, note literature/notes/2505.15917.md) is the
reference construction. It proves no lower bound; its costs are those of one
construction. At n = 2048 with 0.1% uniform gate error, a 1 us surface-code
cycle and a 10 us reaction time, it needs:

| quantity | RSA-2048 (Gidney 2025, Table 5, Sec. 3.2) | one Heron r2 backend |
|---|---|---|
| logical qubits | 1399 (1280 of them the exponent register) | none; no error correction |
| physical qubits | 897,864 | 156 |
| Toffoli gates | 6.5e9 per factoring, about 7.1e8 per shot | -- |
| two-qubit gate error | 1e-3 assumed | median CZ 1.9e-3 to 2.7e-3 (live_run.py, 2026-10-10) |
| runtime | 12.07 h per shot, 4.96 days expected | -- |

The circuits in this repository give the practical scale, so far in
simulation only: no job has run on hardware. The dim-32 associator spectrum is
96 CZ on 5 qubits, at joint ESP 0.77 on the best patch of three backends in the
dry run of 2026-10-10T16:59:44Z. Its noise-model histogram, simulated from that
calibration, sits near the simulated noise floor: it is closer to the true
prediction than to the sign-flip prediction by a TVD margin of only 0.062
(0.181 against 0.243), and its TVD to the simulated sign-flip control histogram
is 0.131. A submitted and collected run is what turns this into a hardware
bound. A computation of 7.1e8 Toffolis per shot is about seven orders of
magnitude past this circuit size, before any error-correction overhead.

## What decomposes and what does not

Per the Gidney note:

- **Splits:**
  - the s + 1 Ekera-Hastad shots, which are independent and recombined
    classically;
  - the classical precomputation of the prime set and discrete-log tables;
  - the prime-by-prime serialization of the residue arithmetic;
  - the quantum Fourier transform, which is a semiclassical frequency
    measurement of n - 1 adaptive phase gates and is negligible in cost.
- **Does not split:** the quantum core. All m = 1280 exponent qubits stay
  coherent from the first lookup to the final frequency-basis measurement, about
  4.45 million exponent-addressed lookups per shot, and every saving in the
  construction rests on each multiplier g^(2^k) mod N being a classical
  constant.
- **Splitting the exponent into independent chunks** needs a
  quantum-by-quantum modular multiplication to recombine the partial products,
  and that removes the classical-constant property. The note rates this
  moderate, because the paper does not analyze a split.

## Cayley-Dickson multiplications form an exponent-4 2-group

`verify.check_left_mult_group` pins the following for dims 4 through 64.

**Proved for every n.**
- Every element of G_n = <L_{e_m}> is a signed XOR translation D P_a: each
  L_{e_m} maps |x> to +/-|m XOR x>, and products keep that form.
- Every element has order 1, 2, or 4: (D P_a)^2 = D D^(a) is diagonal and
  squares to the identity. G_n is therefore a 2-group of exponent dividing 4.

**Computed for the listed dimensions, unproved beyond them.**
- The translation part maps G_n onto F_2^n with kernel H, the +/-1 diagonals
  in G_n. Schreier's lemma with transversal {L_{e_a}} generates H by the
  diagonals L_{e_{a^b}}^{-1} L_{e_a} L_{e_b}, the associator phases of design
  C, and H is abelian, so log2 |H| is the F_2 rank of their sign vectors.
- That rank is 1 at n = 2 and 2^(n-1) for n = 3 through 6 (check_left_mult_group;
  the survey's sympy computation extends it to n = 8), with every vector of
  algebraic degree at most n - 2. So |G_n| = 2^(n + 2^(n-1)) at those
  dimensions: 128 for the octonions, 4096 for the sedenions, 2^38 at dim 64, and
  8 (Q8) at n = 2.
- Enumeration of the whole group confirms the order and the exponent through
  dim 16. Schreier's lemma names generators of H; the rank formula for every n
  needs a proof this note does not have.

**Consequence for order finding.**
- Phase estimation on x -> a x mod N needs a unitary of order r = ord_N(a).
- No element of G_n has order beyond 4, at any dimension, 2048 and 4096
  included. This rules out random bases, whose order is on the scale of N;
  the obstruction that holds for every base is the next one.
- A multiplier x -> a x mod N fixes 0, and a signed XOR translation D P_t sends
  |0> to +/-|t>. So the only translation among multipliers is t = 0, which is
  the identity, a = 1. No single element of G_n is a nontrivial multiplier.

**Linear combinations.** "Folding zero-divisor chunks" means a linear
combination of unitaries over G_n. A zero divisor's L_a = L_{e_i} + L_{e_j} is
one such combination with two terms. The real span of G_n is every matrix at
n = 3, 4, 5, where H's diagonals have full real rank 2^n, so an LCU can
represent a modular multiplier there. G_2 = Q8 spans 4 of the 16 dimensions of
4 x 4 matrices. Dimensions beyond 32 remain unchecked. A failed span test means
that no nonzero exact representation exists; the coefficient bound below
remains a necessary condition rather than an existence result.

**Effective-normalization floor.** Let P_pi be a permutation, let beta be
nonzero, and write an exact scaled representation over signed XOR translations
as

```text
beta P_pi = sum_g c_g U_g,
U_g |x> = sigma_g(x) |x XOR t_g>,  sigma_g(x) in {+1,-1}.
```

Define the displacement fiber S_t = {x : pi(x) XOR x = t}, let T count the
nonempty fibers, and set lambda = sum_g |c_g|. Grouping coefficients by t gives

```text
sum_{g:t_g=t} c_g sigma_g(x) = beta  for x in S_t.
```

Choosing one x from each nonempty S_t and applying the triangle inequality
forces `sum_{g:t_g=t} |c_g| >= |beta|`. The displacement classes partition the
LCU terms, so

```text
lambda >= |beta| T.
```

Thus the scale-invariant effective normalization obeys
`lambda/|beta| >= T`. For a normalized input |b>, the standard LCU good branch
has probability `|beta|^2/lambda^2 <= 1/T^2`. The probability is
input-independent because P_pi is unitary. Repeated raw post-selection needs
order `(lambda/|beta|)^2` trials. Standard amplitude amplification needs order
`lambda/|beta|` block-encoding calls and therefore at least order T calls. The
bound supplies no matching upper bound: PREPARE, SELECT, coefficient lookup,
and reflections can add cost, and lambda can exceed |beta| T.

**Two-term zero divisors behave differently.** `select_circuit` implements the
two translations L_{e_i} and L_{e_j}, with lambda = 2. On a normalized input
|b>, the selected branch has probability `||(L_{e_i}+L_{e_j})b||^2/4`.
An annihilator gives probability zero and its bright control gives probability
one. The zero-divisor operator is singular, so the state-dependent bright/dark
result does not transfer to the unitary modular-permutation case.

**Base two has an exact exponential displacement bound.** Let N be an odd
n-bit modulus and let pi implement `2x mod N` below N and identity on unused
register states. For every `0 <= x <= (N-1)/2`, reduction does not occur and

```text
pi(x) XOR x = (x << 1) XOR x.
```

The GF(2) map `I + left_shift` is injective: the truncated shift L is nilpotent
and `(I+L)^-1 = I + L + ... + L^(n-1)`. The `(N+1)/2` inputs therefore carry
distinct displacements:

```text
T >= (N+1)/2 > 2^(n-2).
```

Every nonzero exact scaled signed-XOR LCU for the base-two family consequently
has exponential effective normalization `lambda/|beta|` and raw success at
most `4/(N+1)^2`. For the Mersenne modulus
`N = 2^n-1`, multiplication by `2^k` is a cyclic rotation R^k. The kernel of
`I+R^k` has dimension `gcd(n,k)`, which gives the exact count
`T = 2^(n-gcd(n,k))`; doubling has `T = 2^(n-1)`. The direct circuit for the
same multiplier uses only `n-gcd(n,k)` controlled swaps. The exponential LCU
floor therefore measures a mismatch between arithmetic and the signed-XOR
dictionary, not intrinsic circuit complexity.

**The exponential law does not cover every base.** For `N = 2^n-1`, the
multiplier `a = -1 mod N` has only the displacements 0 and `2^n-1`. Its order is
two and Shor's factor extraction returns the trivial pair 1 and N. A stronger
linear-displacement counterfamily sets `q = 2^m+1`, `N = 3q`, and `a = 2q+1`.
The multiplier acts by the five shifts `0`, `+q`, `-q`, `+2q`, and `-2q`
according to `x mod 3` and the reduction interval. Carry and borrow masks give

```text
T = 3m-2  for even m,
T = 3m+1  for odd m.
```

For even m, a has order two and `gcd(a-1,N)=q`, `gcd(a+1,N)=3`, so the even-m
subfamily supplies useful factor-yielding bases. For odd m, a has order three,
so standard Shor post-processing rejects the odd order. The full counterfamily
refutes a universal exponential displacement claim without weakening the
base-two theorem. The detailed carry-mask derivation, source witnesses,
exclusion argument, and overlap count live in
`literature/notes/open_gororoba_survey_deep_notes.md`.

**Signed Mersenne powers also have a direct circuit boundary.** For every
`1 <= x < 2^n-1`, multiplication by `-2^k` is a cyclic rotation followed by
one's-complement inversion. The direct controlled circuit therefore uses the
positive rotation's Fredkin network plus `n` controlled X gates on the
nonzero-residue subspace used by order finding. One's-complement inversion
exchanges the all-zero and all-one bit strings. The identity-padded
full-register permutation restores those two endpoints with a controlled
Gray-path transposition of `2n-1` basis edges. Both circuits use zero scratch
qubits, while their explicit domain labels prevent the subspace circuit from
claiming full-register equality.

**Executable evidence and call path.** `modular_permutation` defines the
identity-padded arithmetic map. `modular_displacement_profile` validates the
complete-register bijection and partitions it by `input XOR output`.
`_verify_xor_displacement_profiles` checks all 127 odd base-two moduli through
eight bits, 35 Mersenne rotations, seven Mersenne reflections, and every branch
set, total, multiplicative order, and even-m extracted factor for 11 members of
the linear-T family through m = 12. The verifier also rejects a mutated
non-bijection. The circuit path remains separate:

```text
designs._verify
  -> designs._check_design_b
     -> designs.design_b_zero_divisor
        -> designs.lcu_witness
           -> select_lcu.sparse_pair_prep
           -> select_lcu.select_circuit
              -> select_lcu.joint_select_signs -> cd_core.cd_sign

modular_arithmetic._verify
  -> modular_arithmetic._verify_xor_displacement_profiles
     -> modular_arithmetic.modular_displacement_profile
        -> modular_arithmetic.modular_permutation
        -> modular_arithmetic.xor_displacement_profile
     -> modular_arithmetic.modular_permutation
     -> modular_arithmetic.xor_displacement_profile

verify.main
  -> verify.check_left_mult_group
     -> verify._schreier_sign_vector
     -> verify._f2_basis
     -> verify._group_by_enumeration

order_finding.order_finding_plan
  -> factoring.make_order_finding_plan
  -> modular_arithmetic.multiplier_profile
     -> modular_arithmetic.modular_permutation

hybrid_shor.main
  -> hybrid_shor._plan_payload
     -> factoring.classical_precheck
     -> order_finding.order_finding_plan
  -> hybrid_shor._simulate_payload
     -> hybrid_shor._plan_payload
     -> order_finding.factor_order_finding
        -> order_finding.order_finding_plan
     -> hybrid_shor._decoded_payload -> factoring.decode_counts
```

The distinct circuit and arithmetic paths prevent a two-term zero-divisor
circuit from serving as evidence for an arithmetic LCU. GNU cflow parses C,
produces C-parser diagnostics on the Python modules, and supplies no usable
call graph. Cscope supplies lexical text references only; Python definitions
and reliable caller attribution remain absent. `scripts/python_call_graph.py`
supplies a deterministic, conservative static direct-call map under the Python
source version shared by Ruff and mypy in `pyproject.toml`. Compiler symbol
tables and an explicit lexical binding inventory suppress module attribution
for parameters, assignments, local imports, loop, with, exception,
comprehension, nested-definition, and global-rebinding shadows. The mapper
attributes calls inside every comprehension form across pre- and post-PEP 709
interpreters, skips postponed and function-local annotations, records stable
bare decorators as implicit calls, and invalidates exports assigned or deleted
through direct repository-module aliases. Executable positive and negative
fixtures enforce the boundaries and reject syntax newer than the configured
Python target. The mapper explicitly excludes module-initializer calls,
dynamic and class-method dispatch, nested function, lambda, and class bodies,
function-local import flow, decorated exports, reflective mutation, and calls
through values. cProfile caller and callee tables confirm the dynamic
displacement-verifier path.

The instrumented capture uses Python 3.14.7, GNU cflow 1.8, and cscope 15.9 and
scans all 15 Python modules. The conservative AST map contains 255 top-level
functions and 490 distinct repository-local edges. The five factoring and LCU
roots reach 114 functions and 208 edges in union. Python 3.11.17, 3.13.15, and
3.14.7 produce byte-identical maps with SHA-256
`368cc5e562907f7590b9e16ec857ba466ea7e9ae5b0da3ed762beec2e6bb7505`.
The corrected scope adds ten executable comprehension edges to the earlier map.
Direct monkey-patching in `runtime_contracts.py` invalidates twelve otherwise
stable edges to `live_run.select` and `live_run.configure_sampler`, so the net
map loses two edges while the root union gains two functions and eight edges.
GNU cflow exits zero but emits 1,784 C-parser diagnostics and zero graph lines.
Cscope builds without diagnostics, but its four queries for
`modular_displacement_profile` return six
lexical rows, one false definition, one false callee, and five unreliable caller
rows. cProfile records 214,075 calls: 174 calls to
`modular_displacement_profile`, 186 to `modular_permutation`, and 189 to
`xor_displacement_profile`. Its caller and callee tables show 174 profile calls
through `modular_displacement_profile` plus 12 direct permutation calls and 15
direct profile calls from `_verify_xor_displacement_profiles`. The verifier's
cumulative time is host-specific; the versioned call counts and relationships
define the replayable observation.

The Bash capture keeps every generated index and profile in a temporary
directory and removes the directory on exit:

```bash
(
  set -eu
  analysis_tmp="$(mktemp -d)"
  trap 'find "$analysis_tmp" -type f -delete; rmdir "$analysis_tmp"' EXIT
  PYTHON="${PYTHON:-$(command -v python3)}"
  mapfile -t analysis_files < <(rg --files gororoba_quantum -g '*.py' | sort)

  "$PYTHON" --version
  cflow --version
  cscope --version

  cflow --no-preprocess --main=_verify_xor_displacement_profiles \
    "${analysis_files[@]}" >"$analysis_tmp/cflow.out" \
    2>"$analysis_tmp/cflow.err"
  wc -l "$analysis_tmp/cflow.out" "$analysis_tmp/cflow.err"

  cscope -b -q -k -f "$analysis_tmp/cscope.out" "${analysis_files[@]}"
  for query_kind in 0 1 2 3; do
    cscope -d -L -f "$analysis_tmp/cscope.out" \
      "-$query_kind" modular_displacement_profile
  done

  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" scripts/python_call_graph.py \
    >"$analysis_tmp/python-call-graph.tsv"
  sed -n '1,3p' "$analysis_tmp/python-call-graph.tsv"
  rg '^root' "$analysis_tmp/python-call-graph.tsv"

  for interpreter_name in python3.11 python3.13 python3.14; do
    if call_graph_python="$(command -v "$interpreter_name")"; then
      versioned_map="$analysis_tmp/python-call-graph-$interpreter_name.tsv"
      PYTHONDONTWRITEBYTECODE=1 "$call_graph_python" \
        scripts/python_call_graph.py >"$versioned_map"
      "$call_graph_python" --version
      sha256sum "$versioned_map"
    fi
  done

  profile_path="$analysis_tmp/displacement.prof"
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/gororoba_quantum" \
    "$PYTHON" - "$profile_path" <<'PY'
import cProfile
import sys

from modular_arithmetic import _verify_xor_displacement_profiles

profiler = cProfile.Profile()
profiler.runcall(_verify_xor_displacement_profiles)
profiler.dump_stats(sys.argv[1])
PY
  "$PYTHON" - "$profile_path" <<'PY'
import pstats
import sys

statistics = pstats.Stats(sys.argv[1]).strip_dirs().sort_stats("cumulative")
selector = "_verify_xor_displacement_profiles|displacement_profile|modular_permutation"
statistics.print_stats(selector)
statistics.print_callers(selector)
statistics.print_callees(selector)
PY
)
```

**Residual coefficient roadmap.** Four mechanism-specific questions remain:

1. Extend the signed-diagonal span calculation beyond n = 5 or produce a
   separating functional for the first missing modular permutation.
2. Compute minimum unit-output-scale coefficient one-norms at n = 3, 4, 5 and
   retain matching linear-program dual certificates; T is only a lower bound.
3. Classify displacement growth for useful bases of balanced semiprimes rather
   than infer RSA behavior from small-factor counterfamilies.
4. Compare end-to-end PREPARE, SELECT, reflection, and direct-arithmetic gate
   costs on the same multiplier; a normalization bound alone is not a compiler
   resource estimate.

### Signed modulo-15 census

`scripts/mod15_signed_multiplier_census.py` enumerates the seven nonidentity
units of (Z/15)^x, each of which `_mersenne_power_of_two` classifies as a
signed power of two: 2, 4, 8 are positive rotations and 7 = -8, 11 = -4,
13 = -2, 14 = -1 are rotations followed by one's-complement inversion. For
each base and both input domains the script builds the controlled multiplier
and reads its 32-state unitary (control plus four work qubits). It requires
unit-phase basis images; the control-0 identity; control 1 equal to
`a x mod 15` on residues 1..14; the raw rotate-and-invert rule on all 16 states
(endpoints 0 and 15 exchanged for a negative base); the full-register endpoint
rule (0 and 15 fixed) as the nonzero-residue circuit plus the controlled
Gray-path transposition of 0 and 15; zero scratch qubits; a gate census
that matches `multiplier_profile`; and `a` followed by `a^-1` (either order)
equal to the identity. The ideal yield uses `ideal_phase_distribution` and
`distribution_success` at eight phase bits, the count `order_finding_plan`
selects for N = 15. The compile column is one controlled multiplier on the
static FakeFez target at optimization level 3 over seeds 0 through 7; routed CZ,
depth, and critical-path duration (`QuantumCircuit.estimate_duration`) come
from the same compiled circuit.

| base | order | signed form | cswap | cx | ideal factor yield | median routed CZ | depth range |
|---:|---:|---|---:|---:|---:|---:|---:|
| 2 | 4 | +2^1 | 3 | 0 | 0.500000 | 36 | 111-112 |
| 4 | 2 | +2^2 | 2 | 0 | 0.500000 | 20 | 61-61 |
| 7 | 4 | -2^3 | 3 | 4 | 0.500000 | 40 | 126-127 |
| 8 | 4 | +2^3 | 3 | 0 | 0.500000 | 36 | 111-112 |
| 11 | 2 | -2^2 | 2 | 4 | 0.500000 | 23 | 63-82 |
| 13 | 4 | -2^1 | 3 | 4 | 0.500000 | 42 | 126-126 |
| 14 | 2 | -2^0 | 0 | 4 | 0.000000 | 7 | 15-19 |

CZ and depth in the table belong to the nonzero-residue domain, the domain of
the order-finding circuit. Base 14 = -1 has order 2 and a^(r/2) = -1, so the
factor extractor rejects every sample while the order recovery probability
stays 0.5; it is the arithmetic negative control, executable and factor-useless.
The six other bases each yield factors 3 and 5 with ideal probability 0.5. The
full-register domain adds seven controlled basis edges (four-control MCX gates
with no scratch) to each negative base, which raises the median routed CZ to
463, 454, 468, and 427 for bases 7, 11, 13, and 14 against 40, 23, 42, and 7 on
the nonzero-residue domain. The nonzero-residue circuit leaves 0 and 15
exchanged under control 1, so the endpoint rule holds on the full register only;
positive rotations fix both endpoints in either domain. The retained record
`results/hw_estimate/mod15_signed_multiplier_census.json` holds the per-seed
CZ, depth, duration, and qubit counts for both domains, the endpoint
outputs, tool versions, and the script hash.

The census is compiler and exact-host evidence; every record sets
`qpu_executed` to `false`. Step 3 hardware work stays on base 2. A multi-base
hardware run needs its own written case and approval under the QPU rules in
`AGENTS.md`.

Replay from the repository root (under 10 s):

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" scripts/mod15_signed_multiplier_census.py \
  --out results/hw_estimate/mod15_signed_multiplier_census.json
```

## What the algebra does connect to

**Bernstein-Vazirani over F_2^3.**
- The octonion associator phase is the linear character (-1)^(n_ij . x) of the
  Fano-line normal n_ij.
- H^3 W H^3 |0> therefore returns n_ij deterministically. That is design C at
  dim 8, and for pair (1,4) it returns n = 2. It is Bernstein-Vazirani: one
  oracle query recovers the hidden string, where design A reads one bit of the
  same character.
- Shor's order finding hides the period r of x -> a^x mod N in the exponent
  domain, the integers, approximated by a power-of-two cyclic register; r need
  not divide N. Simon's and Bernstein-Vazirani's problems hide subgroups of
  F_2^n instead. Cayley-Dickson signs live natively in the F_2^n family.

**Hidden quadratic and cubic forms.**
- Design C's Walsh spectrum of omega_ij reads out the phase function. At degree
  2 the distribution is flat on an affine subspace of size 2^rank, where rank is
  that of the quadratic form's symplectic matrix: 4 outcomes for dim 16 pair
  (1,8). The degree-3 and degree-4 exemplars give non-flat distributions.
- The pair (1, 2^(n-1)) has zero-frequency weight (1 - 2^(3-n))^2, checked for
  n = 3 through 7 by `verify.check_associator_walsh_hierarchy`. That check also
  pins the rank-2 quadratic support and every nonzero probability, giving a
  closed-form target for each newly introduced rung of the ladder. Lower-degree
  pairs remain present after a doubling.
- The n=3 linear character is the standard Bernstein-Vazirani/HSP instance.
  The higher-degree forms are phase-oracle benchmarks whose nonuniform Walsh
  spectra fall outside the standard HSP promise.

**The C881 sign-row bridge.**
- C881's 15 labels denote the top-level dim-32 pathion cross-assessor
  components in PG(3,2), rather than the seven dim-16 sedenion box-kites. On
  those shared four-bit labels, its 8/7 heptacross indicator, extended by
  H(0) = 0, equals `[cd_sign(16, 8, S) = -1]` exactly.
- Both functions have ANF masks (1, 2, 3, 4, 5, 6, 7, 8). Direct synthesis
  therefore uses four Z gates, three CZ gates, and one CCZ. The bounded
  Reed-Muller solver in `verify.check_pathion_separator_sign_bridge` rejects
  every degree-at-most-two polynomial on the 15 labels before recovering the
  cubic witness.
- `C881_GF2CubicMinDegree.v` proves all nonempty linear failures, six individual
  quadratic failures, and the cubic witness. Its exhaustive quadratic claim is
  a comment; open_gororoba's Rust search and the independent local solver close
  that finite lower bound. The verifier hash-pins the cited Rocq source before
  admitting its copied labels and classes. The result excludes an exact
  Clifford-only diagonal phase oracle in the fixed binary encoding. It supplies
  neither an arbitrary classifier lower bound nor a circuit-depth lower bound.

**A certified Toffoli-class benchmark.**
- Toffoli and CCZ gates make up the 6.5e9-gate core of RSA-2048. A degree-3
  phase with pi coefficients is CCZ-class.
- The associator phase has degree max(1, bitlen(max(i,j)) - 2), so the ladder
  supplies phase circuits of chosen non-Clifford degree with exact answers and
  sign-flip and omitted-block controls:

  | dim | phase degree | CZ (FakeFez target) |
  |---|---|---|
  | 8 | 1 | 18 |
  | 16 | 2 | about 50 |
  | 32 | 3 | about 96 |
  | 64 | 4 | 200 to 239 |

  The CZ column is for pair (1, 2^(n-1)).
- Measuring TVD against degree at matched CZ count separates degree-driven error
  from gate-count-driven error. The falsifier: if fidelity tracks CZ count alone,
  algebraic degree carries no information beyond circuit size.
- `live_run.py` already compiles the dims 8 to 32 rungs onto the best calibrated
  patch of the three backends.

**Semiclassical order finding on dynamic circuits.**
- Gidney's QFT is semiclassical: n - 1 adaptively phased gates driven by
  mid-circuit measurement.
- The smallest exact Heron surface is order finding for a = 2 mod 15. Its
  multiplier, a cyclic rotation of the four work bits, is the exact permutation
  on every input rather than a circuit compiled from the known answer (Smolin,
  Smith, and Vargo, Nature 499, 163 (2013)).
- `folded_qpe()` preserves the compiler-conformance benchmark. Its input is the
  known eigenstate |u_s> = (1/2) sum_k exp(-2 pi i s k/4) |2^k> of the
  multiplier, prepared as a phased W state. That makes the two-bit readout
  deterministic and equal to s.
- The four eigenstates run identical-cost circuits with distinct outcomes, so
  each controls the others. The identity multiplier is the null and reads 0.
- `factor_order_finding()` supplies the faithful Shor surface. It starts the
  work register in `|1>`, receives neither the order nor the factors, and uses
  eight-bit precision. Exact repeated squaring yields six leading identity
  rounds followed by multipliers four and two, so the circuit executes two
  measurements, one reset, one conditioned phase, and five Fredkin gates.
- The paired identity null follows the same two-round dynamic schedule and
  removes the Fredkin gates. The primary's ideal factor yield is 0.5; the exact
  uniform-decoder yield is 0.296875, so experiment summaries report the margin
  over both controls.
- `"$PYTHON" order_finding.py` checks the multiplier on the full register, the
  eigenvalues i^s, and the readout exactly. The generic controlled synthesis of
  the rotation costs 248 CZ on the FakeFez target; the Fredkin form costs 67.
- The live dry run of 2026-10-10T17:23:16Z placed the group on ibm_kingston at
  67 CZ. The noise model reads the correct phase with probability 0.91 for each
  s and the null at 0.957. The duration estimate (record field duration_s)
  excludes the classical feed-forward latency, which the Target does not report.
- This tests the dynamic-circuit machinery the factoring QFT needs. It
  establishes a factoring pipeline for a classically easy Mersenne case and
  makes no quantum-advantage claim. Monz et al. (Science 351, 1068 (2016)) ran
  the recycled-control form on trapped ions.

## What open_gororoba supplies

A survey of open_gororoba at fe668020 (literature/notes/open_gororoba_survey.md,
with derivations and replay scripts in open_gororoba_survey_deep_notes.md)
separates proven, tested, and asserted content.

**Re-checked here:**
- *The sign recursion as a circuit.* Over GF(2), cd_basis_mul_sign_iter
  unrolls to f_{n+1}(a, b, p', q') = f_n(swap_b(p', q')) + a(1 + b) + a[q' = 0],
  with a and b the top bits of p and q. It agrees with cd_sign on every (p, q)
  through dim 256.
  - The survey turns it into a circuit for the multiplexed product
    sum_p |p><p| (x) L_{e_p}: n(n-1) controlled swaps, 3n - 2 multi-controlled
    Z gates, and n CNOTs. It simulated that circuit at gate level through n = 6.
  - That is polynomial in n, where the DiagonalGate compile of one L_{e_m}
    grows as about 2^n.
  - At the 3 to 6 qubits these devices run, the controlled swaps cost more than
    the diagonal, so the crossover lies beyond this hardware.
  - The multiplexed product is still a family of signed XOR translations, so
    the modular-multiplier obstruction above applies to it unchanged.
- *Defect count.* The ordered basis triples with nonzero associator number
  v(N) = N^3/2 - 14N + 24: 168, 1848, 15960, and 130200 at N = 8, 16, 32, 64,
  checked here by brute force.
  - The survey matches the repository's zero-divisor edge totals at dims 16 to
    256 (84 to 523,404) to E(D) = v(D/2)/2.
  - Its predictions for dims 512 to 4096 (4,192,524 up to 2,147,469,324)
    assume the identity continues; nothing proves that.

**From the survey, not re-run here:**
- *Rocq.* 313 .v files, with no Admitted and no admit. CDSignHalfStep.v holds
  the only dimension-generic sign lemmas.
- *Fast factorization.* The only Rocq-proven one is Cariow 2013 at dim 16:
  Walsh-Hadamard diagonalization plus a 106-term sparse correction, 122
  multiplications. The dim-32 and dim-64 counts are unachieved targets.
- *"512/1024/2048" files.* The Rocq files with those numbers in their names, in
  curated/, model thread capacity and carry no Cayley-Dickson content.
- *Quantum content.* The repository's quantum material is an MPS simulator, a
  Grover search, and hardware profiles. It has no QFT, no modular arithmetic,
  and no Shor; its box-kite QEC, p-adic CD crypto, and sedenion braid compiler
  modules are stubs or analogies.
- *The group order.* The survey's independent sympy computation gives
  2^(n + 2^(n-1)) for n = 3 through 8, matching check_left_mult_group.
