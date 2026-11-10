"""Over Q(i), the Nakayama generators G of a fiber pair generate the full Pfaffian kernel-coordinate ideal locally.

The producer chooses G among a candidate list (a cached or recorded survivor selection). The fiber cone that A5-270
and the transfer checks describe is that of I = (FullF), all Pfaffian kernel coordinates, so G must span I / m I over
Q(i) itself. Test: every element of FullF, reduced modulo J, lies in J + m * FullF + (G) (global membership, which
implies membership in the local ring), so (G) + m I = I and Nakayama's lemma gives (G) = I at the origin. Falsifier: a
nonzero remainder. Mutation: dropping the last element of G must leave a nonzero remainder whenever G is minimal.

Writes span-<slug>.json beside this file. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/span_check.py --slug xp-nm
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reduction_check as rc  # noqa: E402

SPAN = (
    "ideal SpanF=reduce(reducedMap(FullF),ReducedJ);",
    "ideal SpanM=simplify(reduce(reducedMap(maximal),ReducedJ),2);",
    "ideal SpanBase=ReducedJ+SpanM*SpanF;",
    '"RESULT fullf_count",ncols(SpanF);"RESULT g_count",ncols(ReducedG);',
    'ideal SpanStd=std(SpanBase+ReducedG);"RESULT remainders",size(reduce(SpanF,SpanStd));',
    "ideal Dropped=ReducedG;Dropped[ncols(Dropped)]=0;",
    'ideal DropStd=std(SpanBase+Dropped);"RESULT dropped_remainders",size(reduce(SpanF,DropStd));',
)


def check(slug: str) -> dict[str, Any]:
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    outcome = rc.rees._run_singular(body + "\n".join(SPAN) + "\nquit;\n", "span_qi", 4 * rc.TIMEOUT_SECONDS)
    if outcome.status != "completed":
        raise SystemExit(f"{slug}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    remainders = int(res["remainders"])
    dropped = int(res["dropped_remainders"])
    return {
        "slug": slug,
        "field": "Q(i)",
        "fullf_count": int(res["fullf_count"]),
        "g_count": int(res["g_count"]),
        "remainders": remainders,
        "dropped_last_generator_remainders": dropped,
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "verdict": "G generates (FullF) at the origin" if remainders == 0 and dropped > 0 else "not shown",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=[spec.slug for spec in rc.fiber_inputs.SPECS])
    arguments = parser.parse_args()
    result = check(arguments.slug)
    (HERE / f"span-{arguments.slug}.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
