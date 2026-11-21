"""Audit of the Singular quotient exports that the compute workstation held: digests, sidecars and quotient sizes.

Usage: exports_audit.py EXPORTS_DIR OUT_DIR

Reads every file of each export directory below EXPORTS_DIR once, writes OUT_DIR/exports-file-digests.tsv (one row per
file: directory, file, bytes, sha256), OUT_DIR/exports-audit.tsv (one row per directory: family, prime, truncation
order, engine tag, the verdict of each export.json digest and of each .sha256 sidecar, the monomial count of qB.txt and
its degree histogram, the generator count of s.txt) and OUT_DIR/exports-digest-groups.tsv (files with equal bytes in
several directories). The standard monomials in qB.txt (Singular kbase of the truncated quotient) count the dimension of
the quotient, so the count is the quotient dimension that the engine reports as dim_quotient.
"""

import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

CHUNK = 1 << 24
POWER = re.compile(r"\^(\d+)")


def sha256_of(path: str) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def monomial_degree(monomial: str) -> int:
    total = 0
    for factor in monomial.split("*"):
        if factor == "1":
            continue
        match = POWER.search(factor)
        total += int(match.group(1)) if match else 1
    return total


def degree_histogram(path: str) -> dict[int, int]:
    with open(path, encoding="ascii") as handle:
        text = handle.read().strip()
    histogram: dict[int, int] = defaultdict(int)
    for monomial in text.split(","):
        histogram[monomial_degree(monomial)] += 1
    return dict(sorted(histogram.items()))


def count_top_level_commas(path: str) -> int:
    count = 0
    with open(path, "rb") as handle:
        while block := handle.read(CHUNK):
            count += block.count(b",")
    return count


def directory_summary(path: str) -> tuple[dict[int, int], int | str]:
    """The degree histogram of qB.txt and the generator count of s.txt of one export directory."""
    names = set(os.listdir(path))
    histogram = degree_histogram(os.path.join(path, "qB.txt")) if "qB.txt" in names else {}
    generators: int | str = count_top_level_commas(os.path.join(path, "s.txt")) + 1 if "s.txt" in names else ""
    return histogram, generators


def parse_name(name: str) -> dict[str, str]:
    match = re.fullmatch(r"([a-z0-9-]+?)-p(\d+)-n(\d+)(?:-(v\d+m?))?(\..+)?", name)
    if not match:
        return {"family": name, "prime": "", "order": "", "engine": "", "suffix": ""}
    family, prime, order, engine, suffix = match.groups()
    return {"family": family, "prime": prime, "order": order, "engine": engine or "", "suffix": suffix or ""}


def main() -> int:
    exports, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    jobs = []
    for entry in sorted(os.listdir(exports)):
        path = os.path.join(exports, entry)
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                if os.path.isfile(os.path.join(path, name)):
                    jobs.append((entry, name, os.path.join(path, name)))
        elif os.path.isfile(path):
            jobs.append(("", entry, path))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda job: sha256_of(job[2]), jobs))
    digests: dict[tuple[str, str], tuple[str, int]] = {}
    with open(os.path.join(out, "exports-file-digests.tsv"), "w", encoding="ascii") as handle:
        handle.write("directory\tfile\tbytes\tsha256\n")
        for (entry, name, _), (digest, size) in zip(jobs, results, strict=True):
            if name in (".lock", ".owner"):
                continue
            digests[(entry, name)] = (digest, size)
            handle.write(f"{entry}\t{name}\t{size}\t{digest}\n")
    groups: dict[str, list[str]] = defaultdict(list)
    for (entry, name), (digest, size) in digests.items():
        if size > 0:
            groups[digest].append(f"{entry}/{name}" if entry else name)
    with open(os.path.join(out, "exports-digest-groups.tsv"), "w", encoding="ascii") as handle:
        handle.write("sha256\tcopies\tmembers\n")
        for digest, members in sorted(groups.items(), key=lambda item: -len(item[1])):
            if len(members) > 1:
                handle.write(f"{digest}\t{len(members)}\t{' '.join(sorted(members))}\n")
    header = [
        "directory",
        "family",
        "prime",
        "order",
        "engine",
        "variables",
        "export_json",
        "j_sha256",
        "g_sha256",
        "listed_files",
        "listed_match",
        "listed_mismatch",
        "listed_missing",
        "unlisted_tables",
        "sidecars_ok",
        "sidecars_bad",
        "qb_monomials",
        "qb_degree_histogram",
        "generators_s",
        "table_bytes",
    ]
    entries = [entry for entry in sorted(os.listdir(exports)) if os.path.isdir(os.path.join(exports, entry))]
    # Independent per-directory parses of qB.txt and s.txt (CPU-bound) run through parallel.ordered_map.
    summaries = dict(
        zip(
            entries,
            ordered_map(directory_summary, [os.path.join(exports, entry) for entry in entries], min_items=1),
            strict=True,
        )
    )
    with open(os.path.join(out, "exports-audit.tsv"), "w", encoding="ascii") as handle:
        handle.write("\t".join(header) + "\n")
        for entry in entries:
            path = os.path.join(exports, entry)
            info = parse_name(entry)
            files = {name: value for (e, name), value in digests.items() if e == entry}
            table_bytes = sum(size for _, size in files.values())
            record = None
            if "export.json" in files:
                with open(os.path.join(path, "export.json"), encoding="ascii") as stream:
                    record = json.load(stream)
            listed = record["files"] if record else {}
            match = sum(1 for n, d in listed.items() if n in files and files[n][0] == d)
            mismatch = [n for n, d in listed.items() if n in files and files[n][0] != d]
            missing = [n for n in listed if n not in files]
            unlisted = sorted(n for n in files if n.endswith(".txt") and n not in listed)
            ok = bad = 0
            for name in files:
                if name.endswith(".sha256"):
                    with open(os.path.join(path, name), encoding="ascii") as stream:
                        want = stream.read().split()[0]
                    target = name[: -len(".sha256")]
                    if target in files and files[target][0] == want:
                        ok += 1
                    else:
                        bad += 1
            histogram, generators = summaries[entry]
            row = [
                entry,
                info["family"],
                info["prime"],
                info["order"],
                info["engine"],
                len(record["vars"]) if record else "",
                "yes" if record else "no",
                record["J_sha256"] if record else "",
                record["G_sha256"] if record else "",
                len(listed),
                match,
                ",".join(mismatch) or "-",
                ",".join(missing) or "-",
                ",".join(unlisted) or "-",
                ok,
                bad,
                sum(histogram.values()) if histogram else "",
                json.dumps(histogram, separators=(",", ":")) if histogram else "",
                generators,
                table_bytes,
            ]
            handle.write("\t".join(str(x) for x in row) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
