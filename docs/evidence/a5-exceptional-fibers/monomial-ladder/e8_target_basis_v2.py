"""Standard-monomial bases of k[y]/K2 for any degree: the successor of `e8_target_rank.py prepare`.

`e8_target_rank.py prepare` accepts degrees 5 and 6 and reads HF(k[y]/sqrt(K2), d) from the `sqrt_k2` table of
`../arcs/<target>/campaign_summary.json`, which stops at degree 6. This module runs the same Singular export
(`e8_target_rank.singular_script`: `kbase(std(K2), d)` and the normal form of each standard monomial modulo the retained
`P1 cap P2 = sqrt(K2)`) and takes HF(k[y]/sqrt(K2), d) as the rank of the normal-form matrix over F_p, which is the
dimension of the image of k[y]_d in k[y]/sqrt(K2). Where the campaign table holds the degree it must agree with that
rank. The record schema is `e8_target_rank.BASIS_SCHEMA`, so `e8_target_rank.validate_basis` and the column reader of
`../arc-jets/jet_rank.py` accept it unchanged; only `producer_sha256` names this file.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_target_basis_v2.py prepare --target e8nm-p32009 \
        --degree 7 --out docs/evidence/a5-exceptional-fibers/monomial-ladder/target-records/e8nm-p32009-d7-basis.json
    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_target_basis_v2.py replay \
        docs/evidence/a5-exceptional-fibers/monomial-ladder/target-records/e8nm-p32009-d7-basis.json
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e8_target_rank as T  # noqa: E402
from arc_targets import Target  # noqa: E402

targets = T.targets


def campaign_radical_hf(target: Target, degree: int) -> int | None:
    """HF(k[y]/sqrt(K2), degree) of the retained campaign table, or None where the table stops short of it."""
    table = json.loads((target.directory / "campaign_summary.json").read_text())["hilbert"]["sqrt_k2"]
    return int(table[str(degree)]) if str(degree) in table else None


def prepare(target: Target, degree: int, singular: str, timeout: int, output: Path) -> dict[str, Any]:
    started = time.monotonic()
    sources = T.bound_inputs(target)
    monomials, normal, receipt = T.export_basis(target, degree, singular, timeout, output)
    base = int(T.coefficient_matrix(normal, target.prime).rank())
    retained = campaign_radical_hf(target, degree)
    if retained is not None and retained != base:
        raise ValueError(f"measured HF(sqrt(K2), {degree}) = {base} differs from the campaign table value {retained}")
    upper = int(targets.k2_hilbert_function(target)[str(degree)])
    rows = T.kernel_rows(normal, target.prime)
    if len(monomials) != upper or len(rows) != upper - base:
        raise ValueError("export dimensions differ from the retained K2 Hilbert function")
    record = {
        "schema": T.BASIS_SCHEMA,
        "target": target.name,
        "prime": target.prime,
        "root": target.root,
        "degree": degree,
        "nvars": targets.NGEN,
        "base_dimension": base,
        "base_dimension_source": "campaign_summary.json" if retained is not None else "rank of radical_normal_forms",
        "upper_dimension": upper,
        "target_dimension": len(rows),
        "monomials": monomials,
        "radical_normal_forms": [T.encode_polynomial(p) for p in normal],
        "target_rows": rows,
        "sources": sources,
        "producer_sha256": T.digest(Path(__file__)),
        "base_producer_sha256": T.digest(Path(T.__file__)),
        **receipt,
        "python_flint": importlib.metadata.version("python-flint"),
        "elapsed_ms": round(1000 * (time.monotonic() - started)),
        "premises": "Retained K2 membership and both dominant arc certificates; their proofs are not replayed.",
    }
    record["payload_sha256"] = T.payload_digest(record)
    T.validate_basis(record)
    T.save_record(output, record)
    return record


def replay(record: dict[str, Any], singular: str, timeout: int, scratch: Path) -> dict[str, Any]:
    """Validate the record and compare it with a fresh Singular export of the retained ideals."""
    T.validate_basis(record)
    target = targets.TARGETS[record["target"]]
    if record["producer_sha256"] != T.digest(Path(__file__)):
        raise ValueError("the record names another producer")
    if record["sources"] != T.bound_inputs(target):
        raise ValueError("the bound inputs differ from the record")
    T.verify_export(record, singular, timeout, scratch)
    return {
        "target": record["target"],
        "degree": record["degree"],
        "monomials": len(record["monomials"]),
        "status": "replayed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--target", choices=tuple(targets.TARGETS), required=True)
    prep.add_argument("--degree", type=int, required=True)
    prep.add_argument("--singular", default="Singular")
    prep.add_argument("--timeout", type=int, default=300)
    prep.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("replay")
    check.add_argument("basis", type=Path)
    check.add_argument("--singular", default="Singular")
    check.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.command == "prepare":
        if args.degree < 1:
            parser.error("--degree must be positive")
        record = prepare(targets.TARGETS[args.target], args.degree, args.singular, args.timeout, args.out)
        keys = ("target", "degree", "base_dimension", "upper_dimension", "target_dimension", "elapsed_ms")
        print(json.dumps({key: record[key] for key in keys}))
    else:
        with tempfile.TemporaryDirectory() as scratch:
            summary = replay(
                json.loads(args.basis.read_text()), args.singular, args.timeout, Path(scratch) / "replay-basis.json"
            )
        print(json.dumps(summary))


if __name__ == "__main__":
    main()
