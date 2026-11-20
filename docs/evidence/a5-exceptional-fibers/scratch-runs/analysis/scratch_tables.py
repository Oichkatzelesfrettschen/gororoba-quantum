"""Tables from the retained plucker-map, kernel-limit, monomial-probe and Singular timing records of the scratch runs.

Usage: scratch_tables.py SCRATCH_RUNS_DIR OUT_DIR

Writes OUT_DIR/plucker-map.tsv (one row per fiber-to-Plucker-map case), OUT_DIR/kernel-limits.tsv (one row per
kernel-limit case), OUT_DIR/monomial-probes.tsv and OUT_DIR/singular-timings.tsv (wall seconds and peak resident
memory of the Singular standard-basis runs of probes/vb-levers/ladder and codex-final, with the closing RESULT line
where a log has one).
"""

import glob
import json
import os
import re
import sys

WALL = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)")
RSS = re.compile(r"Maximum resident set size \(kbytes\): (\d+)")
RESULT_MS = re.compile(r"^RESULT ms (\d+) sb_size (\d+)", re.MULTILINE)
KBASE = re.compile(r"^RESULT kbase_size (\d+)", re.MULTILINE)


def wall_seconds(text: str) -> float | None:
    match = WALL.search(text)
    if not match:
        return None
    seconds = 0.0
    for part in match.group(1).split(":"):
        seconds = seconds * 60 + float(part)
    return seconds


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def plucker_map(scratch: str, out: str) -> None:
    columns = [
        "source",
        "family",
        "slug",
        "prime",
        "order",
        "base_nullity",
        "generators",
        "arcs",
        "case",
        "samples",
        "plucker_rank",
        "veronese_ranks",
        "delta",
        "solution_dimension",
        "held_out",
        "held_out_proportional",
    ]
    with open(out, "w", encoding="ascii") as handle:
        handle.write("\t".join(columns) + "\n")
        for path in sorted(glob.glob(os.path.join(scratch, "fpm*", "*.json"))):
            item = json.loads(read(path))
            if item.get("schema") != "a5-fiber-plucker-map-v1":
                continue
            for name, case in item["cases"].items():
                row = [
                    os.path.relpath(path, scratch),
                    item["family"],
                    item["slug"],
                    item["prime"],
                    item["order"],
                    item["base_nullity"],
                    item["generators"],
                    item["arcs_with_limit"],
                    name,
                    case["samples"],
                    case["plucker_rank"],
                    json.dumps(case["veronese_ranks"], separators=(",", ":")),
                    case["delta"],
                    case["solution_dimension"],
                    case["held_out"],
                    case["held_out_proportional"],
                ]
                handle.write("\t".join(str(x) for x in row) + "\n")


def kernel_limits(scratch: str, out: str) -> None:
    columns = [
        "source",
        "family",
        "order",
        "verdict",
        "slug",
        "field",
        "arcs",
        "base_nullity",
        "arc_nullity",
        "limit_dimension",
        "g_order",
        "pivot_valuation_sum",
        "limit_in_base_kernel",
        "distinct_planes",
    ]
    with open(out, "w", encoding="ascii") as handle:
        handle.write("\t".join(columns) + "\n")
        for path in sorted(glob.glob(os.path.join(scratch, "kl*", "*-result.json"))):
            item = json.loads(read(path))
            if item.get("schema") != "a5-kernel-plucker-limits-v2":
                continue
            for case in item["cases"]:
                row = [
                    os.path.relpath(path, scratch),
                    item["family"],
                    item["order"],
                    item["verdict"],
                    case["slug"],
                    case["field"],
                    case["arcs"],
                    case["base_nullity"],
                    case["arc_nullity"],
                    case["limit_dimension"],
                    case["g_order"],
                    case["largest_pivot_valuation_sum"],
                    case["limit_in_base_kernel"],
                    case.get("distinct_planes", ""),
                ]
                handle.write("\t".join(str(x) for x in row) + "\n")


def monomial_probes(scratch: str, out: str) -> None:
    with open(out, "w", encoding="ascii") as handle:
        handle.write("source\tslug\tprime\torder\tspace\trank\tsingle_monomial_rows\tverdict\n")
        for path in sorted(glob.glob(os.path.join(scratch, "mprobe", "*.log"))):
            for line in read(path).splitlines():
                if not line.startswith("{"):
                    continue
                item = json.loads(line)
                if item.get("schema") != "a5-monomial-probe-v1":
                    continue
                for space, value in item["spaces"].items():
                    row = [
                        os.path.relpath(path, scratch),
                        item["slug"],
                        item["prime"],
                        item["order"],
                        space,
                        value["rank"],
                        value["single_monomial_rows"],
                        item["verdict"],
                    ]
                    handle.write("\t".join(str(x) for x in row) + "\n")


def singular_timings(scratch: str, out: str) -> None:
    with open(out, "w", encoding="ascii") as handle:
        handle.write("source\twall_seconds\tpeak_rss_kib\tresult_ms\tsb_size\tkbase_size\n")
        times = sorted(glob.glob(os.path.join(scratch, "probes", "vb-levers", "ladder", "*.time")))
        times += sorted(glob.glob(os.path.join(scratch, "codex-final", "*.time")))
        for path in times:
            text = read(path)
            wall = wall_seconds(text)
            rss = RSS.search(text)
            log = path[: -len(".time")] + ".log"
            ms = kbase = None
            if os.path.exists(log):
                body = read(log)
                ms = RESULT_MS.search(body)
                kbase = KBASE.search(body)
            row = [
                os.path.relpath(path, scratch),
                "" if wall is None else wall,
                rss.group(1) if rss else "",
                ms.group(1) if ms else "",
                ms.group(2) if ms else "",
                kbase.group(1) if kbase else "",
            ]
            handle.write("\t".join(str(x) for x in row) + "\n")


def main() -> int:
    scratch, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    plucker_map(scratch, os.path.join(out, "plucker-map.tsv"))
    kernel_limits(scratch, os.path.join(out, "kernel-limits.tsv"))
    monomial_probes(scratch, os.path.join(out, "monomial-probes.tsv"))
    singular_timings(scratch, os.path.join(out, "singular-timings.tsv"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
