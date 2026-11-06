"""Build the A_5 exceptional-fiber claim registry from retained records.

Usage: build_registry.py [--check] SCAN_DIR...

h_d = dim I^d / m I^d of the fiber cone F(I) is certified at a prime when a bound lower bound equals a verified upper
bound. Upper bounds: h_1 <= #G always; for d >= 2, h_d <= HF(k[y]/K2, d) (`k2-hilbert.jsonl`) once K2 lies in L,
which a validated degree-2 membership receipt for the same fiber and prime carries, provided a `k2-span` row of
`witnesses.jsonl` shows the receipt's relation file and every K2 source of `k2-hilbert.jsonl` span the same space in
the same generator order. Lower bounds:
- degree-by-degree membership rank: a `receipt-dD.json` under working/ whose own prime, status `degree-certified`,
  zero membership failures and input sha256 check out against a known header of that fiber and prime;
- truncated rank r_N <= h_d: a JSON record whose engine sha256 matches engine bytes found under the scan roots, whose
  header sha256 matches a canonical producer header or a legacy input with a `header-pair` witness, and whose header
  ring prime and generator count agree with the fiber.
A record that fails a binding check is listed in `unbound.jsonl` and certifies nothing. A degree whose lower bound
meets the K2 count without a verified upper bound reads `lower bound equals candidate count`. An ok
`sign-isomorphism` row of `witnesses.jsonl` makes the two fiber cones isomorphic graded rings at that prime, so a degree
certified for either fiber is certified for both, with the K2 counts required equal and the transport recorded.
--check rebuilds the outputs in memory and exits 1 when any differs from the retained copy.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE / "working"
CANON_DIRS = {32009: "build/inputs/p32009-r10754", 32029: "build/inputs/p32029-r9115"}
STEM_FIBER = {
    "xm-nm": "X-",
    "xp-np": "X+",
    "e8-nm": "E8-bar -> N-",
    "e8-np": "E8-bar -> N+",
    "e8-vb": "E8-bar -> VB",
    "iso-np": "Iso",
    "iso-nm": "Iso",
    "w8-nm": "W8 -> N-",
    "w8-np": "W8 -> N+",
}
GENERATORS = {
    "X-": 15,
    "X+": 15,
    "E8-bar -> VB": 10,
    "Iso": 17,
    "E8-bar -> N-": 21,
    "E8-bar -> N+": 21,
    "W8 -> N-": 24,
    "W8 -> N+": 24,
}

# Inputs outside the canonical producer directories that certificates name: header sha256 prefix -> (fiber, prime,
# path under working/ or this directory). Each needs an `ok` header-pair row in witnesses.jsonl to certify.
LEGACY_HEADERS = {
    "982b0f329104552d": ("Iso", 32009, "distribute/out/a5-iso-d4/iso_p1/d4/d4-products.sing"),
    "12c2026acce4afa7": ("Iso", 32029, "replay/inputs/iso-np-p32029-d4-products.sing"),
    "59c26c9143dab52f": ("W8 -> N-", 32009, "inputs/w8_nm_fiber.sing"),
    "e3b426730d222721": ("W8 -> N-", 32029, "distribute/out/a5-p2-w8/w8_p2/d3/d3-products.sing"),
    "d9d7a00ee18d171b": ("E8-bar -> N-", 32009, "inputs/e8_nm_fiber.sing"),
    "f6ad8f9c7cc69b3f": ("E8-bar -> N-", 32009, "distribute/out/a5-e8-d2/e8nm_p1/d2/d2-products.sing"),
    "a8f90b44267c302e": ("E8-bar -> N+", 32009, "inputs/e8_np_fiber.sing"),
    "2f8c9727fc2e4484": ("E8-bar -> N-", 32029, "distribute/out/a5-e8-d2/e8nm_p2/d2/d2-membership.sing"),
    "fefdacab7fff6ea7": ("E8-bar -> N+", 32029, "distribute/out/a5-e8-d2/e8np_p2/d2/d2-membership.sing"),
    "69228f988f9b8444": ("X-", 32009, "distribute/out/a5-xm-d4/xm_p1/d2/d2-membership.sing"),
    "a2f22fbddf2ea707": ("X-", 32009, "build/logs/part-b/hdr/xm.sing"),
    "cefd373c26d610ac": ("E8-bar -> VB", 32009, "build/logs/part-b/hdr/vb.sing"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fresh(witness: dict, fields: tuple[str, ...]) -> dict:
    """Admit a witness only while every relation file it compared still holds the bytes it recorded."""
    for field in fields:
        if witness[field] is not None and sha(HERE / witness[field]) != witness.get(f"{field}_sha256"):
            raise SystemExit(f"stale {witness['kind']} witness: {witness[field]} differs from the compared bytes")
    return witness


def header_file(rel: str) -> Path:
    p = W / rel
    return p if p.exists() else HERE / rel


def header_facts(path: Path) -> tuple[int, int]:
    """Ring characteristic and number of G generators of a Singular header."""
    text = path.read_text().replace("\n", "")
    m = re.search(r"ring r=(\d+),", text)
    g = re.search(r"ideal G=([^;]*);", text)
    if m is None or g is None:
        raise RuntimeError(f"{path}: no ring line or ideal G")
    return int(m.group(1)), len([x for x in g.group(1).split(",") if x.strip()])


def known_headers(witness_ok: set[str]) -> dict[str, dict]:
    """sha256 (full) -> fiber, prime, path: canonical producer headers and witnessed legacy inputs."""
    table: dict[str, dict] = {}
    for prime, d in CANON_DIRS.items():
        for path in sorted((W / d).glob("*.sing")):
            fiber = STEM_FIBER.get(path.stem)
            if fiber is not None:
                rel = str(path.relative_to(HERE))
                table[sha(path)] = {"fiber": fiber, "prime": prime, "path": rel, "kind": "canonical"}
    for prefix, (fiber, prime, rel) in LEGACY_HEADERS.items():
        path = header_file(rel)
        full = sha(path)
        if not full.startswith(prefix):
            raise RuntimeError(f"{rel}: sha256 {full[:16]} differs from its map key {prefix}")
        if str(path.relative_to(HERE)) in witness_ok:
            table[full] = {"fiber": fiber, "prime": prime, "path": str(path.relative_to(HERE)), "kind": "witnessed"}
    for h in table.values():
        p, n = header_facts(HERE / h["path"])
        if p != h["prime"] or n != GENERATORS[h["fiber"]]:
            raise RuntimeError(f"{h['path']}: ring {p}, {n} generators against {h['fiber']} at {h['prime']}")
    return table


def k2_table() -> dict[tuple[str, int], dict]:
    table: dict[tuple[str, int], dict] = {}
    for ln in (HERE / "k2-hilbert.jsonl").read_text().splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        key = (r["fiber"], r["prime"])
        if key in table and table[key]["h"] != r["h"]:
            raise RuntimeError(f"two K2 sources disagree for {key}")
        table.setdefault(key, {"h": r["h"], "sources": []})["sources"].append(
            {"path": "working/" + r["relations"], "sha256": r["relations_sha256"]}
        )
    return table


def receipts(headers: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    """Validated membership-rank receipts, and the rejected ones with their reasons."""
    good, bad = [], []
    for path in sorted(W.rglob("receipt-d*.json")):
        r = json.loads(path.read_text())
        rel = str(path.relative_to(HERE))
        inp = str(r.get("input_sha256", ""))
        h = headers.get(inp)
        reasons = []
        if h is None:
            # The fiber of a receipt comes only from its input bytes: a canonical header or a witnessed legacy input.
            bad.append({"path": rel, "reason": "input sha256 matches no canonical or witnessed header"})
            continue
        if r.get("prime") not in (None, h["prime"]):
            reasons.append(f"receipt prime {r.get('prime')} against header prime {h['prime']}")
        if r.get("status") != "degree-certified":
            reasons.append(f"status {r.get('status')}")
        if (r.get("membership_check") or {}).get("failures", 1) != 0:
            reasons.append("membership failures or no membership check")
        if r.get("generator_count") not in (None, GENERATORS[h["fiber"]]):
            reasons.append(f"generator_count {r.get('generator_count')}")
        if "rank_h_d" not in r or "degree" not in r:
            reasons.append("no rank or degree")
        # The membership check certifies the relation bytes it read; legacy receipts name the file relative to the
        # repository root, and it sits beside the receipt.
        relations = path.parent / Path(str(r.get("relation_file", "relations-d2.rel"))).name
        if not relations.is_file() or sha(relations) != r.get("relation_sha256"):
            reasons.append("relation file differs from the bytes the receipt checked")
        if reasons:
            bad.append({"path": rel, "reason": "; ".join(reasons)})
            continue
        good.append(
            {
                "fiber": h["fiber"],
                "prime": h["prime"],
                "d": r["degree"],
                "rank": r["rank_h_d"],
                "input": h["path"],
                "path": rel,
                "sha256": sha(path),
            }
        )
    return good, bad


def engines(roots: list[Path]) -> dict[str, str]:
    found: dict[str, str] = {}
    for root in [HERE / "replay" / "engine", *roots]:
        for p in sorted(root.rglob("fiber_rank*.py")):
            found.setdefault(sha(p)[:16], p.name)
    return found


def scan(roots: list[Path], k2: dict, headers: dict[str, dict], eng: dict[str, str]) -> tuple[list[dict], list[dict]]:
    by_prefix = {k[:16]: v for k, v in headers.items()}
    bound: dict[tuple, dict] = {}
    unbound: dict[tuple, dict] = {}
    for root in roots:
        for dp, dn, fn in os.walk(root):
            # The data-review directory holds reviewers' deliberately mutated records and receipts.
            dn[:] = [x for x in dn if x != "data-review"]
            for f in sorted(fn):
                if not (f.endswith(".jsonl") or f.endswith(".json")):
                    continue
                p = Path(dp, f)
                for ln in p.read_text(errors="replace").splitlines():
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        continue
                    if not isinstance(r, dict) or not {"r_N", "d", "N"} <= r.keys():
                        continue
                    h = by_prefix.get(str(r.get("header_sha256_16")))
                    if h is None:
                        continue
                    count = k2.get((h["fiber"], h["prime"]), {}).get("h", {}).get(str(r["d"]))
                    if count is None or r["r_N"] != count:
                        continue
                    key = (r.get("engine_sha256_16"), r["header_sha256_16"], r["d"], r["N"], r.get("mode", "raw"))
                    entry = {
                        "fiber": h["fiber"],
                        "prime": h["prime"],
                        "header_input": h["path"],
                        "source": f"{root.name}/{p.relative_to(root)}",
                        "record": r,
                    }
                    reasons = []
                    if r.get("engine_sha256_16") not in eng:
                        reasons.append("engine bytes not found")
                    if r.get("prime") not in (None, h["prime"]):
                        reasons.append(f"prime {r.get('prime')} against header prime {h['prime']}")
                    if r.get("generators") not in (None, GENERATORS[h["fiber"]]):
                        reasons.append(f"generators {r.get('generators')}")
                    if reasons:
                        unbound.setdefault(key, {**entry, "reason": "; ".join(reasons)})
                    else:
                        bound.setdefault(key, {**entry, "engine_file": eng[r["engine_sha256_16"]]})

    def order(c: dict) -> tuple:
        r = c["record"]
        return (c["fiber"], c["prime"], r["d"], r["N"], str(r.get("engine_sha256_16")), r.get("mode", "raw"))

    return sorted(bound.values(), key=order), sorted(unbound.values(), key=order)


def upper_bound(fiber: str, prime: int, k: dict, recs: list[dict], spans: set[tuple[str, str]]) -> list | str:
    srcs = [x if isinstance(x, str) else x["path"] for x in k["sources"]]
    d2 = [
        r
        for r in recs
        if r["fiber"] == fiber and r["prime"] == prime and r["d"] == 2 and r["rank"] == k["h"]["2"]
        and all((r["path"], src) in spans for src in srcs)
    ]  # fmt: skip
    if d2:
        return [{"receipt": r["path"], "sha256": r["sha256"]} for r in d2]
    return "none verified"


def transport(fibers: list[dict], isos: list[dict]) -> list[dict]:
    """Certify on both sides of every ok sign isomorphism the degrees either side certifies on its own."""
    by = {(f["fiber"], f["prime"]): f for f in fibers}
    for w in isos:
        ends = [(w["from"], w["prime"]), (w["to"], w["prime"])]
        have = [by[e] for e in ends if e in by]
        if not have:
            continue
        for e in ends:
            if e not in by:
                src = have[0]
                by[e] = {"fiber": e[0], "prime": e[1], "k2_sources": [], "upper_bound_d_ge_2": "transported",
                         "degrees": [{"d": g["d"], "k2_count": g["k2_count"], "status": "open", "lower_bounds": []}
                                     for g in src["degrees"]]}  # fmt: skip
        a, b = by[ends[0]], by[ends[1]]
        counts = [{g["d"]: g["k2_count"] for g in x["degrees"]} for x in (a, b)]
        if counts[0] != counts[1]:
            raise SystemExit(f"sign isomorphism {ends}: K2 counts differ {counts}")
        own = [{g["d"] for g in x["degrees"] if g["status"] == "certified"} for x in (a, b)]
        for x, mine, theirs, other in ((a, own[0], own[1], b), (b, own[1], own[0], a)):
            for g in x["degrees"]:
                if g["d"] in theirs - mine:
                    g["status"] = "certified"
                    g["transported_from"] = {"fiber": other["fiber"], "witness": "witnesses.jsonl",
                                             "flip": w["flip"], "G_signs": w["G_signs"]}  # fmt: skip
    out = sorted(by.values(), key=lambda f: (f["fiber"], f["prime"]))
    for f in out:
        f["certified_degrees"] = [g["d"] for g in f["degrees"] if g["status"] == "certified"]
    return out


def claims(k2: dict, certs: list[dict], recs: list[dict], isos: list[dict], spans: set[tuple[str, str]]) -> dict:
    fibers = []
    for (fiber, prime), k in sorted(k2.items()):
        upper2 = upper_bound(fiber, prime, k, recs, spans)
        degrees = []
        for d_str, count in sorted(k["h"].items(), key=lambda x: int(x[0])):
            d = int(d_str)
            lower = [
                {"method": "membership rank", "rank": r["rank"], "path": r["path"], "sha256": r["sha256"]}
                for r in recs
                if r["fiber"] == fiber and r["prime"] == prime and r["d"] == d
            ]
            lower += [
                {
                    "method": "truncated rank",
                    "rank": c["record"]["r_N"],
                    "N": c["record"]["N"],
                    "mode": c["record"].get("mode", "raw"),
                    "engine": c["record"].get("engine_sha256_16"),
                    "header": c["record"]["header_sha256_16"],
                    "source": c["source"],
                }
                for c in certs
                if c["fiber"] == fiber and c["prime"] == prime and c["record"]["d"] == d
            ]
            meets = any(x["rank"] == count for x in lower)
            upper_ok = d == 1 or isinstance(upper2, list)
            status = "certified" if meets and upper_ok else "lower bound equals candidate count" if meets else "open"
            degrees.append({"d": d, "k2_count": count, "status": status, "lower_bounds": lower})
        fibers.append(
            {
                "fiber": fiber,
                "prime": prime,
                "k2_sources": k["sources"],
                "upper_bound_d_ge_2": upper2,
                "certified_degrees": [g["d"] for g in degrees if g["status"] == "certified"],
                "degrees": degrees,
            }
        )
    return {
        "schema": "a5-fiber-claims-v2",
        "statement": "h_d = HF(k[y]/K2, d) at the named prime for every degree marked certified (h_1 = #G at d = 1)",
        "boundary": "finite-field results at the named prime; a characteristic-zero statement needs a specialization "
        "argument; equality in finitely many degrees leaves F(I) = k[y]/K2 open",
        "fibers": transport(fibers, isos),
    }


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    roots = [Path(a).resolve() for a in args if a != "--check"]
    wit = [json.loads(ln) for ln in (HERE / "witnesses.jsonl").read_text().splitlines() if ln.strip()]
    witness_ok = {w["legacy"] for w in wit if w["kind"] == "header-pair" and w["ok"]}
    isos = [fresh(w, ("k2_to", "k2_from")) for w in wit if w["kind"] == "sign-isomorphism" and w["ok"]]
    spans = {
        (w["receipt"], w["k2_source"])
        for w in wit
        if w["kind"] == "k2-span" and w["ok"] and fresh(w, ("k2_source", "receipt_relations"))
    }
    headers = known_headers(witness_ok)
    k2 = k2_table()
    recs, rejected = receipts(headers)
    certs, unbound = scan(roots, k2, headers, engines(roots))

    def dump(rows: list[dict]) -> str:
        return "".join(json.dumps(c, sort_keys=True) + "\n" for c in rows)

    out = {
        HERE / "certificates.jsonl": dump(certs),
        HERE / "unbound.jsonl": dump(unbound + [{"receipt": b["path"], "reason": b["reason"]} for b in rejected]),
        HERE / "claims.json": json.dumps(claims(k2, certs, recs, isos, spans), indent=1, sort_keys=True) + "\n",
    }
    if check:
        bad = [p.name for p, t in out.items() if not p.exists() or p.read_text() != t]
        print("registry differs: " + ", ".join(bad) if bad else "registry matches")
        return 1 if bad else 0
    for p, t in out.items():
        p.write_text(t)
    print(
        f"{len(certs)} bound truncated-rank certificates, {len(unbound)} unbound, "
        f"{len(recs)} receipts, {len(rejected)} rejected receipts"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
