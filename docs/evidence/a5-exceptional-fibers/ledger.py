"""Check and summarize the A_5 exceptional-fiber claim ledger (`ledger.tsv`).

The ledger holds one row per claim of the program: every equation computed (a Hilbert-function value, a rank, a
degree), every structural statement (radical, prime, Cohen-Macaulay, a decomposition, a fiber inclusion), every method
claim and every operational finding, with its status after justification and falsification, the evidence that
decides it, and the test that would overturn it. Failures stay in the ledger with status refuted, rejected,
superseded or stalled, so the record shows what was tried as well as what survives.

Columns (tab-separated, first line is the header):

- id: stable key, `A5-` and a number; never reused.
- kind: equation | structure | method | operational.
- fibers: the pairs Y -> Z the claim concerns, comma-separated, or `all`.
- primes: 32003, 32009, 32029, `both` (32009 and 32029), `char0`, or `any` (a statement independent of the field).
- claim: the statement, with equations written out.
- status: one of STATUSES below.
- basis: the deciding evidence in words (the measured numbers, the argument).
- evidence: repository-relative paths, `;`-separated, each of which must exist.
- falsifier: the test or observation that would change the status; `none` for a theorem or a closed refutation.
- supersedes: ids this row replaces, `;`-separated, or empty. Every id named here has status `superseded`, and every
  `superseded` row is named by a row that is not itself `superseded`, so the pointer runs from the live successor to
  the row it replaced.
- updated: the date of the last status change (YYYY-MM-DD).

    $PYTHON docs/evidence/a5-exceptional-fibers/ledger.py [--check] [--summary] [--open]
"""

import argparse
import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = HERE / "ledger.tsv"
COLUMNS = [
    "id",
    "kind",
    "fibers",
    "primes",
    "claim",
    "status",
    "basis",
    "evidence",
    "falsifier",
    "supersedes",
    "updated",
]
KINDS = {"equation", "structure", "method", "operational"}
PRIMES = {"32003", "32009", "32029", "both", "char0", "any"}
STATUSES = {
    "proved": "a complete argument or exact computation decides it over the stated fields",
    "certified": "a lower bound and a matching upper bound decide the value",
    "survives": "consistent with every test that ran; the falsifier names the test still owed",
    "open": "no deciding test yet",
    "refuted": "a measurement or an argument contradicts it",
    "rejected": "dropped on an argument without a measurement",
    "superseded": "replaced by a stronger or cheaper route, named in basis or by a supersedes link",
    "stalled": "a computation that would decide it did not finish; the evidence records the cost",
    "boundary": "outside what the current records can decide; the evidence names the follow-up",
}
# The statuses of a row whose falsifier or deciding test is still outstanding; `--open` lists these rows.
OPEN_STATUSES = frozenset({"survives", "open", "stalled", "boundary"})
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^A5-\d{3}$")


def rows() -> list[dict[str, str]]:
    with LEDGER.open(newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames != COLUMNS:
            raise SystemExit(f"header {reader.fieldnames} differs from {COLUMNS}")
        return list(reader)


def check(data: list[dict[str, str]]) -> list[str]:
    problems: list[str] = []
    ids = [r["id"] for r in data]
    for dup in sorted(k for k, v in Counter(ids).items() if v > 1):
        problems.append(f"{dup}: id used more than once")
    known = set(ids)
    status = {r["id"]: r["status"] for r in data}
    for r in data:
        rid = r["id"]
        if not ID.match(rid):
            problems.append(f"{rid}: id is not A5-NNN")
        if r["kind"] not in KINDS:
            problems.append(f"{rid}: kind {r['kind']!r}")
        if r["primes"] not in PRIMES:
            problems.append(f"{rid}: primes {r['primes']!r}")
        if r["status"] not in STATUSES:
            problems.append(f"{rid}: status {r['status']!r}")
        if not r["claim"].strip() or not r["falsifier"].strip():
            problems.append(f"{rid}: empty claim or falsifier")
        if not DATE.match(r["updated"]):
            problems.append(f"{rid}: updated {r['updated']!r}")
        paths = [x.strip() for x in r["evidence"].split(";") if x.strip()]
        if not paths:
            problems.append(f"{rid}: no evidence")
        for path in paths:
            if not (ROOT / path.split("#")[0]).exists():
                problems.append(f"{rid}: evidence {path} does not exist")
        for sup in [x.strip() for x in r["supersedes"].split(";") if x.strip()]:
            if sup not in known:
                problems.append(f"{rid}: supersedes unknown {sup}")
            elif sup == rid:
                problems.append(f"{rid}: supersedes itself")
            elif status[sup] != "superseded":
                problems.append(f"{rid}: supersedes {sup}, whose status is {status[sup]}, not superseded")
    named = {x.strip() for r in data if r["status"] != "superseded" for x in r["supersedes"].split(";") if x.strip()}
    for r in data:
        if r["status"] == "superseded" and r["id"] not in named:
            problems.append(f"{r['id']}: superseded, and no live row names it in supersedes")
    return problems


def uncited_directories(data: list[dict[str, str]], directories: list[str]) -> list[str]:
    """The directories, as repository-relative paths, under which no row cites an evidence path."""
    cited = [x.strip() for r in data for x in r["evidence"].split(";") if x.strip()]
    return [d for d in directories if not any(path == d or path.startswith(d + "/") for path in cited)]


def a5_directories() -> list[str]:
    """Every `docs/evidence/a5-*` directory that holds a tracked file; `--check` requires a citing row for each.

    The tracked files come from `git ls-files`, so an ignored or leftover directory does not count; outside a git
    checkout, or on a host with no git executable, every such directory on disk counts.
    """
    try:
        listing = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "docs/evidence/a5-*"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        listing = None
    if listing is not None and listing.returncode == 0:
        return sorted({"/".join(line.split("/")[:3]) for line in listing.stdout.splitlines() if line.count("/") >= 3})
    return sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "evidence").glob("a5-*") if p.is_dir())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="validate the ledger and require a citing row for every a5-* evidence directory; exit 1 on any problem",
    )
    ap.add_argument("--summary", action="store_true", help="counts by status and kind")
    ap.add_argument(
        "--open",
        action="store_true",
        help="list all rows with outstanding falsifiers (survives, open, stalled, boundary)",
    )
    a = ap.parse_args()
    data = rows()
    problems = check(data)
    if a.check:
        uncited = uncited_directories(data, a5_directories())
        problems += [f"{d}: no ledger row cites this evidence directory" for d in uncited]
    for line in problems:
        print(line)
    if a.summary or not (a.check or a.open):
        print("rows", len(data))
        for status, n in sorted(Counter(r["status"] for r in data).items()):
            print(f"  {status:<10} {n:>4}  {STATUSES[status] if status in STATUSES else ''}")
        print("by kind", dict(sorted(Counter(r["kind"] for r in data).items())))
    if a.open:
        for r in data:
            if r["status"] in OPEN_STATUSES:
                print(f"{r['id']}\t{r['status']}\t{r['fibers']}\t{r['claim'][:110]}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
