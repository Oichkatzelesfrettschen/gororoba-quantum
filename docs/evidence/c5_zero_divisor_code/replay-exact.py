"""Replay the C5 zero-divisor code against a random spherical code.

Message i is the i-th of the 84 standard zero-divisor pairs (a_i, b_i) of
Reggiani's Table 1 (docs/notes/papers/2411.18881.md): a_i = e_i + e_j,
b_i = e_k +- e_l with 1 <= i <= 6, 9 <= j <= 15, i < k <= 7, 9 <= l <= 15,
selected from cd_core's corpus in sorted order. The transmitter sends b_i and
the receiver decodes by the annihilation norm ||L_{a_j} v|| over the 84 rows.
Two alternative codebooks re-pair the 84 distinct left factors (first
partner, perfect-matching mate). README.md fixes every definition.
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
CODE_SIZE = 84
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


Support = tuple[int, int, int]
Codebook = tuple[list[Support], list[Support]]


def table1_rows() -> list[tuple[int, int, int, int, int, int]]:
    """Reggiani's Table 1: the corpus rows (i, j, +1, k, l, s) inside its index ranges, sorted."""
    rows = sorted(
        {
            (i, j, t, k, el, s)
            for i, j, t, k, el, s in cd_core.sedenion_zero_divisor_corpus()
            if t == 1 and 1 <= i <= 6 and 9 <= j <= 15 and i < k <= 7 and 9 <= el <= 15
        }
    )
    _require(len(rows) == 84, "Table 1 must hold 84 standard zero-divisor pairs")
    return rows


def codebooks(lefts: list[Support], partners: dict[Support, list[Support]]) -> dict[str, Codebook]:
    """Each codebook's (annihilator a_i, transmitted blade b_i) per message.

    table1 is the source's pair list; first_partner sends each distinct left
    factor's lowest partner, and matching sends its perfect-matching mate.
    """
    rows = table1_rows()
    mate = perfect_matching(lefts, partners)
    return {
        "table1": ([r[:3] for r in rows], [r[3:] for r in rows]),
        "first_partner": (lefts, [partners[a][0] for a in lefts]),
        "matching": (lefts, [mate[a] for a in lefts]),
    }


def vector(support: tuple[int, int, int]) -> list[int]:
    i, j, t = support
    v = [0] * DIM
    v[i] = 1
    v[j] = t
    return v


def score_classes(annihilators: list[Support]) -> dict[str, Any]:
    """Group the annihilators by their integer Gram matrix L_a^T L_a.

    ||L_a v||^2 = v^T L_a^T L_a v, so annihilators sharing a Gram matrix,
    equal or not, score every received vector alike and the annihilation
    decoder cannot separate their messages at any sigma.
    """
    groups: dict[bytes, list[int]] = {}
    for index, a in enumerate(annihilators):
        matrix = np.array(cd_core.left_mult_matrix_exact(DIM, vector(a)), dtype=np.int64)
        groups.setdefault((matrix.T @ matrix).tobytes(), []).append(index)
    sizes = [len(members) for members in groups.values()]
    return {
        "gram_classes": len(groups),
        "class_size_histogram": {str(n): sizes.count(n) for n in sorted(set(sizes))},
    }


def deterministic_counts(annihilators: list[Support], blades: list[Support]) -> dict[str, Any]:
    """Ties count the codebook's annihilators a_j with a_j * b_i = 0, the sender included."""
    _require(len(annihilators) == len(blades) == 84, "a codebook holds 84 messages")
    vectors = [vector(a) for a in annihilators]
    signatures = []
    for blade in blades:
        b = vector(blade)
        signatures.append(tuple(j for j, a in enumerate(vectors) if not any(cd_core.cd_multiply_exact(DIM, a, b))))
    _require(all(i in s for i, s in enumerate(signatures)), "every sender must annihilate its own blade")
    ties = [len(s) for s in signatures]
    distinct = [len({annihilators[j] for j in s}) for s in signatures]
    return {
        "messages": len(blades),
        "distinct_annihilators": len(set(annihilators)),
        "tie_counts_histogram": {str(n): ties.count(n) for n in sorted(set(ties))},
        "mean_ties": round(sum(ties) / len(ties), 6),
        "mean_ties_excluding_sender": round(sum(ties) / len(ties) - 1, 6),
        "distinct_annihilators_per_message_histogram": {str(n): distinct.count(n) for n in sorted(set(distinct))},
        "distinct_signatures": len(set(signatures)),
        "distinct_blades": len(set(blades)),
        "correct_annihilator_in_every_signature": all(i in s for i, s in enumerate(signatures)),
        "score_classes": score_classes(annihilators),
    }


def _symbol_errors(decoded: np.ndarray, sent: np.ndarray) -> int:
    return int(np.count_nonzero(decoded != sent))


class SigmaRow:
    """One sigma's decoded rates; a module-level class so parallel.ordered_map can pickle it."""

    def __init__(
        self, random_book: np.ndarray, books: dict[str, tuple[np.ndarray, np.ndarray]], subset: np.ndarray
    ) -> None:
        self.random_book = random_book
        self.books = books
        self.subset = subset

    @staticmethod
    def profile(stack: np.ndarray, y: np.ndarray) -> np.ndarray:
        out = (y @ stack.T).reshape(len(y), len(stack) // DIM, DIM)
        return np.sqrt((out * out).sum(axis=2))

    def __call__(self, item: tuple[float, np.ndarray]) -> dict[str, Any]:
        sigma, noise = item
        messages = len(self.random_book)
        sent_all = np.repeat(np.arange(messages), TRIALS)
        mask = np.isin(sent_all, self.subset)

        def rates(guess: np.ndarray) -> dict[str, Any]:
            sub_errors = _symbol_errors(guess[mask], sent_all[mask])
            all_errors = _symbol_errors(guess, sent_all)
            # Spread of ser_40 over 40-message draws without replacement from
            # these trials: finite-population sd of the mean of per-message rates.
            per_message = np.bincount(sent_all[guess != sent_all], minlength=messages) / TRIALS
            variance = per_message.var(ddof=1) / MESSAGES * (1 - MESSAGES / messages)
            return {
                "ser_40": round(sub_errors / int(mask.sum()), 6),
                "ser_84": round(all_errors / len(sent_all), 6),
                "errors_40": sub_errors,
                "errors_84": all_errors,
                "ser_40_draw_sd": round(float(np.sqrt(variance)), 6),
            }

        z = noise.reshape(-1, DIM)
        rnd = self.random_book[sent_all] + sigma * z
        random_parts = [np.argmax(rnd[lo : lo + CHUNK] @ self.random_book.T, axis=1) for lo in range(0, len(z), CHUNK)]
        row: dict[str, Any] = {"sigma": sigma, "random_mf": rates(np.concatenate(random_parts))}
        for name, (stack, signal) in self.books.items():
            templates = self.profile(stack, signal)
            alg = signal[sent_all] + np.sqrt(2.0) * sigma * z
            decoded: dict[str, list[np.ndarray]] = {"c5": [], "algebraic_mf": [], "profile": []}
            for lo in range(0, len(z), CHUNK):
                y = alg[lo : lo + CHUNK]
                annihilation = self.profile(stack, y)
                decoded["c5"].append(np.argmin(annihilation, axis=1))
                decoded["algebraic_mf"].append(np.argmax(y @ signal.T, axis=1))
                gap = annihilation[:, None, :] - templates[None, :, :]
                decoded["profile"].append(np.argmin((gap * gap).sum(axis=2), axis=1))
            row[name] = {decoder: rates(np.concatenate(parts)) for decoder, parts in decoded.items()}
        return row


def simulate(books: dict[str, Codebook]) -> list[dict[str, Any]]:
    """Symbol errors per sigma; every encoder sees the same seeded noise draws (common random numbers)."""
    rng = np.random.default_rng(SEED)
    subset = np.sort(rng.choice(CODE_SIZE, size=MESSAGES, replace=False))
    random_book = rng.standard_normal((CODE_SIZE, DIM))
    random_book /= np.linalg.norm(random_book, axis=1)[:, None]
    noise = {sigma: rng.standard_normal((CODE_SIZE, TRIALS, DIM)) for sigma in SIGMAS}

    arrays = {
        name: (
            np.array([cd_core.left_mult_matrix_exact(DIM, vector(a)) for a in annihilators], dtype=float).reshape(
                -1, DIM
            ),
            np.array([vector(b) for b in blades]),
        )
        for name, (annihilators, blades) in books.items()
    }
    row = SigmaRow(random_book, arrays, subset)
    return parallel.ordered_map(row, [(sigma, noise[sigma]) for sigma in SIGMAS], min_items=1)


def audit() -> dict[str, Any]:
    books = codebooks(*code_book())
    return {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "numpy": ".".join(np.__version__.split(".")[:2]),
        "seed": SEED,
        "messages_simulated": CODE_SIZE,
        "subset_messages": MESSAGES,
        "trials_per_message": TRIALS,
        "counts": {name: deterministic_counts(*book) for name, book in books.items()},
        "symbol_error_rates": simulate(books),
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
