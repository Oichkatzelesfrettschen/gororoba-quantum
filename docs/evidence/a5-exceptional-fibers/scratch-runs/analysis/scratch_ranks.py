"""Rank records of the retained scratch runs, joined with the Hilbert functions of the findings ledger.

Usage: scratch_ranks.py EVIDENCE_DIR OUT_DIR

EVIDENCE_DIR is docs/evidence/a5-exceptional-fibers. The script reads the fiber-rank engine records
(fiber-rank-linear-algebra, written by fiber_rank_v6 to v13 as .jsonl and .json) and the fast-ladder records
(float64-batched-echelon rows) under scratch-runs/, names the engine of each record by the sha256 prefix of the
engine files it finds, and compares each truncated rank r_N with the certified Hilbert function h_d of the ledger
rows of the same fiber class, prime and degree (rows whose claim reads "h_d = V" with status certified or proved).
The truncated rank at order N is a lower bound of h_d; equal means the run certifies h_d, below means a lower
bound only, above contradicts the ledger. Writes OUT_DIR/scratch-ranks.tsv and OUT_DIR/scratch-ranks-summary.tsv.
"""

import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

BY_GENERATORS = {21: "E8-bar -> N", 10: "E8-bar -> VB", 17: "Iso", 24: "W8", 15: "X"}
BY_SLUG = {"e8-nm": "E8-bar -> N", "e8-np": "E8-bar -> N", "xm-nm": "X", "xp-nm": "X", "w8-nm": "W8", "iso-nm": "Iso"}
LEDGER_FIBER = {
    "E8-bar -> N+": "E8-bar -> N",
    "E8-bar -> N-": "E8-bar -> N",
    "E8-bar -> VB": "E8-bar -> VB",
    "Iso": "Iso",
    "W8 -> N+": "W8",
    "W8 -> N-": "W8",
    "X+": "X",
    "X-": "X",
}
HILBERT = re.compile(r"^h_(\d+) = (\d+) \(degree-\d+ Hilbert function of F\(I\)\)")


def engine_names(evidence: str) -> dict[str, str]:
    names: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(evidence, "**", "fiber_rank_v*.py"), recursive=True)):
        with open(path, "rb") as handle:
            tag = hashlib.sha256(handle.read()).hexdigest()[:16]
        names.setdefault(tag, os.path.basename(path)[len("fiber_rank_") : -len(".py")])
    return names


def ledger_h(evidence: str) -> dict[tuple[str, str, int], tuple[int, str]]:
    table: dict[tuple[str, str, int], tuple[int, str]] = {}
    with open(os.path.join(evidence, "ledger.tsv"), encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for line in handle:
            row = dict(zip(header, line.rstrip("\n").split("\t"), strict=False))
            match = HILBERT.match(row.get("claim", ""))
            if not match or row["status"] not in ("certified", "proved"):
                continue
            fiber = LEDGER_FIBER.get(row["fibers"])
            if fiber is None:
                continue
            table[(fiber, row["primes"], int(match.group(1)))] = (int(match.group(2)), row["id"])
    return table


def sign_of(text: str) -> str:
    lowered = text.lower()
    for token, sign in (("np", "+"), ("n+", "+"), ("-np-", "+"), ("nm", "-"), ("n-", "-"), ("xm", "-")):
        if token in lowered:
            return sign
    return "?"


def engine_records(scratch: str, names: dict[str, str]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    paths = sorted(
        glob.glob(os.path.join(scratch, "engine", "*.jsonl"))
        + glob.glob(os.path.join(scratch, "engine", "v*", "out", "*.json"))
        + glob.glob(os.path.join(scratch, "replay", "out", "*", "replay.jsonl"))
        + glob.glob(os.path.join(scratch, "replay", "out", "*", "out.json"))
    )
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            text = handle.read().strip()
        items = [json.loads(line) for line in text.splitlines()] if path.endswith(".jsonl") else [json.loads(text)]
        for item in items:
            if item.get("check") != "fiber-rank-linear-algebra" or "r_N" not in item:
                continue
            family = BY_GENERATORS.get(item["generators"], "?")
            seconds = item.get("seconds", {})
            total = seconds.get("total") if isinstance(seconds, dict) else None
            out.append(
                {
                    "source": os.path.relpath(path, scratch),
                    "family": family,
                    "sign": sign_of(os.path.relpath(path, scratch)),
                    "prime": item["prime"],
                    "degree": item["d"],
                    "order": item["N"],
                    "engine": names.get(item.get("engine_sha256_16", ""), item.get("engine_sha256_16", "unrecorded")),
                    "mode": item.get("mode", "raw" if "dim_V" in item else "?"),
                    "r": item["r_N"],
                    "blocks": item["blocks"],
                    "dim": item.get("dim_quotient", item.get("dim_V", "")),
                    "seconds": total if total is not None else "",
                }
            )
    return out


def ladder_records(scratch: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for path in sorted(glob.glob(os.path.join(scratch, "*", "*.json"))):
        with open(path, encoding="utf-8") as handle:
            item = json.load(handle)
        if not isinstance(item, dict) or item.get("engine") != "float64-batched-echelon" or "rows" not in item:
            continue
        for row in item["rows"]:
            if "r" not in row:
                continue
            slug = item["slug"]
            out.append(
                {
                    "source": os.path.relpath(path, scratch),
                    "family": BY_SLUG.get(slug, "?"),
                    "sign": sign_of(slug),
                    "prime": item["prime"],
                    "degree": row["degree"],
                    "order": row["order"],
                    "engine": "fast-ladder",
                    "mode": "float64-batched-echelon",
                    "r": row["r"],
                    "blocks": "",
                    "dim": row.get("B", ""),
                    "seconds": row.get("seconds", ""),
                }
            )
    return out


def main() -> int:
    evidence, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    scratch = os.path.join(evidence, "scratch-runs")
    reference = ledger_h(evidence)
    records = engine_records(scratch, engine_names(evidence)) + ladder_records(scratch)
    columns = [
        "source", "family", "sign", "prime", "degree", "order", "engine", "mode", "r", "dim_or_cols", "blocks",
        "seconds", "ledger_h", "ledger_row", "relation",
    ]
    summary: Counter[tuple[str, str]] = Counter()
    with open(os.path.join(out_dir, "scratch-ranks.tsv"), "w", encoding="ascii") as handle:
        handle.write("\t".join(columns) + "\n")
        for rec in sorted(records, key=lambda r: (str(r["family"]), int(r["prime"]), int(r["degree"]), int(r["order"]))):
            ref = reference.get((str(rec["family"]), str(rec["prime"]), int(rec["degree"])))
            if ref is None:
                relation = "no ledger value"
            elif rec["r"] == ref[0]:
                relation = "equal"
            elif int(rec["r"]) < ref[0]:
                relation = "below"
            else:
                relation = "ABOVE"
            summary[(str(rec["family"]), relation)] += 1
            row = [
                rec["source"], rec["family"], rec["sign"], rec["prime"], rec["degree"], rec["order"], rec["engine"],
                rec["mode"], rec["r"], rec["dim"], rec["blocks"], rec["seconds"],
                ref[0] if ref else "", ref[1] if ref else "", relation,
            ]
            handle.write("\t".join(str(x) for x in row) + "\n")
    by_family: dict[str, dict[str, int]] = defaultdict(dict)
    for (family, relation), count in summary.items():
        by_family[family][relation] = count
    with open(os.path.join(out_dir, "scratch-ranks-summary.tsv"), "w", encoding="ascii") as handle:
        handle.write("family\trelation\trecords\n")
        for family in sorted(by_family):
            for relation in sorted(by_family[family]):
                handle.write(f"{family}\t{relation}\t{by_family[family][relation]}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
