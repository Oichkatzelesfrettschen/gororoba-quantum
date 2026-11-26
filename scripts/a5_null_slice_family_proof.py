"""Checks of the proof that the two so(m,1) null-slice families hold for every n (ledger A5-618, A5-626, A5-636).

chi_n(a, tau, k) = s(tau, k) s(a, tau ^ k) s(a, k) s(tau, a ^ k), s = cd_core.cd_sign, is +1 exactly where L_a and
L_tau commute on e_k. The proof in docs/evidence/a5-null-slice-family-proof/README.md rests on:

- Step 0, the four-case recursion of cd_sign on the top bit H = 2^(n-1) (read from the loop of cd_core.cd_sign);
- I1 to I3: s(x, 0) = s(0, x) = 1, s(x, x) = -1 for x != 0, s(x, y) = -s(y, x) for distinct nonzero x, y;
- Lemma T: chi_n(a, H, k) = -1 for every a outside {0, H} and every k;
- Lemma U: for distinct nonzero a, t < H, chi_n(a, t, k) = chi_(n-1)(a, t, k mod H);
- Lemma R: for nonzero a < H and t < H outside {0, a}, chi_n(a, H + t, k) = sigma(k mod H) chi_(n-1)(a, t, k mod H),
  sigma = +1 on {0, a, t, a ^ t} and -1 elsewhere.

Each lemma is an n-independent sign identity proved by the case split in the README; this record checks every case
exhaustively at the levels named, checks the recursion table against cd_core.cd_sign, and checks the family claim
C_a = T u (T ^ a ^ tau) from the table at n = 4 to 12. Levels run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

TABLE_LEVEL = 12
CD_CORE_LEVELS = tuple(range(1, 11))
IDENTITY_LEVELS = tuple(range(1, 13))
T_LEVELS = tuple(range(1, 12))
RU_LEVELS = tuple(range(2, 10))
FAMILY_LEVELS = tuple(range(4, 13))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def recursion_table(level: int) -> Any:
    """s_level(p, q) from the four cases of Step 0, built up from s_0 = [[1]]."""
    table = np.ones((1, 1), dtype=np.int8)
    for _ in range(level):
        half = table.shape[0]
        new = np.empty((2 * half, 2 * half), dtype=np.int8)
        new[:half, :half] = table
        new[:half, half:] = table.T
        low = table.copy()
        low[:, 1:] *= -1
        new[half:, :half] = low
        high = table.T.copy()
        high[:, 0] = -1
        new[half:, half:] = high
        table = new
    return table


def chi(table: Any, a: int, tau: int, k: Any) -> Any:
    return table[tau, k] * table[a, tau ^ k] * table[a, k] * table[tau, a ^ k]


def sigma(k: Any, members: list[int]) -> Any:
    return np.where(np.isin(k, members), 1, -1)


def check_item(task: tuple[str, int]) -> int:
    """Failures of one check at one level."""
    name, level = task
    table = recursion_table(level).astype(np.int16)
    dimension = 1 << level
    half = dimension >> 1
    k = np.arange(dimension)
    if name == "cd_core":
        reference = np.array([[cd_core.cd_sign(dimension, p, q) for q in range(dimension)] for p in range(dimension)])
        return int(np.count_nonzero(reference != table))
    if name == "identities":
        off = ~np.eye(dimension, dtype=bool)
        off[0, :] = False
        off[:, 0] = False
        return int(
            np.count_nonzero(table[:, 0] != 1)
            + np.count_nonzero(table[0, :] != 1)
            + np.count_nonzero(np.diag(table)[1:] != -1)
            + np.count_nonzero((table + table.T)[off] != 0)
        )
    if name == "T":
        return sum(int(np.any(chi(table, a, half, k) != -1)) for a in range(1, dimension) if a != half)
    previous = recursion_table(level - 1).astype(np.int16)
    reduced = k % half
    failures = 0
    for a in range(1, half):
        for t in range(1, half):
            if t == a:
                continue
            if name == "U":
                failures += int(np.any(chi(table, a, t, k) != chi(previous, a, t, reduced)))
            else:
                factor = sigma(reduced, [0, a, t, a ^ t])
                failures += int(np.any(chi(table, a, half + t, k) != factor * chi(previous, a, t, reduced)))
    return failures


def family_item(level: int) -> dict[str, Any]:
    table = recursion_table(level).astype(np.int16)
    dimension = 1 << level
    k = np.arange(dimension)
    h = 1 << (level - 3)
    families = [("time 7 * 2^(n-3)", 7 * h, [i for i in range(1, 2 * h) if i != h], h, 2 * h)]
    if level >= 6:
        q = 1 << (level - 2)
        families.append(("octonion space", 2 * q + q + 8, list(range(1, 8)), 8, q))
    rows = []
    for family, tau, space, u, v in families:
        common = {u, v, tau ^ u, tau ^ v}
        failures = 0
        support: set[int] = set()
        for a in space:
            found = set(np.nonzero(chi(table, a, tau, k) == 1)[0].tolist())
            failures += int(found != common | {t ^ a ^ tau for t in common})
            support |= found
        clifford = all(bool(np.all(chi(table, a, b, k) == -1)) for a in space for b in space if a < b)
        rows.append(
            {
                "family": family,
                "level": level,
                "space_size": len(space),
                "failures": failures,
                "common_kernel": dimension - len(support),
                "space_clifford": clifford,
            }
        )
    return {"level": level, "rows": rows}


def compute() -> dict[str, Any]:
    tasks = [("cd_core", n) for n in CD_CORE_LEVELS]
    tasks += [("identities", n) for n in IDENTITY_LEVELS]
    tasks += [("T", n) for n in T_LEVELS]
    tasks += [("U", n) for n in RU_LEVELS] + [("R", n) for n in RU_LEVELS]
    failures = parallel.ordered_map(check_item, tasks, min_items=1)
    checks: dict[str, dict[str, int]] = {}
    for (name, level), count in zip(tasks, failures, strict=True):
        checks.setdefault(name, {})[str(level)] = count
    families = parallel.ordered_map(family_item, list(FAMILY_LEVELS), min_items=1)
    return {
        "schema": "a5-null-slice-family-proof/1",
        "checks": checks,
        "families": [row for item in families for row in item["rows"]],
    }


def validate(result: dict[str, Any]) -> None:
    expected_levels = {
        "cd_core": CD_CORE_LEVELS,
        "identities": IDENTITY_LEVELS,
        "T": T_LEVELS,
        "U": RU_LEVELS,
        "R": RU_LEVELS,
    }
    for name, levels in expected_levels.items():
        row = result["checks"][name]
        require(sorted(int(n) for n in row) == list(levels), f"{name} levels")
        require(all(count == 0 for count in row.values()), f"{name} failures {row}")
    families = result["families"]
    require(len(families) == 16 and all(row["failures"] == 0 for row in families), "family claims")
    for row in families:
        n = row["level"]
        first = row["family"].startswith("time")
        require(row["common_kernel"] == (4 if first else (1 << n) - 32), f"common kernel {row}")
        require(row["space_size"] == ((1 << (n - 2)) - 2 if first else 7), f"space size {row}")
        if not first:
            require(row["space_clifford"], f"octonion space not Clifford {row}")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    table = recursion_table(5).astype(np.int16)
    previous = recursion_table(4).astype(np.int16)
    k = np.arange(32)
    reduced = k % 16
    lhs = chi(table, 3, 16 + 5, k)
    right = chi(previous, 3, 5, reduced)
    control(
        bool(np.all(lhs == sigma(reduced, [0, 3, 5, 6]) * right)),
        bool(np.all(lhs == sigma(reduced, [0, 3, 5]) * right)),
        "peel set",
    )
    control(bool(np.all(chi(table, 3, 16, k) == -1)), bool(np.all(chi(table, 3, 16 + 5, k) == -1)), "top unit")
    broken = recursion_table(5)
    broken[17, 3] = -broken[17, 3]
    reference = np.array([[cd_core.cd_sign(32, p, q) for q in range(32)] for p in range(32)])
    control(
        bool(np.array_equal(recursion_table(5), reference)), bool(np.array_equal(broken, reference)), "recursion table"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 3 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
