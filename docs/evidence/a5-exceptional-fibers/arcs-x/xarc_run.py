"""Replay the arc certificate of the opposite-sign X fibers (X+ -> N- and X- -> N+) at one prime.

usage: xarc_run.py --prime P [--root I] [--header-dir DIR]
The headers `xp-nm.sing` and `xm-np.sing` come from DIR (default: the one directory `pP-r*` of
working/build/inputs/ that holds both). The prime and the root of -1 are read from their first two lines; --prime and
--root must agree with them. The steps run in order: generate the Singular scripts into sing/pP/, run each script into
logs/pP/ (a nonzero exit, a timeout or a `?` error line of Singular raises), compare the two incidences by sign changes,
and replay the exact series certificate of each incidence into records/pP/SLUG/. The caller caps address space
(replay.sh: ulimit -v 8388608). The scripts run from this directory.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import subprocess
import sys
from pathlib import Path

import xarc_certify
import xarc_flip
import xarc_gen
from xarc_common import HERE, INCIDENCES, load_headers, prime_dir

sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))
import parallel  # noqa: E402

SINGULAR_TIMEOUT = 900


def singular_errors(output: str) -> list[str]:
    """The error lines of a Singular transcript: Singular reports a failed statement on lines that start with `?` and
    still exits with status 0."""
    return [line.strip() for line in output.splitlines() if line.lstrip().startswith("?")]


def run_singular(script: Path, cwd: Path, timeout: int = SINGULAR_TIMEOUT) -> str:
    """Run a Singular script with stdin closed and return its output; a timeout, a nonzero exit status or an error
    line in the output raises."""
    singular = shutil.which("Singular")
    if singular is None:
        raise RuntimeError("Singular is not on PATH")
    try:
        done = subprocess.run(
            [singular, "-q", str(script)],
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{script.name}: Singular exceeded {timeout} s") from exc
    if done.returncode != 0:
        raise RuntimeError(f"{script.name}: Singular exited with status {done.returncode}: {done.stderr[-400:]}")
    output = done.stdout + done.stderr
    errors = singular_errors(output)
    if errors:
        raise RuntimeError(f"{script.name}: Singular reported {len(errors)} errors, the first: {errors[0]}")
    return output


class SingularStep:
    """Callable for one script name: run sing/pP/NAME from this directory and write logs/pP/NAME.log."""

    def __init__(self, prime: int, timeout: int = SINGULAR_TIMEOUT) -> None:
        self.prime = prime
        self.timeout = timeout

    def __call__(self, name: str) -> str:
        script = prime_dir("sing", self.prime) / name
        output = run_singular(script.relative_to(HERE), HERE, self.timeout)
        log = prime_dir("logs", self.prime) / (script.stem + ".log")
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(output)
        return log.name


def run(prime: int, root: int | None, header_dir: Path | None) -> None:
    headers = load_headers(prime, root, header_dir)
    logs = prime_dir("logs", prime)
    logs.mkdir(parents=True, exist_ok=True)
    names = xarc_gen.write_scripts(headers)
    parallel.ordered_map(SingularStep(prime), names, min_items=2)

    flip_log = io.StringIO()
    with contextlib.redirect_stdout(flip_log):
        xarc_flip.main(prime)
    (logs / "flip_check.log").write_text(flip_log.getvalue())

    for slug in INCIDENCES:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            xarc_certify.main(prime, slug)
        (logs / f"certify_{slug}.log").write_text(out.getvalue())
        print(out.getvalue(), end="")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prime", type=int, required=True)
    ap.add_argument("--root", type=int, default=None)
    ap.add_argument("--header-dir", type=Path, default=None)
    args = ap.parse_args(argv[1:])
    run(args.prime, args.root, args.header_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
