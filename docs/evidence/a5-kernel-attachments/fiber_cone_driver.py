"""Degree-by-degree driver for the fiber cone F(I) = sum_d I^d / m I^d with a receipt per degree (method A).

The header file declares a ring in the translated coordinates ``t`` over F_p in ``dp``, optionally ``number I``, an
ideal ``J`` of the ambient variety and an ideal ``G`` of kernel coordinates. Degree d targets are the monomials of
degree d in ``y`` that are normal modulo the relations of lower degree (every monomial for d <= 2). Their products in
G reduce modulo J after each factor. Because the quotient (J + m P_d) / J is killed by m, the normal forms of P_d
modulo std(J + m P_d) in the global ordering span the graded piece, so rank h_d and the left kernel over F_p are
exact; each kernel vector is then re-verified by membership in std(J + m P_d).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import resource
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

SCHEMA = "a5-fiber-cone-degree-receipt-v1"
STATUS = "degree-certified"
DEFAULT_MEMORY_GIB = 3
DEFAULT_TIMEOUT_SECONDS = 900
_UNITS = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_path(path: Path | str) -> str:
    """Repository-relative spelling; a path outside this tree and the main checkout keeps its file name only."""
    resolved = Path(path).resolve()
    roots = [ROOT]
    common = subprocess.run(  # noqa: S603
        ["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if common.returncode == 0:
        roots.append((ROOT / common.stdout.strip()).resolve().parent)
    for root in roots:
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            continue
    return resolved.name


# ---------------------------------------------------------------- polynomial text -> exact F_p linear algebra

_FACTOR = re.compile(r"(\d+)|([A-Za-z_]\w*(?:\(\d+\))?)(?:\^(\d+))?")
Monomial = tuple[tuple[str, int], ...]


def parse_poly(text: str, p: int) -> dict[Monomial, int]:
    """Parse one Singular-printed polynomial over F_p into {monomial: coefficient mod p}, rejecting anything else."""
    body = re.sub(r"\s+", "", text)
    _require(body != "", "empty polynomial")
    out: dict[Monomial, int] = {}
    pos = 0
    for match in re.finditer(r"([+-]?)([^+-]+)", body):
        _require(match.start() == pos, f"unparsed text before offset {match.start()}")
        pos = match.end()
        coef = 1
        exps: dict[str, int] = {}
        for factor in match.group(2).split("*"):
            hit = _FACTOR.fullmatch(factor)
            _require(hit is not None, f"unreadable factor {factor!r}")
            if not (hit is not None):
                raise RuntimeError("missing parsed value: hit is not None")
            if hit.group(1) is not None:
                coef *= int(hit.group(1))
            else:
                exps[hit.group(2)] = exps.get(hit.group(2), 0) + (int(hit.group(3)) if hit.group(3) else 1)
        key = tuple(sorted(exps.items()))
        value = (out.get(key, 0) + (-coef if match.group(1) == "-" else coef)) % p
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    _require(pos == len(body), "trailing unparsed text")
    return out


def split_ideal(text: str) -> list[str]:
    return [piece for piece in text.replace("\n", "").split(",") if piece.strip()]


def monomial_text(key: Monomial) -> str:
    return "*".join(name if e == 1 else f"{name}^{e}" for name, e in key)


@dataclass(frozen=True)
class Kernel:
    rank: int
    relations: list[list[int]]
    rows: int
    cols: int
    nonzeros: int


def left_kernel(rows: list[dict[Monomial, int]], p: int) -> Kernel:
    """Exact rank and left kernel over F_p of the sparse row matrix (kernel vectors are coefficient lists by row)."""
    cols: dict[Monomial, int] = {}
    for row in rows:
        for key in row:
            cols.setdefault(key, len(cols))
    nonzeros = sum(len(row) for row in rows)
    if not rows:
        return Kernel(0, [], 0, 0, 0)
    if not cols:
        return Kernel(0, [[1 if i == j else 0 for i in range(len(rows))] for j in range(len(rows))], len(rows), 0, 0)
    transposed = flint.nmod_mat(len(cols), len(rows), p)
    for i, row in enumerate(rows):
        for key, value in row.items():
            transposed[cols[key], i] = value
    kernel, nullity = transposed.nullspace()
    relations = [[int(kernel[i, j]) for i in range(len(rows))] for j in range(nullity)]
    return Kernel(len(rows) - nullity, relations, len(rows), len(cols), nonzeros)


# ---------------------------------------------------------------- Singular execution


@dataclass
class Outcome:
    stage: str
    seconds: float
    peak_bytes: int | None
    results: dict[str, str]
    return_code: int
    error: str | None


def _peak(stderr: str) -> int | None:
    hit = re.search(r"Memory peak:\s*([\d.]+)([BKMGT])", stderr)
    return int(float(hit.group(1)) * _UNITS[hit.group(2)]) if hit else None


def singular_errors(text: str) -> list[str]:
    """Singular prints each interpreter or computation error as a line whose first non-blank character is `?`,
    indented inside procedures, and may continue and exit 0 afterwards."""
    return [line.strip() for line in text.splitlines() if line.lstrip().startswith("?")]


def run_singular(
    script: str,
    stage: str,
    cwd: Path,
    memory_gib: int = DEFAULT_MEMORY_GIB,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Outcome:
    """Run one script in a MemoryMax-capped transient unit; systemd-run reports the unit's memory peak on stderr."""
    cwd.mkdir(parents=True, exist_ok=True)
    (cwd / f"{stage}.sing").write_text(script)
    command = [
        "systemd-run", "--user", "--wait", "--pipe", "--same-dir",
        "-p", f"MemoryMax={memory_gib}G", "-p", "MemorySwapMax=0",
        "-E", "MALLOC_ARENA_MAX=2",
        "timeout", "-k", "10", str(timeout),
        "Singular", "-q", "--no-warn", f"{stage}.sing",
    ]  # fmt: skip
    started = time.monotonic()
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)  # noqa: S603
    seconds = time.monotonic() - started
    (cwd / f"{stage}.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    results = {m.group(1): m.group(2).strip() for m in re.finditer(r"^RESULT (\S+) ?(.*)$", proc.stdout, re.M)}
    errors = singular_errors(proc.stdout + proc.stderr)
    error = "\n".join(errors) if errors else (f"exit status {proc.returncode}" if proc.returncode else None)
    return Outcome(stage, seconds, _peak(proc.stderr), results, proc.returncode, error)


def tool_versions() -> dict[str, str]:
    def first_line(cmd: list[str]) -> str:
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)  # noqa: S603
        except (OSError, subprocess.TimeoutExpired):
            return "unavailable"
        return (done.stdout.strip().splitlines() or ["unavailable"])[0]

    return {
        "singular": first_line(["Singular", "--dump-versiontuple"]),
        "flint": str(flint.__FLINT_RELEASE__),
        "python-flint": flint.__version__,
        "macaulay2": first_line(["M2", "--version"]),
    }


# ---------------------------------------------------------------- Singular script pieces


@dataclass(frozen=True)
class Header:
    text: str
    ring: str
    prime: int
    root: str | None


def read_header(path: Path, prime: int) -> Header:
    text = path.read_text()
    ring = re.search(r"^\s*ring\s+(\w+)\s*=\s*(\d+)\s*,\s*\([^)]*\)\s*,\s*dp\s*;", text, re.M)
    _require(ring is not None, "header lacks a `ring NAME=p,(vars),dp;` line")
    if not (ring is not None):
        raise RuntimeError("missing parsed value: ring is not None")
    _require(int(ring.group(2)) == prime, f"header prime {ring.group(2)} differs from --prime {prime}")
    for name in ("J", "G"):
        _require(re.search(rf"^\s*ideal\s+{name}\s*=", text, re.M) is not None, f"header lacks `ideal {name}=`")
    root = re.search(r"number\s+I\s*=\s*([^;]+);", text)
    return Header(text.rstrip("\n") + "\n", ring.group(1), prime, root.group(1).strip() if root else None)


def products_block(header: Header, degree: int, previous: str | None) -> str:
    """Singular code defining sJ, G (reduced), the target list kb and the products P in the header ring."""
    ring = header.ring
    previous_line = f'execute("ideal K="+read("{previous}")+";");' if degree >= 3 and previous else "ideal K=0;"
    return f"""option(redSB); system("--ticks-per-sec",1000); int tm0=rtimer;
ideal sJ=std(J); int n=ncols(G); int i; int k; int f; int e; int c;
for(i=1;i<=n;i++){{G[i]=reduce(G[i],sJ);}}
ring Y={header.prime},(y(1..n)),dp;
{previous_line}
ideal sK=std(K); ideal kb=kbase(sK,{degree}); c=ncols(kb);
setring {ring}; ideal P; poly q; intvec ev;
for(i=1;i<=c;i++){{ setring Y; ev=leadexp(kb[i]); setring {ring}; q=1;
  for(f=1;f<=n;f++){{ for(e=1;e<=ev[f];e++){{ q=reduce(q*G[f],sJ); }} }} P[i]=q; }}
"RESULT generators",n; "RESULT targets",c; "RESULT products_ms",rtimer-tm0;
"""


def stage_products(header: Header, degree: int, previous: str | None) -> str:
    return (
        header.text
        + products_block(header, degree, previous)
        + f"""write(":w gens.txt",G); setring Y; write(":w targets.txt",kb); setring {header.ring};
int tm1=rtimer;
ideal Q=sJ; for(k=1;k<=nvars(basering);k++){{for(i=1;i<=c;i++){{Q=Q,var(k)*P[i];}}}}
ideal sQ=std(Q); "RESULT std_ms",rtimer-tm1,"size",size(sQ);
write(":w sq.txt",sQ);
int tm2=rtimer; ideal N=reduce(P,sQ); write(":w nf.txt",N); "RESULT reduce_ms",rtimer-tm2;
quit;
"""
    )


def stage_membership(header: Header, degree: int, previous: str | None, nrel: int, ntarget: int, coeffs: str) -> str:
    return (
        header.text
        + products_block(header, degree, previous)
        + f"""int tm1=rtimer;
execute("ideal sQ="+read("sq.txt")+";"); sQ=std(sQ);
intmat C[{nrel}][{ntarget}]={coeffs}; int bad=0; poly s; int b; int r1;
for(r1=1;r1<={nrel};r1++){{ s=0; for(b=1;b<={ntarget};b++){{ s=s+C[r1,b]*P[b]; }}
  if(reduce(s,sQ)!=0){{bad++;}} }}
"RESULT membership_failures",bad; "RESULT membership_ms",rtimer-tm1;
quit;
"""
    )


def stage_compare(header: Header, n: int, file_a: str, file_b: str) -> str:
    """Script comparing two ideals of k[y(1..n)] for equality (used by validation and certificates)."""
    return f"""option(redSB); ring Y={header.prime},(y(1..{n})),dp;
execute("ideal A="+read("{file_a}")+";"); execute("ideal B="+read("{file_b}")+";");
ideal sA=std(A); ideal sB=std(B);
"RESULT a_in_b",size(reduce(A,sB))==0; "RESULT b_in_a",size(reduce(B,sA))==0; quit;
"""


# ---------------------------------------------------------------- the degree run


def run_degree(
    header_path: Path,
    degree: int,
    previous_relations: Path | None,
    out: Path,
    prime: int,
    memory_gib: int = DEFAULT_MEMORY_GIB,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    _require(degree >= 1, "degree must be positive")
    header = read_header(header_path, prime)
    out.mkdir(parents=True, exist_ok=True)
    previous_name: str | None = None
    previous_text = ""
    if degree >= 3:
        _require(previous_relations is not None, "degree >= 3 needs --previous-relations")
        if not (previous_relations is not None):
            raise RuntimeError("missing parsed value: previous_relations is not None")
        previous_text = previous_relations.read_text().strip()
        previous_name = "previous-relations.rel"
        (out / previous_name).write_text(previous_text or "0")
    stages: dict[str, Any] = {}

    first = run_singular(stage_products(header, degree, previous_name), f"d{degree}-products", out, memory_gib, timeout)
    _require(first.error is None, f"products stage failed: {first.error}")
    stages["singular_products_std"] = {
        "wall_seconds": round(first.seconds, 3),
        "peak_bytes": first.peak_bytes,
        "products_ms": int(first.results["products_ms"]),
        "std_ms": int(first.results["std_ms"].split()[0]),
        "reduce_ms": int(first.results["reduce_ms"]),
    }
    (out / "nf.txt").replace(out / f"nf-d{degree}.txt")
    nf_path = out / f"nf-d{degree}.txt"
    targets_text = (out / "targets.txt").read_text().replace("\n", "").strip()
    targets = [parse_poly(tg, prime) for tg in split_ideal(targets_text)]
    target_names = [monomial_text(next(iter(m))) for m in targets]
    _require(all(len(m) == 1 and next(iter(m.values())) == 1 for m in targets), "targets are not monic monomials")
    _require(len(target_names) == int(first.results["targets"]), "target count differs from Singular's")
    (out / f"targets-d{degree}.txt").write_text(",\n".join(_singular_monomial(next(iter(m))) for m in targets))

    started = time.monotonic()
    rows = [parse_poly(piece, prime) for piece in split_ideal(nf_path.read_text())]
    _require(len(rows) == len(target_names), f"{len(rows)} normal forms for {len(target_names)} targets")
    kernel = left_kernel(rows, prime)
    names = [_singular_monomial(next(iter(m))) for m in targets]
    relation_texts = ["+".join(f"{c}*{names[i]}" for i, c in enumerate(vec) if c) for vec in kernel.relations]
    rel_path_out = out / f"relations-d{degree}.rel"
    rel_path_out.write_text(",\n".join(relation_texts))
    cumulative = [s for s in (previous_text, ",\n".join(relation_texts)) if s]
    (out / f"relations-upto-d{degree}.rel").write_text(",\n".join(cumulative))
    stages["linear_algebra"] = {
        "wall_seconds": round(time.monotonic() - started, 3),
        "peak_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }

    if kernel.relations:
        coeffs = ",".join(str(c) for vec in kernel.relations for c in vec)
        second = run_singular(
            stage_membership(header, degree, previous_name, len(kernel.relations), len(names), coeffs),
            f"d{degree}-membership", out, memory_gib, timeout,
        )  # fmt: skip
        _require(second.error is None, f"membership stage failed: {second.error}")
        failures = int(second.results["membership_failures"])
        _require(failures == 0, f"{failures} relation(s) failed exact membership in std(J + m P_d)")
        stages["membership"] = {
            "wall_seconds": round(second.seconds, 3),
            "peak_bytes": second.peak_bytes,
            "singular_ms": int(second.results["membership_ms"]),
        }
        membership = {"checked": len(kernel.relations), "failures": 0}
    else:
        membership = {"checked": 0, "failures": 0}

    gens_hash = hashlib.sha256((out / "gens.txt").read_bytes()).hexdigest()
    receipt = {
        "schema": SCHEMA,
        "status": STATUS,
        "degree": degree,
        "input_sha256": sha256_file(header_path),
        "input": rel_path(header_path),
        "prime": prime,
        "root_of_minus_one": header.root,
        "generator_count": int(first.results["generators"]),
        "generator_order_sha256": gens_hash,
        "previous_relations": rel_path(previous_relations) if previous_relations else None,
        "previous_relations_sha256": sha256_file(previous_relations) if previous_relations else None,
        "target_monomials": names,
        "target_monomials_sha256": hashlib.sha256(",".join(names).encode()).hexdigest(),
        "normal_form_file": rel_path(nf_path),
        "normal_form_sha256": sha256_file(nf_path),
        "matrix": {"rows": kernel.rows, "cols": kernel.cols, "nonzeros": kernel.nonzeros},
        "rank_h_d": kernel.rank,
        "relation_count": len(kernel.relations),
        "relation_file": rel_path(rel_path_out),
        "relation_sha256": sha256_file(rel_path_out),
        "membership_check": membership,
        "stage_seconds_not_cumulative": {k: v["wall_seconds"] for k, v in stages.items()},
        "stages": stages,
        "memory_cap_gib": memory_gib,
        "timeout_seconds": timeout,
        "tool_versions": tool_versions(),
    }
    (out / f"receipt-d{degree}.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def _singular_monomial(key: Monomial) -> str:
    return "*".join(name if e == 1 else f"{name}^{e}" for name, e in key)


# ---------------------------------------------------------------- bounded pool over independent items


def admitted_workers(budget_gib: int, per_job_gib: int, items: int) -> int:
    """Workers the memory budget admits: each Singular job holds up to per_job_gib, so the pool never has more
    than floor(budget / per_job) resident; the CPU count and item count cap it further."""
    _require(per_job_gib >= 1 and budget_gib >= per_job_gib, "budget must admit at least one job")
    return max(1, min(budget_gib // per_job_gib, items, parallel.workers()))


def _run_item(item: dict[str, Any]) -> dict[str, Any]:
    prev = Path(item["previous_relations"]) if item.get("previous_relations") else None
    return run_degree(
        Path(item["header"]), int(item["degree"]), prev, Path(item["out"]), int(item["prime"]),
        int(item.get("memory_gib", DEFAULT_MEMORY_GIB)), int(item.get("timeout", DEFAULT_TIMEOUT_SECONDS)),
    )  # fmt: skip


def run_batch(
    items: list[dict[str, Any]], budget_gib: int, timeout: int = DEFAULT_TIMEOUT_SECONDS
) -> list[dict[str, Any]]:
    """Run independent items (pair, degree) concurrently under a total memory budget. parallel.ordered_map
    sizes its pool from GOROROBA_WORKERS, so the admission bound is applied by chunking the items. An item's own
    "timeout" key overrides the batch timeout for that item's Singular stages."""
    items = [{"timeout": timeout, **item} for item in items]
    per_job = max(int(i.get("memory_gib", DEFAULT_MEMORY_GIB)) for i in items)
    width = admitted_workers(budget_gib, per_job, len(items))
    receipts: list[dict[str, Any]] = []
    for start in range(0, len(items), width):
        receipts.extend(parallel.ordered_map(_run_item, items[start : start + width], min_items=2))
    return receipts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--header", type=Path)
    ap.add_argument("--degree", type=int)
    ap.add_argument("--previous-relations", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--prime", type=int)
    ap.add_argument("--memory-gib", type=int, default=DEFAULT_MEMORY_GIB)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    ap.add_argument("--batch", type=Path, help="JSON list of items with header, degree, out, prime keys")
    ap.add_argument("--batch-budget-gib", type=int, default=DEFAULT_MEMORY_GIB)
    args = ap.parse_args(argv)
    if args.batch:
        receipts = run_batch(json.loads(args.batch.read_text()), args.batch_budget_gib, args.timeout)
    else:
        for name in ("header", "degree", "out", "prime"):
            _require(getattr(args, name) is not None, f"--{name} is required")
        receipts = [
            run_degree(args.header, args.degree, args.previous_relations, args.out, args.prime,
                       args.memory_gib, args.timeout)
        ]  # fmt: skip
    for r in receipts:
        print(f"degree {r['degree']} h={r['rank_h_d']} relations={r['relation_count']} status={r['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
