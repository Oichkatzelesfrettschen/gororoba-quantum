"""Replay the arc certificate of one or more targets and write every retained record into the target directory.

usage: run_target.py [--work DIR] TARGET...      (TARGET: e8nm-p32009 e8nm-p32029 e8np-p32009 e8np-p32029)
The steps run in order: input digests, minimal primes of sqrt(K2) with the Hilbert functions, the scroll identification
of V(P2), the identity J(Phi) = 0 and the rank of dPhi, the primality of J, the two certified symbolic families, their
numeric certificates, the mutation controls, the scans of monomial families, the survey of base points, the line
check, the comparison with the N- target at the same prime (N+ targets) and the collation. Scratch (the Singular
script and log of every scanned family) lands in DIR, default $TMPDIR/a5-arcs-work/TARGET. Singular runs from the
repository root with a timeout; the caller caps address space (replay.sh: ulimit -v 8388608).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import cross_check
import gen_family as g
import mutation_controls as mc
import phi_rank
import scan_families
import survey as sv
from arc_targets import (
    TARGETS,
    Target,
    check_generator_order,
    k2_hilbert_function,
    k2_ideal,
    load_primes,
    minus_partner,
)
from certify import COMPONENTS, certify
from collate import collate, parse_primes_log
from line_check import line_check
from singular_scripts import (
    compare_script,
    j_decomp_script,
    k2_primes_script,
    scroll_script,
    verify_phi_script,
)

# Projective dimension and degree that identify the two minimal primes of sqrt(K2) in the Singular log.
P1_SHAPE = (4, 11)
P2_SHAPE = (3, 4)
SINGULAR_STEP_TIMEOUT = 900


def log(msg: str, t0: float) -> None:
    print(f"[{time.monotonic() - t0:7.1f} s] {msg}", flush=True)


def singular_step(target: Target, name: str, script: str) -> str:
    """Write NAME.sing into the target directory, run it from the repository root and keep NAME.log."""
    path = target.directory / f"{name}.sing"
    path.write_text(script)
    text = g.run_singular(path, SINGULAR_STEP_TIMEOUT)
    (target.directory / f"{name}.log").write_text(text)
    return text


def prepare_primes(target: Target) -> dict[str, Any]:
    """Minimal primes of sqrt(K2): write P1.txt and P2.txt, identified by (projective dimension, degree)."""
    text = singular_step(target, "k2_primes", k2_primes_script(target))
    info = parse_primes_log(text)
    gens = {int(m.group(1)): m.group(2) for m in re.finditer(r"^PRIME_GENS (\d+) (.*)$", text, re.M)}
    by_shape = {(v["projective_dimension"], v["degree"]): i for i, v in info["primes_by_log_index"].items()}
    if len(gens) != 2 or P1_SHAPE not in by_shape or P2_SHAPE not in by_shape:
        raise RuntimeError(
            f"{target.name}: the primes of sqrt(K2) have shapes {sorted(by_shape)}, not {P1_SHAPE}, {P2_SHAPE}"
        )
    if not info["radical_equals_P1_cap_P2"]:
        raise RuntimeError(f"{target.name}: sqrt(K2) differs from P1 cap P2")
    (target.directory / "P1.txt").write_text(gens[by_shape[P1_SHAPE]] + "\n")
    (target.directory / "P2.txt").write_text(gens[by_shape[P2_SHAPE]] + "\n")
    info["linear_generators"] = {
        "P1": info["primes_by_log_index"][by_shape[P1_SHAPE]]["linear_generators"],
        "P2": info["primes_by_log_index"][by_shape[P2_SHAPE]]["linear_generators"],
    }
    return info


def run_target(target: Target, work_root: Path) -> None:
    t0 = time.monotonic()
    work = work_root / target.name
    work.mkdir(parents=True, exist_ok=True)
    target.directory.mkdir(exist_ok=True)
    d: dict[str, Any] = {}
    prov = check_generator_order(target)
    d["k2"] = k2_ideal(target)
    log(f"{target.name}: inputs verified; {prov}", t0)

    d["primes"] = prepare_primes(target)
    d["P1"], d["P2"], _ = load_primes(target)
    log(f"{target.name}: minimal primes {d['primes']['primes_by_log_index']}", t0)

    singular_step(target, "scroll_check", scroll_script(target, d["P2"]))
    d["verify_phi_log"] = singular_step(target, "verify_phi", verify_phi_script(target))
    d["phi_rank"] = {
        "point": dict(zip(phi_rank.POINT_NAMES, phi_rank.POINT, strict=True)),
        "rank": phi_rank.jacobian_rank(target),
    }
    (target.directory / "phi_rank.json").write_text(json.dumps(d["phi_rank"], indent=1) + "\n")
    d["j_decomp_log"] = singular_step(target, "j_decomp", j_decomp_script(target))
    log(f"{target.name}: slice verified", t0)

    fam_dir = target.directory / "families"
    fam_dir.mkdir(exist_ok=True)
    for comp, key in (("P2", "family_P2_log"), ("P1", "family_P1_log")):
        fam = COMPONENTS[comp][0]
        g.run(target, fam, work)
        for suffix in ("sing", "log"):
            shutil.copyfile(work / "fam" / f"fam_{fam.tag}.{suffix}", fam_dir / f"fam_{fam.tag}.{suffix}")
        d[key] = (fam_dir / f"fam_{fam.tag}.log").read_text()
        d[f"numeric_{comp}"] = certify(target, fam, comp, d[key], log_name=f"families/fam_{fam.tag}.log")
        (target.directory / f"numeric_{comp}.json").write_text(json.dumps(d[f"numeric_{comp}"], indent=1) + "\n")
    d["mutation"] = mc.mutation_controls(target)
    (target.directory / "mutation_controls.json").write_text(json.dumps(d["mutation"], indent=1) + "\n")
    log(f"{target.name}: certificates and controls", t0)

    scans = {kind: scan_families.scan(target.name, work, kind) for kind in ("k-rs", "k-pq", "near")}
    log(f"{target.name}: scans {[len(v) for v in scans.values()]}", t0)
    survey_rows = sv.survey(target)
    (target.directory / "survey.json").write_text(json.dumps(survey_rows) + "\n")
    (target.directory / "line_check.json").write_text(json.dumps(line_check(target), indent=1) + "\n")
    log(f"{target.name}: survey and line check", t0)

    minus = minus_partner(target)
    if minus is not None:
        pm = load_primes(minus)
        pp = load_primes(target)
        d["compare_nm_log"] = singular_step(target, "compare_nm", compare_script(target, minus, pp, pm))
        d["cross_control"] = cross_check.cross_control(target, minus)
        (target.directory / "cross_control.json").write_text(cross_check.dump(d["cross_control"]))
        log(f"{target.name}: comparison with {minus.name}", t0)

    collate(target, scans, survey_rows, d)
    log(f"{target.name}: done", t0)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--work", type=Path, default=Path(os.environ.get("ARCS_WORK", Path(tempfile.gettempdir()) / "a5-arcs-work"))
    )
    ap.add_argument("targets", nargs="+", choices=sorted(TARGETS))
    args = ap.parse_args(argv[1:])
    for name in args.targets:
        k2_hilbert_function(TARGETS[name])
        run_target(TARGETS[name], args.work)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
