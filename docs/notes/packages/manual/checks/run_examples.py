"""Replay every EXAMPLES block of the package manual pages against the installed packages.

A runnable example in docs/notes/packages/manual/*.md is a line `<!-- example -->`, then a fenced
python or sh block, then a fenced text block holding its exact output. The python block runs as
`$PYTHON -c CODE` from the repository root with PYTHONPATH=gororoba_quantum, the sh block as
`sh -c CODE` from the same directory; both run with warnings ignored, and stdout and stderr are
compared merged. Absolute site-packages and checkout paths read as `site-packages/` and `./`.

--check (local, needs the host package stack) fails on any difference; --write replaces each text
block with the output of the run. CI has no package stack, so this replay runs on the build host.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import sysconfig
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANUAL = HERE.parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

BLOCK = re.compile(
    r"<!-- example -->\n```(?P<lang>python|sh)\n(?P<code>.*?)```\n\n?```text\n(?P<out>.*?)```",
    re.DOTALL,
)


def scrub(text: str) -> str:
    """Replace host-specific absolute paths with stable relative names."""
    purelib = sysconfig.get_paths()["purelib"].rstrip("/") + "/"
    text = text.replace(purelib, "site-packages/")
    text = text.replace(str(ROOT) + "/", "./")
    return re.sub(r" at 0x[0-9a-f]+", " at 0x...", text)


def run(lang: str, code: str) -> str:
    env = dict(os.environ, PYTHONPATH="gororoba_quantum", PYTHONWARNINGS="ignore", PYTHONDONTWRITEBYTECODE="1")
    python = os.environ.get("PYTHON", "python3")
    argv = [python, "-c", code] if lang == "python" else ["sh", "-c", code]
    completed = subprocess.run(
        argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False
    )
    output = scrub(completed.stdout)
    return output if not output or output.endswith("\n") else output + "\n"


def run_example(example: tuple[str, str]) -> str:
    """run() on one (lang, code) pair, a picklable callable for parallel.ordered_map."""
    return run(*example)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail when any example output differs")
    mode.add_argument("--write", action="store_true", help="rewrite each output block from a fresh run")
    parser.add_argument("pages", nargs="*", help="manual pages to replay (default: all)")
    args = parser.parse_args()
    pages = [Path(p).resolve() for p in args.pages] or sorted(MANUAL.glob("*.md"))
    jobs = []
    texts = {}
    for page in pages:
        texts[page] = page.read_text()
        for match in BLOCK.finditer(texts[page]):
            jobs.append((page, match))
    # Each example is an independent subprocess; the pool returns the outputs in jobs order.
    outputs = ordered_map(run_example, [(match["lang"], match["code"]) for _, match in jobs], min_items=2)
    failures = 0
    for page in pages:
        pieces, last = [], 0
        for (owner, match), output in zip(jobs, outputs, strict=True):
            if owner != page:
                continue
            if output != match["out"]:
                failures += 1
                if args.check:
                    print(f"{page.name}: example at offset {match.start()} differs")
                    print(f"--- retained\n{match['out']}--- ran\n{output}")
            pieces.append(texts[page][last : match.start("out")])
            pieces.append(output)
            last = match.end("out")
        pieces.append(texts[page][last:])
        if args.write:
            page.write_text("".join(pieces))
    print(f"package manual examples: {len(jobs)} run, {failures} differ")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    sys.exit(main())
