"""Render the E8-bar modular Rees fiber scripts of the open cells of ledger row A5-576.

Each script is a retained v2 E8-bar script of ../e8-rees-fibers-v2-p32009 with the zero-generator guard of
../e8-rees-fibers-v3-p32009 (check_rees_fibers_v3.successor_script, the four EDITS) applied, the prime of its four ring
declarations and the root of -1 of its two `number i` lines replaced, its basis file names renamed to the cell, and its
SOURCE line set to the sha256 of the retained v2 script it derives from. Run from docs/evidence/a5-exceptional-fibers:

    python -B working/runs/e8-rees-fibers-v3-open-cells/render_cells.py [--write | --check]

`--write` writes the six scripts beside this file; `--check` (the default) renders them again and compares bytes.
"""

import hashlib
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
V2_DIR = HERE.parent / "e8-rees-fibers-v2-p32009"
V3_DIR = HERE.parent / "e8-rees-fibers-v3-p32009"
PRIME, ROOT = 32009, 10754
# (prime, root of -1) of the open cells; 21255 = 32009 - 10754 and 22914 = 32029 - 9115.
CELLS = [(32009, 21255), (32029, 9115), (32029, 22914)]
SIGNS = {"nm": "e8-nm-p.v2-u-full", "np": "e8-np-p.v2-u-full"}
SOURCE = re.compile(r'"SOURCE sha256 [0-9a-f]{64}"')


def _load_v3() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_rees_fibers_v3", V3_DIR / "check_rees_fibers_v3.py")
    if spec is None or spec.loader is None:
        raise ImportError("check_rees_fibers_v3.py does not load")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(V3_DIR))
    spec.loader.exec_module(module)
    return module


def _replace(text: str, old: str, new: str, count: int) -> str:
    if text.count(old) != count:
        raise ValueError(f"{old!r} occurs {text.count(old)} times, expected {count}")
    return text.replace(old, new)


def cell_name(sign: str, prime: int, root: int) -> str:
    return f"e8-{sign}-p{prime}-r{root}.v3-u-full"


def render(v2_text: str, v2_stem: str, name: str, prime: int, root: int, guard: bool = True) -> str:
    """The cell script; guard=False keeps the v2 loop, which the calibration against an unrun v2 variant uses."""
    text = _load_v3().successor_script(v2_text) if guard else v2_text
    text = _replace(text, f"={PRIME},", f"={prime},", 4)
    text = _replace(text, f"number i={ROOT};", f"number i={root};", 2)
    text = _replace(text, f"{v2_stem}.hs.ssi", f"{name}.hs.ssi", 1)
    text = _replace(text, f"{v2_stem}.sat.ssi", f"{name}.sat.ssi", 1)
    if len(SOURCE.findall(text)) != 1:
        raise ValueError("the script holds no single SOURCE line")
    digest = hashlib.sha256(v2_text.encode()).hexdigest()
    return SOURCE.sub(f'"SOURCE sha256 {digest}"', text)


def scripts() -> dict[str, str]:
    out: dict[str, str] = {}
    for sign, stem in SIGNS.items():
        v2_text = (V2_DIR / f"{stem}.sing").read_text()
        for prime, root in CELLS:
            if (root * root + 1) % prime != 0:
                raise ValueError(f"{root} is no root of -1 modulo {prime}")
            name = cell_name(sign, prime, root)
            out[name] = render(v2_text, stem, name, prime, root)
    return out


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "--check"
    bad = 0
    for name, text in scripts().items():
        path = HERE / f"{name}.sing"
        if mode == "--write":
            path.write_text(text)
        elif not path.exists() or path.read_text() != text:
            print(f"differs: {path.name}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
