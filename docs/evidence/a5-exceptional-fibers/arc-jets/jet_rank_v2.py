"""Arc-jet lower bounds on h_d of E8-bar -> N-/N+ for degrees 1 to 7: the successor of `jet_rank.py`.

`jet_rank.py` is byte-frozen because each of its 16 retained records binds its sha256, and it stops at degree 6: its
command line takes degrees 1 to 6, and `RADICAL_HF` holds the radical Hilbert function of those degrees only. This
module imports it and reuses the arc rule, the functionals of one arc (`jet_rows`), the column reader and the rank over
F_p unchanged, so a record of this module on a degree that `jet_rank.py` covers carries the same arcs, checkpoints and
rank as the retained record (the `control` mode compares them). It adds

- degree 7, whose columns are the standard monomials of K2 of `../monomial-ladder/target-records/<target>-d7-basis.json`
  (written by `../monomial-ladder/e8_target_basis_v2.py`) and whose HF(k[y]/sqrt(K2), 7) is the `base_dimension` of that
  basis, the rank of the normal forms of the standard monomials modulo sqrt(K2);
- a stall stop: with `--stall-steps N` the run ends after N consecutive steps whose rank gain is zero, status
  `stalled_below_k2_bound`, which is a lower bound and no proof of a generator of L outside K2;
- schema `a5-arc-jet-rank/2`, which lists the digest of `jet_rank.py` among the inputs beside the digest of this file.

The statements of `jet_rank.py` carry over: every row is an exact functional on k[y]_d / L_d, so the rank is at most
h_d, and with K2 inside L a rank equal to HF(k[y]/K2, d) proves h_d = HF(k[y]/K2, d) over F_p.

    $PYTHON docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank_v2.py --target e8nm-p32009 --degree 7 \
        --arcs 6000 --step 100 --stall-steps 5 \
        --write docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d7.json
    $PYTHON docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank_v2.py --check \
        docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d7.json
    $PYTHON docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank_v2.py --control \
        docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import jet_rank as J  # noqa: E402

parallel = J.parallel

SCHEMA = "a5-arc-jet-rank/2"
MAX_DEGREE = 7
# Fields of a v1 record that the v2 record of the same run must repeat; the schema, the inputs (the producer digests
# differ), the stall fields and the timing are the only differences.
CONTROL_FIELDS = (
    "target",
    "fiber",
    "prime",
    "root",
    "degree",
    "columns",
    "column_source",
    "hf_k2",
    "hf_radical",
    "families",
    "family_of_arc",
    "parameters",
    "coefficient_rule",
    "terms_per_parameter",
    "precision",
    "arcs_requested",
    "step",
    "python_flint",
    "arcs",
    "checkpoints",
    "status",
    "rank",
    "bound",
    "arcs_with_failed_check",
)


def radical_hf(target: J.Target, degree: int, source: dict[str, str]) -> tuple[int, str]:
    """HF(k[y]/sqrt(K2), degree) and where it comes from.

    Degrees 1 to 6 read the `RADICAL_HF` table of `jet_rank.py`; a basis of one of them, where it exists, must agree.
    Degree 7 reads `base_dimension` of the retained basis, which `e8_target_basis_v2.py` measures as the rank of the
    radical normal forms.
    """
    if "path" in source:
        base = int(json.loads((J.ROOT / source["path"]).read_text(encoding="utf-8"))["base_dimension"])
    else:
        base = None
    if degree in J.RADICAL_HF:
        if base is not None and base != J.RADICAL_HF[degree]:
            raise ValueError(f"basis base_dimension {base} differs from RADICAL_HF[{degree}] = {J.RADICAL_HF[degree]}")
        return J.RADICAL_HF[degree], "RADICAL_HF of jet_rank.py"
    if base is None:
        raise ValueError(f"degree {degree} has no radical Hilbert function and no basis record")
    return base, "base_dimension of the column basis record"


def stalled(checkpoints: list[dict[str, int]], steps: int | None) -> bool:
    """True when the last `steps` checkpoints each gained no rank over their predecessor."""
    if steps is None or len(checkpoints) <= steps:
        return False
    ranks = [c["rank"] for c in checkpoints[-(steps + 1) :]]
    return all(b == a for a, b in zip(ranks, ranks[1:], strict=False))


def compute(
    name: str, degree: int, narcs: int, step: int, out: Path | None, stall_steps: int | None = None
) -> dict[str, Any]:
    if not 1 <= degree <= MAX_DEGREE:
        raise ValueError(f"degree must lie between 1 and {MAX_DEGREE}")
    if narcs < 1 or step < 1:
        raise ValueError("arc count and step must be positive")
    if stall_steps is not None and stall_steps < 1:
        raise ValueError("stall steps must be positive")
    target = J.TARGETS[name]
    started = time.monotonic_ns()
    monos, source = J.columns(target, degree)
    upper = int(J.k2_hilbert_function(target)[str(degree)])
    hf_radical, radical_source = radical_hf(target, degree, source)
    inputs = J.inputs(target, source)
    inputs[J.relative(Path(__file__))] = J.sha256(Path(__file__))
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "target": name,
        "fiber": target.fiber,
        "prime": target.prime,
        "root": target.root,
        "degree": degree,
        "columns": len(monos),
        "column_source": source,
        "hf_k2": upper,
        "hf_radical": hf_radical,
        "hf_radical_source": radical_source,
        "families": [list(f) for f in J.FAMILIES],
        "family_of_arc": "FAMILIES[idx % len(FAMILIES)]",
        "parameters": list(J.PARAMETERS),
        "coefficient_rule": J.COEFFICIENT_RULE,
        "terms_per_parameter": J.NTERMS,
        "precision": J.TOP,
        "arcs_requested": narcs,
        "step": step,
        "stall_steps": stall_steps,
        "inputs": inputs,
        "python_flint": metadata.version("python-flint"),
        "arcs": [],
        "checkpoints": [],
        "status": "running",
    }
    rows: list[list[int]] = []
    current = 0
    stop = "arc budget"
    for start in range(0, narcs, step):
        jobs = [(name, idx, degree, monos) for idx in range(start, min(start + step, narcs))]
        for result in parallel.ordered_map(J.jet_rows, jobs, min_items=2):
            rows.extend(result.pop("rows"))
            record["arcs"].append(result)
        current = J.rank(rows, len(monos), target.prime)
        record["checkpoints"].append({"arcs": len(record["arcs"]), "rows": len(rows), "rank": current})
        record["elapsed_ms"] = (time.monotonic_ns() - started) // 1_000_000
        if out is not None:
            out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(record["checkpoints"][-1]), file=sys.stderr, flush=True)
        if current >= upper:
            stop = "k2 bound reached"
            break
        if stalled(record["checkpoints"], stall_steps):
            stop = "stall"
            break
    bad = [a["index"] for a in record["arcs"] if a["j_nonzero"] or a["k2_nonzero"]]
    if current > upper or bad:
        record["status"] = "inconsistent"
    elif current == upper:
        record["status"] = "equal_to_k2_bound"
    elif stop == "stall":
        record["status"] = "stalled_below_k2_bound"
    else:
        record["status"] = "lower_bound_only"
    record["stop_reason"] = stop
    record["rank"] = current
    record["bound"] = f"{current} <= h_{degree} <= {upper}"
    record["arcs_with_failed_check"] = bad
    record["elapsed_ms"] = (time.monotonic_ns() - started) // 1_000_000
    if out is not None:
        out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def control(path: Path) -> dict[str, Any]:
    """Recompute a retained v1 record through this module and compare every field of CONTROL_FIELDS and the inputs.

    The v2 inputs must equal the v1 inputs plus the digest of this file.
    """
    old = json.loads(path.read_text(encoding="utf-8"))
    if old["schema"] != J.SCHEMA:
        raise SystemExit(f"{path}: not a {J.SCHEMA} record")
    fresh = compute(old["target"], old["degree"], old["arcs_requested"], old["step"], None)
    differing = [k for k in CONTROL_FIELDS if fresh[k] != old[k]]
    own = J.relative(Path(__file__))
    extra = {k: v for k, v in fresh["inputs"].items() if k != own}
    if extra != old["inputs"]:
        differing.append("inputs")
    if differing:
        raise SystemExit(f"{path}: the v2 recomputation differs in {differing}")
    return {
        "control": "identical",
        "target": old["target"],
        "degree": old["degree"],
        "rank": old["rank"],
        "arcs": len(old["arcs"]),
        "fields": len(CONTROL_FIELDS) + 1,
    }


def strip_times(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "elapsed_ms"}


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--target", choices=sorted(J.TARGETS), default="e8nm-p32009")
    parser.add_argument("--degree", type=int, choices=range(1, MAX_DEGREE + 1))
    parser.add_argument("--arcs", type=int, default=1200)
    parser.add_argument("--step", type=int, default=100)
    parser.add_argument("--stall-steps", type=int, default=None, help="stop after this many steps with no rank gain")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, help="compute and write the record, rewritten at every checkpoint")
    mode.add_argument("--check", type=Path, help="recompute a v2 record from its own parameters and compare")
    mode.add_argument("--control", type=Path, help="recompute a retained v1 record through this module and compare")
    args = parser.parse_args()
    if args.stall_steps is not None and args.stall_steps < 1:
        parser.error("--stall-steps must be positive")
    if args.write is not None:
        if args.degree is None:
            parser.error("--write needs --degree")
        record = compute(args.target, args.degree, args.arcs, args.step, args.write, args.stall_steps)
        print(json.dumps({k: record[k] for k in ("target", "degree", "rank", "hf_k2", "status", "stop_reason")}))
    elif args.control is not None:
        print(json.dumps(control(args.control)))
    else:
        old = json.loads(args.check.read_text(encoding="utf-8"))
        if old["schema"] != SCHEMA:
            raise SystemExit(f"{args.check}: not a {SCHEMA} record")
        fresh = compute(old["target"], old["degree"], old["arcs_requested"], old["step"], None, old["stall_steps"])
        if strip_times(fresh) != strip_times(old):
            raise SystemExit(f"{args.check}: the recomputed record differs")
        print(json.dumps({"check": "identical", "target": old["target"], "degree": old["degree"], "rank": old["rank"]}))


if __name__ == "__main__":
    main()
