"""Four-qubit Pauli form of the BDSC target effect and of every sedenion zero-divisor blade effect.

Encoding. e_j maps to the computational state |j3 j2 j1 j0> with j = 8 j3 + 4 j2 + 2 j1 + j0,
so algebra index bit b sits on qubit b and a Pauli word is written q3 q2 q1 q0 (the leftmost
letter acts on q3). L_{e_m} is the signed permutation L[m ^ q][q] = cd_sign(16, m, q).

Blades. The 84 normalized blades a = (e_i + t e_j)/sqrt2 are the distinct left factors of
cd_core.sedenion_zero_divisor_corpus(): 42 index pairs (i, j), i in 1..7, j = 8 + j' with
j' in 1..7 and j' != i, times t = +-1. Each effect E_a = L_a^T L_a / 2 equals
(2 I + t (L_i^T L_j + L_j^T L_i)) / 4, an integer matrix over 4, so every Pauli coefficient
Tr(P_w E_a) / 16 is an exact dyadic rational.

Target. E0 is the blade (e1 + e10)/sqrt2:
    E0 = I/2 - YIXY/4 + YZXY/4 = I/2 - (I - Z2) T / 4,   T = Y3 X1 Y0.
Z2 and T commute, so one local product basis (Y on q3, Z on q2, X on q1, Y on q0) diagonalizes
E0. With signs z2, t = y3 x1 y0 of the measured eigenvalues, the score g = 1/2 for z2 = +1 and
(1 - t)/2 for z2 = -1 satisfies sum_outcomes g Pi_outcome = E0, so E[g] = Tr(E0 rho); the
outcome z2 = -1, t = +1 is the projector (I - Z2)(I + T)/4 onto bdsc.kernel_frame(). The score
takes values 0, 1/2 and 1, so its sample mean is a bounded mean and not a binomial proportion.

Bank. Each blade effect is I/2 + s1 P1 / 4 + s2 P2 / 4 with commuting Pauli words P1, P2, so
E = (1/2)(I + s1 P1)/2 + (1/2)(I + s2 P2)/2: a fair coin choosing one local Pauli test realizes
E as a binary effect. The 21 probes (e_i + e_{8+j})/sqrt2 with 1 <= i < j <= 7 hold 28 distinct
non-identity words. A product basis (one of X, Y, Z per qubit) measures a word when it agrees on
every non-identity letter, so a full-support word is measured only by the basis equal to it; the
13 full-support words force 13 bases into every cover, and those 13 cover all 28 words. Thirteen
is therefore the minimum number of local product bases from whose outcomes all 21 probe
expectations are linear functions; it bounds nothing about entangled measurements.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import bdsc  # noqa: E402
import cd_core  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "bdsc-pauli-v1"
DIM = 16
QUBITS = 4
TARGET_BLADE = (1, 10, 1)
TARGET_BASIS = "YZXY"
PROBE_COUNT = 21
PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
# Basis-change gates that map the named Pauli eigenbasis onto Z before a computational readout.
ROTATIONS = {"X": ("h",), "Y": ("sdg", "h"), "Z": ()}
GATES = {
    "h": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
    "sdg": np.diag([1, -1j]),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def word_matrix(word: str) -> np.ndarray:
    out = np.eye(1, dtype=complex)
    for letter in word:
        out = np.kron(out, PAULI[letter])
    return out


def left_matrix(m: int) -> np.ndarray:
    mat = np.zeros((DIM, DIM), dtype=np.int64)
    for q in range(DIM):
        mat[m ^ q, q] = cd_core.cd_sign(DIM, m, q)
    return mat


def blades() -> list[tuple[int, int, int]]:
    """(i, j, t) for the 84 distinct left factors of the zero-divisor corpus, sorted."""
    found = sorted({(i, j, t) for i, j, t, _k, _l, _s in cd_core.sedenion_zero_divisor_corpus()})
    require(len(found) == 84, f"corpus holds {len(found)} distinct left factors, expected 84")
    return found


def effect_times4(i: int, j: int, t: int) -> np.ndarray:
    """4 E_a = 2 I + t (L_i^T L_j + L_j^T L_i) for a = (e_i + t e_j)/sqrt2, exact integers."""
    li, lj = left_matrix(i), left_matrix(j)
    cross = li.T @ lj
    return 2 * np.eye(DIM, dtype=np.int64) + t * (cross + cross.T)


def decompose(times4: np.ndarray) -> dict[str, Fraction]:
    """Exact Pauli coefficients of E = times4 / 4: c_w = Tr(P_w times4) / 64."""
    out = {}
    for letters in itertools.product("IXYZ", repeat=QUBITS):
        word = "".join(letters)
        trace = complex(np.trace(word_matrix(word) @ times4))
        require(trace.imag == 0 and trace.real == round(trace.real), f"{word}: trace {trace} is not an integer")
        if trace.real:
            out[word] = Fraction(int(round(trace.real)), 64)
    rebuilt = sum((float(c) * word_matrix(w) for w, c in out.items()), np.zeros((DIM, DIM), dtype=complex))
    require(np.array_equal(rebuilt * 4, times4.astype(complex)), "Pauli expansion does not rebuild the effect")
    return out


def commute(a: str, b: str) -> bool:
    return sum(x != "I" and y != "I" and x != y for x, y in zip(a, b, strict=True)) % 2 == 0


def qubitwise(a: str, b: str) -> bool:
    return all(x == "I" or y == "I" or x == y for x, y in zip(a, b, strict=True))


def covers(basis: str, word: str) -> bool:
    return all(w == "I" or w == b for w, b in zip(word, basis, strict=True))


def eigenprojector(letter: str, sign: int) -> np.ndarray:
    return (PAULI["I"] + sign * PAULI[letter]) / 2


def outcome_projector(basis: str, signs: tuple[int, ...]) -> np.ndarray:
    out = np.eye(1, dtype=complex)
    for letter, sign in zip(basis, signs, strict=True):
        out = np.kron(out, eigenprojector(letter, sign))
    return out


def blade_entry(blade: tuple[int, int, int]) -> dict[str, Any]:
    i, j, t = blade
    terms = decompose(effect_times4(i, j, t))
    words = sorted(w for w in terms if w != "IIII")
    require(terms.get("IIII") == Fraction(1, 2), f"blade {(i, j, t)}: identity coefficient {terms.get('IIII')}")
    require(len(words) == 2, f"blade {(i, j, t)}: {len(words)} non-identity words")
    require(all(abs(terms[w]) == Fraction(1, 4) for w in words), f"blade {(i, j, t)}: coefficients not +-1/4")
    require(commute(*words), f"blade {(i, j, t)}: words {words} anticommute")
    # The coin-mixed binary effect (1/2)(I + s1 P1)/2 + (1/2)(I + s2 P2)/2 reproduces E exactly.
    mixed = sum(((np.eye(DIM) + 4 * float(terms[w]) * word_matrix(w)) / 4 for w in words), np.zeros((DIM, DIM)))
    require(
        np.array_equal(mixed * 4, effect_times4(i, j, t).astype(complex)), f"blade {(i, j, t)}: coin mixture differs"
    )
    return {
        "blade": [i, j, t],
        "terms": {w: str(terms[w]) for w in ["IIII", *words]},
        "qubitwise_commuting": qubitwise(*words),
    }


def score_identity() -> dict[str, Any]:
    """Verify E[g] = Tr(E0 rho) and the kernel indicator as operator identities in the YZXY basis."""
    times4 = effect_times4(*TARGET_BLADE)
    score = np.zeros((DIM, DIM), dtype=complex)
    kernel = np.zeros((DIM, DIM), dtype=complex)
    table = []
    for signs in itertools.product((1, -1), repeat=QUBITS):
        y3, z2, x1, y0 = signs
        t = y3 * x1 * y0
        g = Fraction(1, 2) if z2 == 1 else Fraction(1 - t, 2)
        proj = outcome_projector(TARGET_BASIS, signs)
        score += float(g) * proj
        if z2 == -1 and t == 1:
            kernel += proj
        table.append({"signs_q3q2q1q0": list(signs), "score": str(g)})
    require(np.array_equal(score * 4, times4.astype(complex)), "score operator differs from E0")
    t_op = word_matrix("YIXY")
    z2_op = word_matrix("IZII")
    ideal_kernel = (np.eye(DIM) - z2_op) @ (np.eye(DIM) + t_op) / 4
    require(np.array_equal(kernel, ideal_kernel), "kernel outcome projector differs from (I - Z2)(I + T)/4")
    require(np.allclose(kernel, bdsc.projector(), atol=1e-12), "kernel outcome projector differs from bdsc.projector()")
    require(np.allclose(times4 / 4, bdsc.ideal_effect(), atol=1e-12), "cd_core effect differs from bdsc.ideal_effect()")
    for letter, gates in ROTATIONS.items():
        u = np.eye(2, dtype=complex)
        for gate in gates:
            u = GATES[gate] @ u
        require(np.allclose(u @ PAULI[letter] @ u.conj().T, PAULI["Z"], atol=1e-12), f"rotation for {letter} fails")
    spectrum = sorted(np.linalg.eigvalsh(times4 / 4).round(12).tolist())
    require(spectrum == [0.0] * 4 + [0.5] * 8 + [1.0] * 4, f"E0 spectrum {spectrum}")
    return {
        "basis_q3q2q1q0": TARGET_BASIS,
        "rotations": {letter: list(gates) for letter, gates in ROTATIONS.items()},
        "kernel_outcome": "z2 = -1 and y3 x1 y0 = +1",
        "kernel_rank": int(round(np.trace(kernel).real)),
        "scores": table,
    }


def probe_cover(entries: dict[tuple[int, int, int], dict[str, Any]]) -> dict[str, Any]:
    probes = [(i, 8 + j, 1) for i in range(1, 8) for j in range(i + 1, 8)]
    require(len(probes) == PROBE_COUNT, f"{len(probes)} probes")
    words = sorted({w for p in probes for w in entries[p]["terms"] if w != "IIII"})
    forced = [w for w in words if "I" not in w]
    uncovered = [w for w in words if not any(covers(b, w) for b in forced)]
    require(not uncovered, f"full-support bases leave {uncovered} uncovered")
    assignment = {}
    for p in probes:
        probe_words = [w for w in entries[p]["terms"] if w != "IIII"]
        assignment[",".join(map(str, p))] = {w: next(b for b in forced if covers(b, w)) for w in probe_words}
    return {
        "probes": [list(p) for p in probes],
        "distinct_words": words,
        "qubitwise_single_basis": sum(entries[p]["qubitwise_commuting"] for p in probes),
        "minimum_bases": forced,
        "basis_for_word": assignment,
    }


def record() -> dict[str, Any]:
    keys = blades()
    entries = dict(zip(keys, parallel.ordered_map(blade_entry, keys, min_items=1), strict=True))
    target = entries[TARGET_BLADE]["terms"]
    require(target == {"IIII": "1/2", "YIXY": "-1/4", "YZXY": "1/4"}, f"E0 terms {target}")
    return {
        "schema": SCHEMA,
        "record": "pauli_form",
        "encoding": "e_j -> |j3 j2 j1 j0>, word letters q3 q2 q1 q0",
        "target": {"blade": list(TARGET_BLADE), "terms": target, "readout": score_identity()},
        "blades": [entries[b] for b in sorted(entries)],
        "probe_cover": probe_cover(entries),
    }


def write(out: Path) -> None:
    data = record()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def check(out: Path) -> None:
    data = json.loads(out.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(record(), sort_keys=True))
    require(data == fresh, f"{out} differs from the cd_core derivation; rewrite it")
    cover = data["probe_cover"]
    print(
        f"bdsc pauli: {len(data['blades'])} blade effects with three commuting terms; E0 = "
        f"{' '.join(f'{c}*{w}' for w, c in sorted(data['target']['terms'].items()))} read in "
        f"{data['target']['readout']['basis_q3q2q1q0']}; {len(cover['probes'])} probes, "
        f"{len(cover['distinct_words'])} words, {len(cover['minimum_bases'])} bases"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
