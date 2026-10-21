"""Replay the C5 zero-divisor code against a random spherical code.

The 84 signed two-support sedenion zero divisors are the messages; message i
sends a unit-norm partner of a_i (its first partner, or its mate in a perfect
matching) and the receiver decodes by the
annihilation norm ||L_a v||. README.md fixes every definition.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

DIM = 16
SEED = 314
MESSAGES = 40
TRIALS = 400
SIGMAS = (0.0, 0.001, 0.01, 0.05, 0.10, 0.20, 0.30, 0.50, 1.00)
CHUNK = 2800


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def code_book() -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], list[tuple[int, int, int]]]]:
    """Return the 84 left factors (i, j, t) and each one's sorted partners (k, l, s)."""
    corpus = cd_core.sedenion_zero_divisor_corpus()
    lefts = sorted({(i, j, t) for i, j, t, _k, _el, _s in corpus})
    partners: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {a: [] for a in lefts}
    for i, j, t, k, el, s in corpus:
        partners[(i, j, t)].append((k, el, s))
    return lefts, {a: sorted(set(b)) for a, b in partners.items()}


def perfect_matching(
    lefts: list[tuple[int, int, int]], partners: dict[tuple[int, int, int], list[tuple[int, int, int]]]
) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    """The first perfect matching of the annihilation graph in sorted order, by depth-first search.

    The lowest unmatched vertex takes its lowest unmatched partner; a dead end
    backtracks. Every matched pair annihilates in both orders, so message a
    sends its mate and the 84 transmitted blades are distinct.
    """
    mate: dict[tuple[int, int, int], tuple[int, int, int]] = {}

    def extend() -> bool:
        free = next((a for a in lefts if a not in mate), None)
        if free is None:
            return True
        for b in partners[free]:
            if b not in mate:
                mate[free], mate[b] = b, free
                if extend():
                    return True
                del mate[free], mate[b]
        return False

    _require(extend(), "the annihilation graph has no perfect matching")
    return mate


def encoders(
    lefts: list[tuple[int, int, int]], partners: dict[tuple[int, int, int], list[tuple[int, int, int]]]
) -> dict[str, list[tuple[int, int, int]]]:
    """first_partner sends each left factor's lowest partner; matching sends its mate, injectively."""
    mate = perfect_matching(lefts, partners)
    return {"first_partner": [partners[a][0] for a in lefts], "matching": [mate[a] for a in lefts]}


def vector(support: tuple[int, int, int]) -> list[float]:
    i, j, t = support
    v = [0.0] * DIM
    v[i] = 1.0
    v[j] = float(t)
    return v


def deterministic_counts(
    lefts: list[tuple[int, int, int]],
    partners: dict[tuple[int, int, int], list[tuple[int, int, int]]],
    blades: list[tuple[int, int, int]],
) -> dict[str, Any]:
    _require(len(lefts) == 84, "the corpus must hold 84 signed left factors")
    degrees = sorted({len(b) for b in partners.values()})
    left_vectors = [vector(a) for a in lefts]
    signatures = []
    for blade in blades:
        b = vector(blade)
        signatures.append(
            tuple(j for j, a in enumerate(left_vectors) if all(x == 0.0 for x in cd_core.cd_multiply(DIM, a, b)))
        )
    ties = [len(s) for s in signatures]
    return {
        "messages": len(lefts),
        "partners_per_left_factor": degrees,
        "tie_counts_histogram": {str(n): ties.count(n) for n in sorted(set(ties))},
        "mean_ties": round(sum(ties) / len(ties), 6),
        "distinct_signatures": len(set(signatures)),
        "distinct_blades": len(set(blades)),
        "correct_annihilator_in_every_signature": all(i in s for i, s in enumerate(signatures)),
    }


def score_twins(lefts: list[tuple[int, int, int]]) -> dict[str, Any]:
    """Group the left factors by their integer Gram matrix L_a^T L_a.

    ||L_a v||^2 = v^T L_a^T L_a v, so factors sharing a Gram matrix score
    every received vector alike and the annihilation decoder cannot separate
    them at any sigma.
    """
    groups: dict[bytes, list[int]] = {}
    for index, a in enumerate(lefts):
        matrix = np.array(cd_core.left_mult_matrix(DIM, vector(a)), dtype=np.int64)
        groups.setdefault((matrix.T @ matrix).tobytes(), []).append(index)
    sizes = [len(members) for members in groups.values()]
    return {
        "gram_classes": len(groups),
        "class_size_histogram": {str(n): sizes.count(n) for n in sorted(set(sizes))},
    }


def _symbol_errors(decoded: np.ndarray, sent: np.ndarray) -> int:
    return int(np.count_nonzero(decoded != sent))


class SigmaRow:
    """One sigma's decoded rates; a module-level class so parallel.ordered_map can pickle it."""

    def __init__(
        self, random_book: np.ndarray, stack: np.ndarray, books: dict[str, np.ndarray], subset: np.ndarray
    ) -> None:
        self.random_book = random_book
        self.stack = stack
        self.books = books
        self.subset = subset

    def profile(self, y: np.ndarray) -> np.ndarray:
        out = (y @ self.stack.T).reshape(len(y), len(self.random_book), DIM)
        return np.sqrt((out * out).sum(axis=2))

    def __call__(self, item: tuple[float, np.ndarray]) -> dict[str, Any]:
        sigma, noise = item
        messages = len(self.random_book)
        sent_all = np.repeat(np.arange(messages), TRIALS)
        mask = np.isin(sent_all, self.subset)

        def rates(guess: np.ndarray) -> dict[str, Any]:
            sub_errors = _symbol_errors(guess[mask], sent_all[mask])
            all_errors = _symbol_errors(guess, sent_all)
            return {
                "ser_40": round(sub_errors / int(mask.sum()), 6),
                "ser_84": round(all_errors / len(sent_all), 6),
                "errors_40": sub_errors,
                "errors_84": all_errors,
            }

        z = noise.reshape(-1, DIM)
        rnd = self.random_book[sent_all] + sigma * z
        random_parts = [np.argmax(rnd[lo : lo + CHUNK] @ self.random_book.T, axis=1) for lo in range(0, len(z), CHUNK)]
        row: dict[str, Any] = {"sigma": sigma, "random_mf": rates(np.concatenate(random_parts))}
        for name, signal in self.books.items():
            templates = self.profile(signal)
            alg = signal[sent_all] + np.sqrt(2.0) * sigma * z
            decoded: dict[str, list[np.ndarray]] = {"c5": [], "algebraic_mf": [], "profile": []}
            for lo in range(0, len(z), CHUNK):
                y = alg[lo : lo + CHUNK]
                annihilation = self.profile(y)
                decoded["c5"].append(np.argmin(annihilation, axis=1))
                decoded["algebraic_mf"].append(np.argmax(y @ signal.T, axis=1))
                gap = annihilation[:, None, :] - templates[None, :, :]
                decoded["profile"].append(np.argmin((gap * gap).sum(axis=2), axis=1))
            row[name] = {decoder: rates(np.concatenate(parts)) for decoder, parts in decoded.items()}
        return row


def simulate(lefts: list[tuple[int, int, int]], books: dict[str, list[tuple[int, int, int]]]) -> list[dict[str, Any]]:
    """Symbol errors per sigma; every encoder sees the same seeded noise draws (common random numbers)."""
    rng = np.random.default_rng(SEED)
    subset = np.sort(rng.choice(len(lefts), size=MESSAGES, replace=False))
    random_book = rng.standard_normal((len(lefts), DIM))
    random_book /= np.linalg.norm(random_book, axis=1)[:, None]
    noise = {sigma: rng.standard_normal((len(lefts), TRIALS, DIM)) for sigma in SIGMAS}

    lmat = np.array([cd_core.left_mult_matrix(DIM, vector(a)) for a in lefts])
    signals = {name: np.array([vector(b) for b in blades]) for name, blades in books.items()}
    row = SigmaRow(random_book, lmat.reshape(len(lefts) * DIM, DIM), signals, subset)
    return parallel.ordered_map(row, [(sigma, noise[sigma]) for sigma in SIGMAS], min_items=1)


def audit() -> dict[str, Any]:
    lefts, partners = code_book()
    books = encoders(lefts, partners)
    return {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "numpy": ".".join(np.__version__.split(".")[:2]),
        "seed": SEED,
        "messages_simulated": len(lefts),
        "subset_messages": MESSAGES,
        "trials_per_message": TRIALS,
        "counts": {name: deterministic_counts(lefts, partners, blades) for name, blades in books.items()},
        "score_twins": score_twins(lefts),
        "symbol_error_rates": simulate(lefts, books),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed bytes with result.json")
    arguments = parser.parse_args()
    result = json.dumps(audit(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        retained = (Path(__file__).resolve().parent / "result.json").read_bytes()
        _require(result.encode() == retained, "replay differs from retained result bytes")
        print("C5 zero-divisor code counts and seeded error rates match the retained result")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
