# Annihilator geometry program: derive algorithms from the algebra's structure

Owner direction of 2026-11-28 (PST): derive algorithms from the actual structural properties of the Cayley-Dickson
algebras, and use quantum processors to read compositions, interference, transport and higher-order relations that the
existing rank classification does not expose. Reverse the usual problem at every step: specify the desired annihilator
geometry first, then solve for the algebra elements that realize it, and admit a result only after its rank and
geometry are checked exactly.

## Conventions

- The algebra is `cd_core` (`e_p e_q = cd_sign(dim, p, q) e_(p XOR q)`), real coefficients, Euclidean form on the
  basis. The annihilator of `a` is the right kernel `ker L_a = {v : a v = 0}`; the left kernel `ker R_a` is named
  where used.
- A subspace `K` is *realizable* when some `a` has `ker L_a = K` exactly; *contained* when `K` lies inside some
  `ker L_a`. Because `a v` is bilinear, the set `A(K) = {a : a v = 0 for every v in K}` is the intersection of the
  kernels of `R_v` over a basis of `K`, a linear subspace computable exactly.
- Every number in this note is computed (exact rationals or a finite field, named), measured (backend named) or a
  hypothesis with its falsifier.

## Algorithms (owner list, kept verbatim in intent)

| Id | Algorithm | Mechanism and objective |
|---|---|---|
| G1 | Inverse annihilator synthesis | specify a kernel geometry, solve the linear system A(K), admit after exact rank and geometry checks |
| G2 | Restricted synthesis | cheapest operation that agrees with a target transformation on an admitted subspace only |
| G3 | Lossless bridge search | shortest information-preserving transformation between distinct, possibly orthogonal annihilators |
| G4 | Routing through higher nullity | pass through an intermediate higher-nullity sector when a direct bridge is impossible or costly |
| G5 | Path interferometry | distinguish approaches to one singular point by coherent return amplitudes |
| G6 | Latent Clifford discovery | find anticommuting logical generators inside rank-stratum projectors |
| G7 | Spectral collapse | rates, multiplicities and ordering of collapse near singular loci |
| G8 | Word shortening | short equivalent words in non-associatively generated multiplication operators |
| G9 | Equal-local, distinct-global paths | identical transition probabilities, different return amplitudes |
| G10 | Higher-order compatibility | constraints invisible to first-order tangent and kernel analysis |
| G11 | Doubling invariants | which invariants survive doubling, which arise only from inter-component coupling |
| G12 | Discriminating experiment choice | pick the symbolic calculation or hardware run by its power to separate competing hypotheses |
| G13 | Rewriting inference | compact rewriting systems and identities from word spectra and circuit outcomes |
| G14 | Large-annihilator encodings | cheaper encodings, protected sectors or gates inside larger annihilators |
| G15 | Ordered relations | relations that pairwise overlaps and spectra cannot reconstruct (Bargmann invariants) |
| G16 | Adversarial compression | compress a circuit, build states outside its admitted domain, refine circuit or preconditions |

## Questions (open; each becomes a ledger row when a computation settles it)

Kernels and synthesis: which kernels can be specified arbitrarily and realized; which subspaces never occur as
annihilators; can distinct elements share every observable signature; smallest generating set of the attainable
transport operators; which associators act only on selected annihilator sectors; does the atlas hold unidentified complex
or quaternionic structures; which logical structures appear only past a rank threshold; are geometrically distinct strata
computationally equivalent.

Transport and holonomy: can two orthogonal annihilators communicate without leakage; can every pair connect through a
finite chain of lossless bridges; does a higher-dimensional sector give a cheaper route; can two paths share all pairwise
overlaps yet differ in higher-order invariants; which closed loops carry nontrivial holonomy, and do different loops give
noncommuting holonomies; which topological invariants survive doubling; can larger strata be rebuilt from their limiting
annihilators; what obstructs a globally continuous representative of a projector family.

Compilation: shortest circuit that realizes an operator only on its kernel; when a dense multiplication operator becomes a
sparse Pauli operator after projection; which signed permutations reduce to affine Boolean phases on selected sectors;
recursive evaluation without full matrices; the transition network as a compilation graph; distinct circuits with
identical logical action; whether extra intermediate dimensions cut ancilla cost; which constraints give polynomial cost.

Logic and hardware: can annihilator structure supply logical gates; which sectors hold useful non-Clifford operations; can
rank-changing operations act as measurements; can a QPU separate hypotheses that agree under classical low-order
observation; can noise expose differences in operator sensitivity; which degeneracies are robust; can hardware estimate
high-order contractions faster than tensor networks; can outcomes guide a simpler exact identity; what makes a failure
informative rather than a failed acquisition.

The first questions under computation: can two annihilators with zero overlap be joined by an exact information-preserving
algebra operation; is there a shared 8-dimensional annihilator whose 4-dimensional sub-annihilators form the six endpoints
of a Clifford Cl(3,0) structure; does every point of the resulting projector sphere arise as an actual A_5 annihilator;
do nullity 12 and 16 give other signatures.

## First computation (2026-11-28, exact rationals, scratch, unretained)

At y0 = e_1 + e_10 (nullity 8, the W8 point of [A5 nullity transitions](../evidence/a5-nullity-transitions/README.md),
statement 8), with predictions written before the run:

- 36 signed two-term directions w give nullity 4 with kernel inside K8 = ker L_y0, constant along y0 + s w; they span six
  planes in three orthogonal pairs, and E_k = 2 P_k - P_K8 anticommute, square to P_K8 and are traceless: Cl(3,0) on K8.
- Lossless bridges: for every ordered pair of the six planes, including the orthogonal pairs, the w with L_w A inside B
  form a space of dimension 14 (from the first pair) or 8, and a generic such w maps A onto B with rank 4 and a Gram
  equal to a scalar multiple of A's: an isometry up to scale. Hypothesis to settle: whether every bridge in the space is
  isometric, and whether a bridge restricts to a Clifford generator.
- Inverse synthesis: each of the six planes is realizable (a generic element of A(K) has kernel exactly K); a fixed
  generic rational 4-plane of K8 is not (A(K) has dimension 4 and its generic kernel is all of K8). Five rational points
  n of the sphere give planes (P_K8 + n.E)/2, each realizable; dim A(K) is 12 at n = (1, 0, 0) and 6 at the other four,
  so the E_1 axis is distinguished. Open: a symbolic proof over the whole sphere.

## Standing limits

- A stabilizer-compatible shortcut is classically simulable; an experiment is not hard because its algebra is exotic. The
  frontier is structure whose restricted operator complexity stays large after classical compression.
- Three pairwise anticommuting orthogonal reflections of an 8-dimensional space give signature (3,0), six rank-4
  projectors and a complex structure automatically; the content lies in which projectors are exact annihilators, the
  largest realizable anticommuting family, and whether the generators are restrictions of algebra operators rather than of
  known symmetries (the A5-254 Klein matrices, the (Z/2)^5 sign characters, the G_2 derivations).
- A statement such as "the bridge is the identity in logical frames" depends on the frames; frame-free invariants
  (holonomy classes, Bargmann traces) carry the claim.
- Hardware serves a scientific purpose: replicated small experiments on disjoint Heron patches, with the deciding
  observables preregistered, numerator and denominator measured separately, the +, -, -, + arms and a null arm
  (docs/notes/algebra_circuit_rules.md#hardware-probes), and a power calculation at routed-CZ visibility before any case.

## Pipeline

Generate candidates (kernels, identities, paths, symmetries, logical operations); falsify cheaply (exact arithmetic,
finite fields, SAT and SMT, elimination, automorphisms, adversarial samples); build competing algorithms (recursive
multiplication, restricted synthesis, stabilizer reductions, tensor networks, quantum-native transformations); execute
classically and on hardware; reconstruct structure and test competing explanations; promote surviving identities to exact
certificates and formal proofs (gororoba-math: Lean, Rocq, Agda; z3 for decision procedures).
