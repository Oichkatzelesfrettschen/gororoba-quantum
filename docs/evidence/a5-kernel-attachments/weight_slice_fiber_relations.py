"""Degree-d relations of the fiber cone of the nullity-8 sources at the nullity-16 basepoints, on a torus weight slice.

At the basepoint z_0 of N+ or N- the two-dimensional torus of the stabilizer in g_2 + scaling + boost acts on the
nine-dimensional normal slice z_0 + sum_k s_k n_k along joint eigenvectors n_k. In a frame of torus eigenvectors of
C^15 (the complement of ker C(z_0), then ker C(z_0)) the 9 x 9 Schur form W = det(B) D + X^T adj(B) X of the slice
has weight-homogeneous entries, so its 126 principal 4-Pfaffians are weight-homogeneous polynomials in s_1..s_9. The
integer weight 2 w_1 - w_2 of the first two torus characters is nonnegative on the slice coordinates; the
coordinates of weight zero stay free.

For one source (W8, E8bar, Iso, X+, X-) the germ ideal J of the source closure on the slice is replaced by the
intersection of its minimal primes through the origin. The producer then selects Nakayama generators G among the
Pfaffians (a Pfaffian joins G when its reduction modulo J + m (all Pfaffians), computed on a truncation at the
largest Pfaffian weight, is nonzero), forms the products G_a ... G_d, and reads the relations q(G) in J + m I^d
(I = (G)) as the syzygies of the normal forms of the products modulo J + m P + (monomials of weight above the largest
product weight). Two facts make this the local computation. Every ideal involved is graded by the torus weight and
the added monomials lie above the largest weight of a product, so the truncation changes no normal form of a product.
The class of q(G) modulo J + m P is killed by the maximal ideal, so a unit of the local ring (det B, 1 + i s_2,
1 - s_2^2) acts on it as a nonzero constant, and membership in the polynomial ring equals membership in the local
ring. A truncated standard basis of weight-homogeneous input computes each of these in one pass, so the
whole table runs over Q(i) in under a minute, and the relation ideal of the retained W8 and E8bar cells then gets its
Hilbert series, dimension, multiplicity and saturation. Two cells recompute modulo 32009 with i sent to 10754, and the
Q(i) relation space reduced through that map is compared with the modular one by rank.

The record states, per basepoint, the torus weights and, per cell, the germ before and after the component step, the
selected Pfaffians, the generator weights, the relation count and a digest of the relation lines; it binds the
generator and quadric counts to the retained fibers of `nullity8-fiber-import-result.json`. Two controls rerun a cell
with a wrong weight vector and without the component step. The relations themselves are not retained: the digest
names them, and the producer regenerates them.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from string import Template
from typing import Any

import flint
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE.parent / "a5-strata-regularity"))

import composed_limit_sections as sections  # noqa: E402
import holomorphic_kernel_lemma as kernel_lemma  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-weight-slice-fiber-relations-v1"
BASEPOINTS_RESULT = HERE / "nullity16-basepoints-result.json"
IMPORT_RESULT = HERE / "nullity8-fiber-import-result.json"
SOURCE_PATHS = (
    HERE / "weight_slice_fiber_relations.py",
    HERE / "composed_limit_sections.py",
    HERE / "holomorphic_kernel_lemma.py",
    HERE / "nakayama_rees_fibers.py",
    BASEPOINTS_RESULT,
    IMPORT_RESULT,
    HERE.parent / "a5-strata-regularity" / "verify_regularity_independent.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)

ORBITS = ("N+", "N-")
SOURCES = ("w8", "e8", "iso", "xp", "xm")
# Source key of the Singular tables -> source name in the incidence labels of the retained records.
SOURCE_LABELS = {"w8": "W8", "e8": "E8bar", "iso": "Iso", "xp": "X+", "xm": "X-"}
DEGREE = 2
COMPLEX_DIMENSION = 15
KERNEL_DIMENSION = 9
NORMAL_DIMENSION = 9
COMPLEMENT_DIMENSION = COMPLEX_DIMENSION - KERNEL_DIMENSION
PFAFFIAN_COUNT = math.comb(KERNEL_DIMENSION, 4)
# Torus weight 2 w_1 - w_2 of the nine slice coordinates, in the order of the joint eigenvector basis; the one zero is
# the coordinate along which det(B) varies.
EXPECTED_GRADING_WEIGHTS = (1, 0, 3, 2, 2, 1, 4, 4, 3)
TORUS_GENERATORS = (
    "identity minus the lift of derivation 7",
    "lift of derivation 13 minus the lift of derivation 7",
    "boost minus (+1 at N+, -1 at N-) times the lift of derivation 7",
)
# (generators, quadrics) of the degree-2 fiber cone relations per (orbit, source); retained fibers of the
# nullity-8 import record carry the same counts.
EXPECTED_COUNTS = {
    ("N+", "w8"): (24, 144),
    ("N+", "e8"): (21, 148),
    ("N+", "iso"): (17, 68),
    ("N+", "xp"): (15, 69),
    ("N+", "xm"): (3, 0),
    ("N-", "w8"): (24, 144),
    ("N-", "e8"): (21, 148),
    ("N-", "iso"): (17, 68),
    ("N-", "xp"): (3, 0),
    ("N-", "xm"): (15, 69),
}
# (affine dimension, multiplicity) of the quadric ideal in k[y_1..y_g].
EXPECTED_HILBERT = {"w8": (6, 50), "e8": (5, 11)}
# (affine dimension, multiplicity, linear forms of the reduced standard basis) of each minimal prime of that ideal.
EXPECTED_MINIMAL_PRIMES = {"w8": ((6, 20, 9), (6, 30, 4)), "e8": ((4, 4, 14), (5, 11, 9))}
HILBERT_SOURCES = tuple(EXPECTED_HILBERT)
MODULAR_PRIME = 32009
MODULAR_ROOT = 10754
MODULAR_ORBIT = "N-"
MODULAR_SOURCES = ("w8", "e8")
CONTROL_CELL = ("N-", "xp")
SINGULAR_ADDRESS_SPACE_BYTES = 8 * 1024**3
SINGULAR_TIMEOUT_SECONDS = 3600

IMAGINARY = sp.I
SOURCE_SYMBOLS = sp.symbols(f"s1:{NORMAL_DIMENSION + 1}")
SAFE_POLYNOMIAL = re.compile(r"[0-9is+\-*/^() ]*")
RESULT_LINE = re.compile(r"^RESULT (\S+)(?: (.*))?$")
GAUSSIAN_TERM = re.compile(r"([+-]?)(\d+(?:/\d+)?)?(?:\*?(i))?")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


# ---------------------------------------------------------------------------------------------------------------------
# The torus weight slice at a nullity-16 basepoint


def _phase(index: int) -> Any:
    """i^popcount(k) for the one-based coordinate k = index + 1: original z_k = phase * split coordinate."""
    return IMAGINARY ** ((index + 1).bit_count())


def _phase_matrix() -> sp.Matrix:
    return sp.diag(*[_phase(index) for index in range(COMPLEX_DIMENSION)])


def _derivation_matrix(index: int) -> sp.Matrix:
    """The lift of derivation `index` of the split octonions to both halves of the sixteen-dimensional algebra."""
    block = independent.DERS[index]
    matrix = sp.zeros(COMPLEX_DIMENSION, COMPLEX_DIMENSION)
    for row in range(7):
        for column in range(7):
            matrix[row, column] = matrix[8 + row, 8 + column] = sp.Rational(block[row][column])
    return matrix


def _boost_matrix() -> sp.Matrix:
    matrix = sp.zeros(COMPLEX_DIMENSION, COMPLEX_DIMENSION)
    for index in range(7):
        matrix[index, index + 8] = matrix[index + 8, index] = 1
    return matrix


def torus_generators(sign: int) -> list[sp.Matrix]:
    """The three commuting stabilizer generators in the original coordinates (conjugated by the phase matrix)."""
    _require(sign in (1, -1), "the boost sign is +1 at N+ and -1 at N-")
    phase = _phase_matrix()
    d7, d13 = _derivation_matrix(6), _derivation_matrix(12)
    split = [sp.eye(COMPLEX_DIMENSION) - d7, -d7 + d13, _boost_matrix() - sign * d7]
    return [phase * matrix * phase.inv() for matrix in split]


def _c_basis() -> list[sp.Matrix]:
    """The linear encoding z -> C(z) of the holomorphic kernel as fifteen constant matrices."""
    basis = []
    for index in range(COMPLEX_DIMENSION):
        unit = tuple((Fraction(int(column == index)), Fraction(0)) for column in range(COMPLEX_DIMENSION))
        matrix = kernel_lemma._c_matrix(unit)
        basis.append(
            sp.Matrix(
                COMPLEX_DIMENSION,
                COMPLEX_DIMENSION,
                lambda row, column, matrix=matrix: (
                    sp.Rational(matrix[row][column][0]) + IMAGINARY * sp.Rational(matrix[row][column][1])
                ),
            )
        )
    return basis


def _integer(value: Any) -> int:
    number = sp.nsimplify(value)
    _require(number.is_integer is True, f"torus weight {number} is not an integer")
    return int(number)


def joint_basis(matrices: list[sp.Matrix], space: sp.Matrix) -> list[tuple[tuple[int, ...], sp.Matrix]]:
    """Joint eigenvectors of commuting diagonalizable `matrices` inside the invariant column space `space`."""
    width = space.shape[1]
    for matrix in matrices:
        _require(sp.Matrix.hstack(space, matrix * space).rank() == width, "a torus generator leaves the space")
    pseudo_inverse = (space.H * space).inv() * space.H
    restricted = [sp.simplify(pseudo_inverse * matrix * space) for matrix in matrices]
    blocks: list[tuple[tuple[int, ...], sp.Matrix]] = [((), sp.eye(width))]
    for matrix in restricted:
        refined: list[tuple[tuple[int, ...], sp.Matrix]] = []
        for weights, block in blocks:
            sub = sp.simplify((block.H * block).inv() * block.H * matrix * block)
            found = 0
            for value, _multiplicity, vectors in sub.eigenvects():
                found += len(vectors)
                refined.append((weights + (_integer(value),), sp.simplify(block * sp.Matrix.hstack(*vectors))))
            _require(found == block.shape[1], "a torus generator is not diagonalizable on its weight space")
        blocks = refined
    return [
        (weights, sp.simplify(space * block[:, column]))
        for weights, block in blocks
        for column in range(block.shape[1])
    ]


@dataclass(frozen=True)
class OrbitSlice:
    """The slice data at one basepoint: the point, the joint eigenbases of the normal slice and the kernel frame."""

    orbit: str
    boundary_point: tuple[str, ...]
    z0: sp.Matrix
    normal: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    kernel: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    complement: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    tangent_weights: tuple[tuple[int, ...], ...]
    c_basis: tuple[sp.Matrix, ...]


def build_slice(orbit: str) -> OrbitSlice:
    """The retained basepoint of `orbit` with its torus-adapted normal slice and kernel frame."""
    _require(orbit in ORBITS, f"unknown boundary orbit {orbit}")
    rows = json.loads(BASEPOINTS_RESULT.read_text(encoding="utf-8"))["incidences"]
    points = {tuple(row["boundary_point"]) for row in rows if row["boundary_orbit"] == orbit}
    _require(len(points) == 1, f"the rows into {orbit} do not share one boundary point")
    boundary_point = next(iter(points))
    phase = _phase_matrix()
    z0 = phase * sp.Matrix([sp.Rational(value) for value in boundary_point])
    torus = torus_generators(1 if orbit == "N+" else -1)
    for generator in torus:
        _require(sp.simplify(generator * z0).is_zero_matrix is True, "a torus generator moves the basepoint")
    c_basis = _c_basis()
    c_at_z0 = sum((z0[index] * c_basis[index] for index in range(COMPLEX_DIMENSION)), sp.zeros(COMPLEX_DIMENSION))
    kernel_space = sp.Matrix.hstack(*c_at_z0.nullspace())
    _require(kernel_space.shape[1] == KERNEL_DIMENSION, "the kernel of C(z_0) does not have dimension 9")
    # Tangent space of the orbit of z_0 under g_2, the scaling and the boost, in the original coordinates.
    generators = [phase * _derivation_matrix(index) * phase.inv() for index in range(len(independent.DERS))]
    generators += [sp.eye(COMPLEX_DIMENSION), phase * _boost_matrix() * phase.inv()]
    tangent = sp.Matrix.hstack(*sp.Matrix.hstack(*[matrix * z0 for matrix in generators]).columnspace())
    everything = joint_basis(torus, sp.eye(COMPLEX_DIMENSION))
    tangent_weights = sorted(weights for weights, _ in joint_basis(torus, tangent))
    remaining = list(tangent_weights)
    normal = []
    for weights, vector in everything:
        if weights in remaining:
            remaining.remove(weights)
        else:
            normal.append((weights, vector))
    _require(remaining == [] and len(normal) == NORMAL_DIMENSION, "the normal slice does not have dimension 9")
    kernel = joint_basis(torus[:2], kernel_space)
    complement: list[tuple[tuple[int, ...], sp.Matrix]] = []
    span = sp.Matrix.hstack(*[vector for _, vector in kernel])
    for weights, vector in joint_basis(torus[:2], sp.eye(COMPLEX_DIMENSION)):
        if sp.Matrix.hstack(span, vector).rank() > span.shape[1]:
            complement.append((weights, vector))
            span = sp.Matrix.hstack(span, vector)
    _require(len(complement) == COMPLEMENT_DIMENSION, "the kernel frame has no complement of dimension 6")
    return OrbitSlice(
        orbit,
        boundary_point,
        z0,
        tuple(normal),
        tuple(kernel),
        tuple(complement),
        tuple(tangent_weights),
        tuple(c_basis),
    )


def grading_weights(joint_weights: Sequence[Sequence[int]]) -> list[int]:
    """The integer grading 2 w_1 - w_2 of the first two torus characters."""
    return [2 * int(weights[0]) - int(weights[1]) for weights in joint_weights]


def _singular_polynomial(value: Any) -> str:
    text = str(sp.nsimplify(sp.expand(value))).replace("I", "i").replace("**", "^")
    _require(SAFE_POLYNOMIAL.fullmatch(text) is not None, f"unexpected character in the Singular polynomial {text!r}")
    return f"({text})"


def source_equations(piece: OrbitSlice, source: str) -> list[str]:
    """Closure generators of `source` (`closure_generators` of the regularity verifier) pulled back to the slice."""
    split = _phase_matrix().inv() * (
        piece.z0
        + sum((SOURCE_SYMBOLS[index] * vector for index, (_, vector) in enumerate(piece.normal)), sp.zeros(15, 1))
    )
    left, middle, right = list(split[0:7, 0]), split[7], list(split[8:15, 0])
    total = [first + second for first, second in zip(left, right, strict=True)]
    difference = [first - second for first, second in zip(left, right, strict=True)]
    eta_left, eta_right, eta_cross = (
        independent.eta2(left, left),
        independent.eta2(right, right),
        independent.eta2(left, right),
    )
    quadric = eta_left - middle * middle - eta_right
    delta = eta_cross * eta_cross - eta_left * eta_right
    rows = sp.Matrix([left, right, independent.cross(left, right)])
    closure = [quadric, delta] + [rows[:, list(columns)].det() for columns in itertools.combinations(range(7), 3)]
    table = {
        "w8": [middle, independent.eta2(total, total), independent.eta2(difference, difference)],
        "iso": [middle, eta_left, eta_right, eta_cross],
        "e8": closure,
        "xp": [*closure, middle, independent.eta2(difference, difference)],
        "xm": [*closure, middle, independent.eta2(total, total)],
    }
    _require(source in table, f"unknown source {source}")
    return [_singular_polynomial(entry) for entry in table[source] if sp.expand(entry) != 0]


@dataclass(frozen=True)
class SlicePiece:
    """Strings and integers of one basepoint that the Singular scripts need; picklable across the process pool."""

    orbit: str
    boundary_point: tuple[str, ...]
    normal_weights: tuple[tuple[int, ...], ...]
    kernel_weights: tuple[tuple[int, ...], ...]
    complement_weights: tuple[tuple[int, ...], ...]
    tangent_weights: tuple[tuple[int, ...], ...]
    grading: tuple[int, ...]
    matrix_lines: str
    equations: dict[str, tuple[str, ...]]


def _matrix_lines(piece: OrbitSlice) -> str:
    """Singular statements for the Schur form W on the slice, in the ring that declares s1..s9 and i."""
    points = [
        _singular_polynomial(piece.z0[index])
        + "".join(
            f"+{_singular_polynomial(vector[index])}*s{position + 1}"
            for position, (_, vector) in enumerate(piece.normal)
            if vector[index] != 0
        )
        for index in range(COMPLEX_DIMENSION)
    ]
    lines = [f"matrix C[{COMPLEX_DIMENSION}][{COMPLEX_DIMENSION}];"]
    for row in range(COMPLEX_DIMENSION):
        for column in range(row + 1, COMPLEX_DIMENSION):
            terms = [
                f"{_singular_polynomial(piece.c_basis[index][row, column])}*({points[index]})"
                for index in range(COMPLEX_DIMENSION)
                if piece.c_basis[index][row, column] != 0
            ]
            if terms:
                upper, lower = f"C[{row + 1},{column + 1}]", f"C[{column + 1},{row + 1}]"
                lines.append(f"{upper}={'+'.join(terms)}; {lower}=-{upper};")
    lines.append(f"matrix F[{COMPLEX_DIMENSION}][{COMPLEX_DIMENSION}];")
    frame = [vector for _, vector in piece.complement] + [vector for _, vector in piece.kernel]
    for column, vector in enumerate(frame):
        for row in range(COMPLEX_DIMENSION):
            if vector[row] != 0:
                lines.append(f"F[{row + 1},{column + 1}]={_singular_polynomial(vector[row])};")
    lines += [
        "matrix T=transpose(F)*C*F;",
        f"intvec ra=1..{COMPLEMENT_DIMENSION}; intvec rb={COMPLEMENT_DIMENSION + 1}..{COMPLEX_DIMENSION};",
        f"matrix B[{COMPLEMENT_DIMENSION}][{COMPLEMENT_DIMENSION}]=submat(T,ra,ra);",
        f"matrix X[{COMPLEMENT_DIMENSION}][{KERNEL_DIMENSION}]=submat(T,ra,rb);",
        f"matrix Dm[{KERNEL_DIMENSION}][{KERNEL_DIMENSION}]=submat(T,rb,rb);",
        "poly dB=det(B); matrix aB=adjoint(B);",
        "matrix W=dB*Dm+transpose(X)*aB*X;",
    ]
    return "\n".join(lines)


def orbit_task(orbit: str) -> SlicePiece:
    """The slice, torus weights, Schur-form statements and source equations of one basepoint."""
    piece = build_slice(orbit)
    weights = grading_weights([weights for weights, _ in piece.normal])
    _require(tuple(weights) == EXPECTED_GRADING_WEIGHTS, f"grading weights {weights} differ from the expected ones")
    return SlicePiece(
        orbit=orbit,
        boundary_point=piece.boundary_point,
        normal_weights=tuple(weights for weights, _ in piece.normal),
        kernel_weights=tuple(weights for weights, _ in piece.kernel),
        complement_weights=tuple(weights for weights, _ in piece.complement),
        tangent_weights=piece.tangent_weights,
        grading=tuple(weights),
        matrix_lines=_matrix_lines(piece),
        equations={source: tuple(source_equations(piece, source)) for source in SOURCES},
    )


# ---------------------------------------------------------------------------------------------------------------------
# Singular scripts

PROCEDURES = """
proc tdeg(poly p){ int v=0; int k; intvec e=leadexp(p); for(k=1;k<=9;k++){v=v+e[k]*tw[k];} return(v); }
proc thomog(poly p){ int v=tdeg(p); while(p!=0){ if(tdeg(p)!=v){return(0);} p=p-lead(p); } return(1); }
proc tmax(poly p){ int v=0; while(p!=0){ if(tdeg(p)>v){v=tdeg(p);} p=p-lead(p); } return(v); }
// Minimal monomials in the positive-weight variables of weight above E.
proc trunc(int E){
  ideal pos; int k; for(k=1;k<=9;k++){ if(tw[k]>0){pos=pos,var(k);} } pos=simplify(pos,2);
  ideal cur=1; ideal out; ideal nxt; int a; int b; poly q;
  while(size(cur)>0){
    nxt=0;
    for(a=1;a<=ncols(cur);a++){ if(cur[a]!=0){ for(b=1;b<=ncols(pos);b++){
      q=cur[a]*pos[b]; if(tdeg(q)>E){out=out,q;}else{nxt=nxt,q;} } } }
    cur=simplify(nxt,6);
  }
  return(simplify(out,6));
}
proc pf4(matrix A,int a,int b,int c,int d){ return(A[a,b]*A[c,d]-A[a,c]*A[b,d]+A[a,d]*A[b,c]); }
"""

COMPONENT_STEP = """
list L=minAssGTZ(J); ideal JJ=1; ideal Lk; ideal sm=std(maxideal(1)); int kk;
for(kk=1;kk<=size(L);kk++){
  Lk=std(L[kk]);
  print("RESULT component "+string(dim(Lk))+" "+string(mult(Lk))+" "+string(size(reduce(Lk,sm))==0));
  if(size(reduce(Lk,sm))==0){JJ=intersect(JJ,Lk);}
}
J=std(JJ);
"""

PFAFFIAN_STAGE = """
print("RESULT germ_after "+string(dim(J))+" "+string(mult(J))+" "+string(size(J)));
int bad=0; for(k=1;k<=size(J);k++){ if(!thomog(J[k])){bad++;} }
print("RESULT germ_inhomogeneous "+string(bad));
ideal m=maxideal(1);
ideal PF; int a; int b; int c; int d; int n=0;
for(a=1;a<=6;a++){for(b=a+1;b<=7;b++){for(c=b+1;c<=8;c++){for(d=c+1;d<=9;d++){ n++; PF[n]=reduce(pf4(W,a,b,c,d),J); }}}}
int dmax=0; string inhomogeneous="";
for(a=1;a<=126;a++){ if(PF[a]!=0){
  if(tmax(PF[a])>dmax){dmax=tmax(PF[a]);}
  if(!thomog(PF[a])){inhomogeneous=inhomogeneous+" "+string(a);} } }
print("RESULT pfaffian_nonzero "+string(size(PF)));
print("RESULT pfaffian_max_weight "+string(dmax));
print("RESULT pfaffian_inhomogeneous"+inhomogeneous);
"""

SELECTION_STAGE = """
ideal TR=trunc(dmax); ideal TT=std(J+TR+m*PF);
ideal G; intvec sel; int g=0; poly rr;
for(a=1;a<=126;a++){ rr=reduce(PF[a],TT); if(rr!=0){ g++; G[g]=PF[a]; sel[g]=a; TT=std(TT+ideal(rr)); } }
print("RESULT generators "+string(g));
print("RESULT selected "+string(sel));
intvec gw; for(a=1;a<=g;a++){gw[a]=tdeg(G[a]);}
print("RESULT generator_weights "+string(gw));
"""

PRODUCT_STAGE = """
list IX; ideal P; n=0; int pmax=0; $declarations
$loops
print("RESULT products "+string(n)+" "+string(pmax));
ideal TR2=trunc(pmax); ideal sQ=std(J+TR2+m*P);
ideal N=reduce(P,sQ);
ideal mons; poly h;
for(a=1;a<=n;a++){ h=N[a]; while(h!=0){ mons=mons,leadmonom(h); h=h-lead(h); } }
mons=simplify(mons,6);
matrix M=coeffs(N,mons);
print("RESULT normal_forms "+string(size(N))+" "+string(size(mons)));
module S=syz(module(M));
print("RESULT relations "+string(size(S)));
string row;
for(a=1;a<=size(S);a++){
  row="";
  for(b=1;b<=n;b++){ if(S[a][b]!=0){ row=row+" "+string(IX[b])+":"+string(S[a][b]); } }
  print("RELATION"+row);
}
"""

SCRIPT = Template(
    """LIB "matrix.lib"; LIB "linalg.lib"; LIB "primdec.lib";
$ring
option(redSB);
$matrix_lines
intvec tw=$weights;
int k;
$procedures
ideal J=$equations; J=std(J);
print("RESULT germ_before "+string(dim(J))+" "+string(mult(J))+" "+string(size(J)));
$component_step
$pfaffian_stage
$tail
print("RESULT done 1");
quit;
"""
)

HILBERT_SCRIPT = Template(
    """$ring
option(redSB);
ideal K=$polynomials;
ideal sK=std(K);
print("RESULT relation_count "+string(size(K)));
print("RESULT dimension "+string(dim(sK)));
print("RESULT multiplicity "+string(mult(sK)));
bigintvec H=hilb(sK,1);
print("RESULT hilbert_first_numerator "+string(H));
print("RESULT saturated "+string(size(reduce(quotient(sK,maxideal(1)),sK))==0));
LIB "primdec.lib";
list components=minAssGTZ(K); ideal component; int position; int generator; int linear;
for(position=1;position<=size(components);position++){ component=std(components[position]); linear=0;
  for(generator=1;generator<=size(component);generator++){ if(deg(component[generator])==1){linear++;} }
  print("RESULT minimal_prime "+string(dim(component))+","+string(mult(component))+","+string(linear)); }
print("RESULT done 1");
quit;
"""
)


def _ring(characteristic: int, root: int, variables: str, ordering: str) -> str:
    if characteristic == 0:
        return f"ring r=(0,i),({variables}),({ordering}); minpoly=i^2+1;"
    _require(
        pow(root, 2, characteristic) == characteristic - 1, f"{root} is not a square root of -1 modulo {characteristic}"
    )
    return f"ring r={characteristic},({variables}),({ordering}); number i={root};"


def _product_stage(degree: int) -> str:
    names = [f"x{position}" for position in range(1, degree + 1)]
    loops = ""
    for position, name in enumerate(names):
        start = "1" if position == 0 else names[position - 1]
        loops += f"for({name}={start};{name}<=g;{name}++){{"
    body = (
        f"n++; P[n]=reduce({'*'.join(f'G[{name}]' for name in names)},J); IX[n]=intvec({','.join(names)}); "
        "if(tmax(P[n])>pmax){pmax=tmax(P[n]);}"
    )
    return Template(PRODUCT_STAGE).substitute(
        declarations=" ".join(f"int {name};" for name in names), loops=loops + body + "}" * degree
    )


def fiber_script(
    piece: SlicePiece,
    source: str,
    characteristic: int,
    root: int,
    degree: int = DEGREE,
    component_step: bool = True,
    weights: tuple[int, ...] | None = None,
    through_pfaffians_only: bool = False,
) -> str:
    """The Singular script of one cell. `weights` replaces the torus grading and `through_pfaffians_only` stops after
    the homogeneity check of the Pfaffians; both serve the controls."""
    _require(degree >= 2, "a relation has degree at least 2")
    grading = piece.grading if weights is None else weights
    _require(len(grading) == NORMAL_DIMENSION and min(grading) >= 0, "the grading needs nine nonnegative weights")
    ordering = ",".join(str(max(weight, 1)) for weight in grading)
    variables = ",".join(f"s{position}" for position in range(1, NORMAL_DIMENSION + 1))
    tail = "" if through_pfaffians_only else SELECTION_STAGE + _product_stage(degree)
    return SCRIPT.substitute(
        ring=_ring(characteristic, root, variables, f"wp({ordering})"),
        matrix_lines=piece.matrix_lines,
        weights=",".join(str(weight) for weight in grading),
        procedures=PROCEDURES,
        equations=",".join(piece.equations[source]),
        component_step=COMPONENT_STEP if component_step else "",
        pfaffian_stage=PFAFFIAN_STAGE,
        tail=tail,
    )


def hilbert_script(relations: list[str], generators: int, characteristic: int, root: int) -> str:
    """The Singular script that reads the relation ideal in k[y_1..y_g] and reports its Hilbert data."""
    polynomials = []
    for line in relations:
        terms = [
            f"({coefficient})*{'*'.join(f'y({index})' for index in key)}" for key, coefficient in parse_relation(line)
        ]
        polynomials.append("+".join(terms))
    _require(polynomials != [], "no relation to read")
    ring = _ring(characteristic, root, f"y(1..{generators})", "dp")
    return HILBERT_SCRIPT.substitute(ring=ring, polynomials=",\n".join(polynomials))


# ---------------------------------------------------------------------------------------------------------------------
# Running Singular and reading its output


def singular_version() -> tuple[str, str]:
    """The first line of `Singular --version` and its version number."""
    process = subprocess.run(
        ["Singular", "--version"], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=60
    )
    _require(process.returncode == 0 and process.stdout != "", "Singular --version failed")
    banner = process.stdout.splitlines()[0]
    match = re.search(r"version (\d+\.\d+\.\d+)", banner)
    if match is None:
        raise RuntimeError(f"no version in the Singular banner {banner!r}")
    return banner, match.group(1)


def run_singular(script: str) -> dict[str, Any]:
    """Run one script from a file with stdin from /dev/null; return its RESULT values and RELATION lines."""
    with tempfile.TemporaryDirectory(prefix="weight-slice-") as directory:
        path = Path(directory) / "script.sing"
        path.write_text(script, encoding="utf-8")
        try:
            process = subprocess.run(
                [
                    "prlimit",
                    f"--as={SINGULAR_ADDRESS_SPACE_BYTES}",
                    "Singular",
                    "-q",
                    "--no-warn",
                    "--no-rc",
                    str(path),
                ],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=False,
                timeout=SINGULAR_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"Singular exceeded {SINGULAR_TIMEOUT_SECONDS} s") from error
    lines = process.stdout.splitlines()
    failed = (
        process.returncode != 0 or process.stderr.strip() != "" or any(line.lstrip().startswith("?") for line in lines)
    )
    _require(not failed, f"Singular failed ({process.returncode}): {(process.stderr + process.stdout)[-2000:]}")
    values: dict[str, list[str]] = {}
    for line in lines:
        match = RESULT_LINE.match(line)
        if match is not None:
            values.setdefault(match.group(1), []).append((match.group(2) or "").strip())
    _require(values.get("done") == ["1"], "the Singular script did not reach its end")
    return {"values": values, "relations": [line for line in lines if line.startswith("RELATION ")]}


def _integers(text: str) -> list[int]:
    return [int(token) for token in text.split(",") if token != ""]


def _triple(values: dict[str, list[str]], key: str) -> dict[str, int]:
    _require(len(values.get(key, [])) == 1, f"the Singular output lacks one {key} line")
    dimension, multiplicity, size = (int(token) for token in values[key][0].split())
    return {"dimension": dimension, "multiplicity": multiplicity, "generators": size}


def summarize_fiber_run(run: dict[str, Any]) -> dict[str, Any]:
    """The numbers of one Singular run of `fiber_script`; the control runs that stop early lack the later ones."""
    values = run["values"]

    def single(key: str) -> str:
        _require(len(values.get(key, [])) == 1, f"the Singular output lacks one {key} line")
        return str(values[key][0])

    components = sorted(
        (int(dimension), int(multiplicity), bool(int(through)))
        for dimension, multiplicity, through in (entry.split() for entry in values.get("component", []))
    )
    summary: dict[str, Any] = {
        "germ_before": _triple(values, "germ_before"),
        "components": [
            {"dimension": dimension, "multiplicity": multiplicity, "through_origin": through}
            for dimension, multiplicity, through in components
        ],
        "germ_after": _triple(values, "germ_after"),
        "germ_inhomogeneous_generators": int(single("germ_inhomogeneous")),
        "pfaffians_nonzero": int(single("pfaffian_nonzero")),
        "pfaffian_max_weight": int(single("pfaffian_max_weight")),
        "pfaffians_inhomogeneous": _integers(single("pfaffian_inhomogeneous").replace(" ", ",").strip(",")),
    }
    if "generators" in values:
        lines = sorted(str(line) for line in run["relations"])
        summary |= {
            "generator_count": int(single("generators")),
            "selected_pfaffians_one_based": _integers(single("selected")),
            "generator_weights": _integers(single("generator_weights")),
            "product_count": int(single("products").split()[0]),
            "product_max_weight": int(single("products").split()[1]),
            "relation_count": int(single("relations")),
            "relation_lines": len(lines),
            "relations_sha256": hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest(),
        }
    return summary


# ---------------------------------------------------------------------------------------------------------------------
# Reading relations and comparing the Q(i) space with the modular one


def parse_gaussian(text: str) -> tuple[Fraction, Fraction]:
    """a + b i of a Singular element of Q(i), as printed: `1`, `-1/2`, `(i)`, `(-2*i)`, `(1/2*i+1)`."""
    body = text.strip().replace(" ", "")
    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1]
    tokens = re.findall(r"[+-]?[^+-]+", body)
    _require(
        body != "" and "(" not in body and ")" not in body and "".join(tokens) == body,
        f"cannot parse the Gaussian rational {text!r}",
    )
    real, imaginary = Fraction(0), Fraction(0)
    for token in tokens:
        match = GAUSSIAN_TERM.fullmatch(token)
        if match is None or (match.group(2) or match.group(3)) is None:
            raise RuntimeError(f"cannot parse the term {token!r} of the Gaussian rational {text!r}")
        value = Fraction(match.group(2) or "1") * (-1 if match.group(1) == "-" else 1)
        if match.group(3):
            imaginary += value
        else:
            real += value
    return real, imaginary


def parse_relation(line: str) -> list[tuple[tuple[int, ...], str]]:
    """A `RELATION` line as (product index tuple, coefficient text) pairs."""
    _require(line.startswith("RELATION "), f"not a relation line: {line!r}")
    pairs = []
    for item in line.removeprefix("RELATION ").split():
        key, separator, coefficient = item.partition(":")
        _require(separator == ":" and coefficient != "", f"malformed relation term {item!r}")
        pairs.append((tuple(int(index) for index in key.split(",")), coefficient))
    return pairs


def relation_vector(line: str, prime: int, root: int, gaussian: bool) -> dict[tuple[int, ...], int]:
    """A relation as a sparse vector modulo `prime`; a Q(i) coefficient reduces with i sent to `root`."""
    vector: dict[tuple[int, ...], int] = {}
    for key, coefficient in parse_relation(line):
        if gaussian:
            real, imaginary = parse_gaussian(coefficient)
            value = sections.reduce_gaussian([str(real), str(imaginary)], prime, root)
        else:
            value = int(coefficient) % prime
        vector[key] = value
    return vector


def _rank(rows: list[dict[tuple[int, ...], int]], keys: list[tuple[int, ...]], prime: int) -> int:
    if not rows:
        return 0
    entries = [row.get(key, 0) for row in rows for key in keys]
    return int(flint.nmod_mat(len(rows), len(keys), entries, prime).rank())


def compare_reduction(gaussian_lines: list[str], modular_lines: list[str], prime: int, root: int) -> dict[str, Any]:
    """Ranks of the modular relations, the reduced Q(i) relations and their union over F_prime."""
    modular = [relation_vector(line, prime, root, False) for line in modular_lines]
    reduced = [relation_vector(line, prime, root, True) for line in gaussian_lines]
    keys = sorted({key for row in modular + reduced for key in row})
    ranks = {
        "modular_rank": _rank(modular, keys, prime),
        "reduced_rank": _rank(reduced, keys, prime),
        "joint_rank": _rank(modular + reduced, keys, prime),
    }
    return {
        "modular_relations": len(modular),
        "reduced_relations": len(reduced),
        "product_columns": len(keys),
        **ranks,
        "spaces_equal": ranks["modular_rank"] == ranks["reduced_rank"] == ranks["joint_rank"],
    }


# ---------------------------------------------------------------------------------------------------------------------
# Cells, controls and the record


@dataclass(frozen=True)
class RunItem:
    """One Singular script of the first map; `kind` names the cell or control it belongs to."""

    kind: str
    orbit: str
    source: str
    characteristic: int
    script: str


def run_item(item: RunItem) -> dict[str, Any]:
    run = run_singular(item.script)
    return {"summary": summarize_fiber_run(run), "relations": run["relations"]}


def hilbert_item(script: str) -> dict[str, Any]:
    values = run_singular(script)["values"]
    numerator = _integers(values["hilbert_first_numerator"][0])
    return {
        "relation_count": int(values["relation_count"][0]),
        "affine_dimension": int(values["dimension"][0]),
        "multiplicity": int(values["multiplicity"][0]),
        "saturated": bool(int(values["saturated"][0])),
        # The last entry of hilb(I,1) is bookkeeping of Singular's Hilbert-driven standard basis, not a coefficient.
        "first_numerator": numerator[:-1],
        "minimal_primes": sorted(_integers(text) for text in values.get("minimal_prime", [])),
    }


def cell_specs() -> list[tuple[str, str, int, int]]:
    """(orbit, source, characteristic, root of -1) of the ten Q(i) cells, then the modular cells."""
    cells = [(orbit, source, 0, 0) for orbit in ORBITS for source in SOURCES]
    return cells + [(MODULAR_ORBIT, source, MODULAR_PRIME, MODULAR_ROOT) for source in MODULAR_SOURCES]


def incidence_name(orbit: str, source: str) -> str:
    return f"{SOURCE_LABELS[source]}->{orbit}"


def field_name(characteristic: int, root: int) -> str:
    return "Q(i)" if characteristic == 0 else f"GF({characteristic}), i = {root}"


def retained_fibers() -> dict[str, dict[str, Any]]:
    """Incidence -> the fiber of the nullity-8 import record that carries it."""
    record = json.loads(IMPORT_RESULT.read_text(encoding="utf-8"))
    fibers = {}
    for fiber in record["fibers"]:
        for incidence in fiber["incidences"]:
            fibers[str(incidence)] = {
                "fiber": fiber["fiber"],
                "generators": int(fiber["generators"]),
                "quadrics": int(fiber["quadrics"]),
                "projective_dimension": int(fiber["projective_dimension"]),
                "degree": int(fiber["degree"]),
            }
    return fibers


def build_record(degree: int = DEGREE) -> dict[str, Any]:
    banner, version = singular_version()
    pieces = {piece.orbit: piece for piece in parallel.ordered_map(orbit_task, ORBITS, min_items=1)}
    specs = cell_specs()
    items = [
        RunItem(
            "cell",
            orbit,
            source,
            characteristic,
            fiber_script(pieces[orbit], source, characteristic, root, degree),
        )
        for orbit, source, characteristic, root in specs
    ]
    control_orbit, control_source = CONTROL_CELL
    wrong = tuple(EXPECTED_GRADING_WEIGHTS[position] for position in (2, 1, 0, 3, 4, 5, 6, 7, 8))
    items += [
        RunItem(
            "component_step_dropped",
            control_orbit,
            control_source,
            0,
            fiber_script(pieces[control_orbit], control_source, 0, 0, degree, component_step=False),
        ),
        RunItem(
            "wrong_weight_vector",
            "N-",
            "w8",
            0,
            fiber_script(pieces["N-"], "w8", 0, 0, degree, weights=wrong, through_pfaffians_only=True),
        ),
    ]
    runs = parallel.ordered_map(run_item, items, min_items=1)
    fibers = retained_fibers()
    cells = [
        _cell_record(
            item,
            run,
            spec[3],
            degree,
            fibers.get(incidence_name(item.orbit, item.source)),
            pieces[item.orbit].grading,
            version,
        )
        for item, run, spec in zip(items, runs, specs, strict=False)
    ]
    hilbert_positions = [position for position, spec in enumerate(specs) if spec[1] in HILBERT_SOURCES]
    scripts = [
        hilbert_script(
            runs[position]["relations"],
            runs[position]["summary"]["generator_count"],
            specs[position][2],
            specs[position][3],
        )
        for position in hilbert_positions
    ]
    for position, checked in zip(
        hilbert_positions, parallel.ordered_map(hilbert_item, scripts, min_items=1), strict=True
    ):
        cells[position]["hilbert"] = checked
    reductions = []
    for source in MODULAR_SOURCES:
        gaussian = next(position for position, spec in enumerate(specs) if spec[:3] == (MODULAR_ORBIT, source, 0))
        modular = next(
            position for position, spec in enumerate(specs) if spec[:3] == (MODULAR_ORBIT, source, MODULAR_PRIME)
        )
        comparison = compare_reduction(
            runs[gaussian]["relations"], runs[modular]["relations"], MODULAR_PRIME, MODULAR_ROOT
        )
        reductions.append(
            {
                "orbit": MODULAR_ORBIT,
                "source": source,
                "prime": MODULAR_PRIME,
                "i_root": MODULAR_ROOT,
                "same_selected_pfaffians": cells[gaussian]["selected_pfaffians_one_based"]
                == cells[modular]["selected_pfaffians_one_based"],
                **comparison,
            }
        )
    controls = _controls(runs[len(specs) :])
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": dict(parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)),
        "tools": {
            "python_flint": flint.__version__,
            "sympy": sp.__version__,
            "singular": banner,
            "singular_version": version,
        },
        "execution_contract": {
            "degree": degree,
            "singular_options": ["-q", "--no-warn", "--no-rc"],
            "singular_address_space_bytes": SINGULAR_ADDRESS_SPACE_BYTES,
            "singular_timeout_seconds": SINGULAR_TIMEOUT_SECONDS,
            "modular_prime": MODULAR_PRIME,
            "modular_root_of_minus_one": MODULAR_ROOT,
            "random_seed": "none: the scripts draw no random value and Singular is started without --random",
        },
        "scope": {
            "statement": (
                "At the retained basepoints of N+ and N- the nine slice coordinates carry a torus grading under which "
                "the 126 principal 4-Pfaffians of the Schur form are weight-homogeneous. For each of W8, E8bar, Iso, "
                "X+ and X- the germ ideal through the origin, the Nakayama generators among the Pfaffians and the "
                f"degree-{degree} relations of the fiber cone follow from standard bases truncated at a fixed weight, "
                "over Q(i) at both basepoints and modulo 32009 at N- for W8 and E8bar."
            ),
            "claim_boundary": (
                f"The relations are the degree-{degree} forms q(G) in J + m I^{degree} on the slice. The record "
                "decides the fiber cone in no other degree and retains the relation lines only as digests. The "
                "reduction comparison and the Hilbert data cover W8 and E8bar at N- over Q(i) and modulo 32009."
            ),
        },
        "basepoints": [_basepoint_record(pieces[orbit]) for orbit in ORBITS],
        "cells": cells,
        "reduction_comparison": reductions,
        "mutation_controls": controls,
        "falsifier": (
            "A grading under which a Pfaffian or a germ generator is inhomogeneous; a generator or relation count "
            "that differs from the retained value of the same incidence; a Hilbert dimension, multiplicity or "
            "saturation outside the stated values, or a first numerator that differs between Q(i) and the modular "
            "cell; a Q(i) relation space whose reduction differs in rank from the modular one; or a control that "
            "the checker accepts."
        ),
    }
    record["pass"] = verdict(record) == []
    return record


def _basepoint_record(piece: SlicePiece) -> dict[str, Any]:
    return {
        "orbit": piece.orbit,
        "boundary_point": list(piece.boundary_point),
        "torus_generators": list(TORUS_GENERATORS),
        "normal_joint_weights": [list(weights) for weights in piece.normal_weights],
        "grading_weights": list(piece.grading),
        "tangent_joint_weights": [list(weights) for weights in piece.tangent_weights],
        "kernel_joint_weights": [list(weights) for weights in piece.kernel_weights],
        "complement_joint_weights": [list(weights) for weights in piece.complement_weights],
    }


def _cell_record(
    item: RunItem,
    run: dict[str, Any],
    root: int,
    degree: int,
    retained: dict[str, Any] | None,
    grading: tuple[int, ...],
    version: str,
) -> dict[str, Any]:
    summary = run["summary"]
    incidence = incidence_name(item.orbit, item.source)
    _require(summary["pfaffians_inhomogeneous"] == [], f"{incidence}: a Pfaffian is inhomogeneous in the grading")
    _require(summary["germ_inhomogeneous_generators"] == 0, f"{incidence}: a germ generator is inhomogeneous")
    return {
        "orbit": item.orbit,
        "source": item.source,
        "incidence": incidence,
        "field": field_name(item.characteristic, root),
        "characteristic": item.characteristic,
        "i_root": root if item.characteristic else None,
        "degree": degree,
        "component_step": True,
        "grading_weights": list(grading),
        "singular_version": version,
        **summary,
        "retained_fiber": retained,
        "hilbert": None,
    }


def control_detected(control: dict[str, Any]) -> bool:
    """Whether a control run shows what the weight-slice rules reject, recomputed from the stored numbers.

    The generator count comes from the Pfaffian selection, before any product, so it does not depend on the degree.
    """
    if control["name"] == "component_step_dropped":
        return control["generator_count"] != EXPECTED_COUNTS[CONTROL_CELL][0]
    if control["name"] == "wrong_weight_vector":
        return control["inhomogeneous_pfaffians"] + control["inhomogeneous_germ_generators"] > 0
    return False


def _controls(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dropped, wrong = (run["summary"] for run in runs)
    controls = [
        {
            "name": "component_step_dropped",
            "cell": incidence_name(*CONTROL_CELL),
            "input_change": "keep the germ ideal as given instead of the intersection of its minimal primes through "
            "the origin",
            "generator_count": dropped["generator_count"],
            "relation_count": dropped["relation_count"],
        },
        {
            "name": "wrong_weight_vector",
            "cell": incidence_name("N-", "w8"),
            "input_change": "exchange the weights of s1 and s3 in the torus grading",
            "inhomogeneous_pfaffians": len(wrong["pfaffians_inhomogeneous"]),
            "inhomogeneous_germ_generators": wrong["germ_inhomogeneous_generators"],
        },
    ]
    return [{**control, "detected": control_detected(control)} for control in controls]


def verdict(record: dict[str, Any]) -> list[str]:
    """Every way the record fails its own rules; the empty list is a pass."""
    problems: list[str] = []
    degree = int(record["execution_contract"]["degree"])
    basepoints = {entry["orbit"]: entry for entry in record["basepoints"]}
    if list(basepoints) != list(ORBITS):
        problems.append("the basepoints are not N+ and N-")
    for orbit, entry in basepoints.items():
        recomputed = grading_weights(entry["normal_joint_weights"])
        if entry["grading_weights"] != recomputed:
            problems.append(f"{orbit}: the grading weights differ from 2 w_1 - w_2 of the joint weights")
        if tuple(entry["grading_weights"]) != EXPECTED_GRADING_WEIGHTS:
            problems.append(f"{orbit}: the grading weights are not the expected ones")
    expected_specs = [(orbit, source, characteristic) for orbit, source, characteristic, _ in cell_specs()]
    if [(cell["orbit"], cell["source"], cell["characteristic"]) for cell in record["cells"]] != expected_specs:
        problems.append("the cells are not the ten Q(i) cells followed by the two modular cells")
    for cell in record["cells"]:
        problems += _cell_problems(cell, degree)
        basepoint = basepoints.get(cell["orbit"])
        if basepoint is None or cell["grading_weights"] != basepoint["grading_weights"]:
            problems.append(f"{cell['incidence']} ({cell['field']}): the cell grading differs from its basepoint's")
        if cell["singular_version"] != record["tools"]["singular_version"]:
            problems.append(f"{cell['incidence']} ({cell['field']}): the cell names another Singular version")
    by_key = {(cell["orbit"], cell["source"], cell["characteristic"]): cell for cell in record["cells"]}
    for entry in record["reduction_comparison"]:
        label = f"reduction {entry['orbit']} {entry['source']}"
        modular = by_key.get((entry["orbit"], entry["source"], entry["prime"]))
        if modular is None or by_key.get((entry["orbit"], entry["source"], 0)) is None:
            problems.append(f"{label}: a cell of the comparison is missing")
            continue
        if not entry["same_selected_pfaffians"]:
            problems.append(f"{label}: the cells selected different Pfaffians")
        ranks_equal = entry["modular_rank"] == entry["reduced_rank"] == entry["joint_rank"]
        if not ranks_equal or entry["spaces_equal"] != ranks_equal:
            problems.append(f"{label}: the three ranks differ or the stored equality contradicts them")
        if entry["modular_relations"] != modular["relation_count"]:
            problems.append(f"{label}: the reduced Q(i) relation space differs from the modular one")
    if [(entry["orbit"], entry["source"]) for entry in record["reduction_comparison"]] != [
        (MODULAR_ORBIT, source) for source in MODULAR_SOURCES
    ]:
        problems.append("the reduction comparison does not cover the modular cells")
    for source in HILBERT_SOURCES:
        numerators = {
            tuple(cell["hilbert"]["first_numerator"])
            for cell in record["cells"]
            if cell["source"] == source and cell["hilbert"] is not None
        }
        if len(numerators) != 1:
            problems.append(f"{source}: the first Hilbert numerators differ between basepoints or fields")
    names = [control["name"] for control in record["mutation_controls"]]
    if names != ["component_step_dropped", "wrong_weight_vector"]:
        problems.append("the mutation controls are missing")
    for control in record["mutation_controls"]:
        if not control["detected"] or control["detected"] != control_detected(control):
            problems.append(f"the control {control['name']} was not detected")
    return problems


def _cell_problems(cell: dict[str, Any], degree: int) -> list[str]:
    label = f"{cell['incidence']} ({cell['field']})"
    problems: list[str] = []
    if not cell["component_step"]:
        problems.append(f"{label}: the component step is off")
    through = [component for component in cell["components"] if component["through_origin"]]
    if not through:
        problems.append(f"{label}: no component passes through the origin")
    else:
        top = max(component["dimension"] for component in through)
        top_multiplicity = sum(component["multiplicity"] for component in through if component["dimension"] == top)
        if (cell["germ_after"]["dimension"], cell["germ_after"]["multiplicity"]) != (top, top_multiplicity):
            problems.append(
                f"{label}: the germ after the component step differs from its components through the origin"
            )
    if cell["pfaffians_inhomogeneous"] != [] or cell["germ_inhomogeneous_generators"] != 0:
        problems.append(f"{label}: an inhomogeneous Pfaffian or germ generator")
    generators = cell["generator_count"]
    if not generators == len(cell["selected_pfaffians_one_based"]) == len(cell["generator_weights"]):
        problems.append(f"{label}: the generator lists disagree with the count")
    if cell["selected_pfaffians_one_based"] != sorted(set(cell["selected_pfaffians_one_based"])) or not all(
        1 <= index <= PFAFFIAN_COUNT for index in cell["selected_pfaffians_one_based"]
    ):
        problems.append(f"{label}: the selected Pfaffians are not increasing indices of the 126")
    if cell["product_count"] != math.comb(generators + degree - 1, degree):
        problems.append(f"{label}: the product count is not C(g + d - 1, d)")
    if cell["relation_count"] != cell["relation_lines"]:
        problems.append(f"{label}: the relation count differs from the relation lines")
    expected = EXPECTED_COUNTS[(cell["orbit"], cell["source"])]
    if generators != expected[0] or (degree == DEGREE and cell["relation_count"] != expected[1]):
        problems.append(f"{label}: (generators, relations) {(generators, cell['relation_count'])} != {expected}")
    retained = cell["retained_fiber"]
    if retained is None:
        problems.append(f"{label}: no retained fiber carries the incidence")
    elif generators != retained["generators"] or (degree == DEGREE and cell["relation_count"] != retained["quadrics"]):
        problems.append(f"{label}: the counts differ from the retained fiber {retained['fiber']}")
    hilbert = cell["hilbert"]
    if cell["source"] in HILBERT_SOURCES:
        if hilbert is None:
            problems.append(f"{label}: the Hilbert check is missing")
        elif degree == DEGREE:
            expected_hilbert = EXPECTED_HILBERT[cell["source"]]
            if (hilbert["affine_dimension"], hilbert["multiplicity"]) != expected_hilbert or not hilbert["saturated"]:
                problems.append(f"{label}: the Hilbert data differ from {expected_hilbert} or the ideal is unsaturated")
            expected_primes = EXPECTED_MINIMAL_PRIMES[cell["source"]]
            if tuple(tuple(prime) for prime in hilbert.get("minimal_primes", [])) != expected_primes:
                problems.append(f"{label}: the minimal primes differ from {expected_primes}")
            if retained is not None and (
                hilbert["affine_dimension"] != retained["projective_dimension"] + 1
                or hilbert["multiplicity"] != retained["degree"]
            ):
                problems.append(f"{label}: the Hilbert data differ from the retained fiber")
    elif hilbert is not None:
        problems.append(f"{label}: an unexpected Hilbert entry")
    return problems


# ---------------------------------------------------------------------------------------------------------------------
# Command line


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def comparable(record: dict[str, Any]) -> dict[str, Any]:
    """The record without the Singular build banner, whose date differs between the distribution and wheel binaries."""
    tools = {key: value for key, value in record["tools"].items() if key != "singular"}
    return {**record, "tools": tools}


def _self_test(record: dict[str, Any]) -> None:
    problems = verdict(record)
    _require(problems == [] and bool(record["pass"]), "the weight-slice record fails: " + "; ".join(problems))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="recompute and compare with the retained record")
    parser.add_argument("--self-test", action="store_true", help="recompute and apply the pass rules and controls")
    parser.add_argument("--degree", type=int, default=DEGREE, help="degree of the fiber cone relations (default 2)")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record(arguments.degree)
    _self_test(record)
    if arguments.out is not None:
        arguments.out.write_bytes(_record_bytes(record))
    elif arguments.check is not None:
        retained = json.loads(arguments.check.read_text(encoding="utf-8"))
        _require(
            comparable(retained) == comparable(record),
            f"{arguments.check} differs from the regenerated record",
        )


if __name__ == "__main__":
    main()
