"""The Singular replay of the polar-line stack minors stays bound to the matrices of the polar-line module."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"
sys.path.insert(0, str(HERE))

import nullity4_polar_line_module as module  # noqa: E402
import nullity4_quartic_discriminant as disc  # noqa: E402
import sympy as sp  # noqa: E402

SCRIPT = HERE / "nullity4_polar_line_stack.sing"
# The lines the replay prints: the rows of the stack span the free module of rank 8 over the ring modulo the cone and
# 1 - w mu for both signs, and not without the slack, because the stack has rank 6 on mu = 0.
EXPECTED = [
    "stack sigma=1 unit_off_mu_zero=1 unit_without_saturation=0",
    "stack sigma=-1 unit_off_mu_zero=1 unit_without_saturation=0",
    "MARKER DONE nullity4_polar_line_stack",
]
NAMES = {module.S_VAR: sp.Symbol("s"), module.V1: sp.Symbol("v1"), module.MU: sp.Symbol("mu")}


def _stack(vector: list[sp.Expr]) -> sp.Matrix:
    b = module._b(vector)
    return b.col_join(b * module._restrict(module.derivations()[0]))


def _entries(matrix: sp.Matrix) -> str:
    return ", ".join(str(sp.expand(entry.subs(NAMES))).replace("**", "^") for entry in matrix)


def stack_script(vectors: dict[int, list[sp.Expr]] = module.VECTORS) -> str:
    """The Singular text for the 14 x 8 stack S of B(p_sigma(x)) and B(p_sigma(x)) D_1, sigma = 1 and -1.

    S has rank 8 at every point exactly when its rows span the free module of rank 8 over every residue field, which
    over the ring of x modulo the cone, localized at mu, is the statement that a standard basis of the row module
    reduces every generator of the free module to 0; that is the vanishing of the zeroth Fitting obstruction, the
    unit ideal of the 8 x 8 minors, reached without forming them. Without the localization at mu the row module is
    proper, because S has rank 6 on mu = 0.
    """
    lines = [
        "// Row modules of the stack of B and B D_1 of nullity4_polar_line_module.py over the ring of x = (s, v1, mu)",
        "// modulo the cone, with or without the slack 1 - w mu; tests/test_a5_nullity4_polar_line_stack.py writes it",
        "option(redSB);",
    ]
    for name, sigma in (("p", 1), ("m", -1)):
        entries = _entries(_stack(vectors[sigma]))
        for kind, relations in (("u", "s^2 + v1^2 + mu^2, 1 - w * mu"), ("c", "s^2 + v1^2 + mu^2")):
            lines += [
                f"ring r{name}{kind} = 0, (w, mu, v1, s), dp;",
                f"qring q{name}{kind} = std(ideal({relations}));",
                f"matrix S{name}{kind}[14][8] = {entries};",
                f"module G{name}{kind} = std(module(transpose(S{name}{kind})));",
                f"int f{name}{kind} = size(reduce(freemodule(8), G{name}{kind})) == 0;",
            ]
        lines.append(
            f'print("stack sigma={sigma} unit_off_mu_zero=" + string(f{name}u)'
            f' + " unit_without_saturation=" + string(f{name}c));'
        )
    lines += ['print("MARKER DONE nullity4_polar_line_stack");', "quit;", ""]
    return "\n".join(lines)


def test_stack_script_matches_the_module() -> None:
    if SCRIPT.read_text() != stack_script():
        raise AssertionError("nullity4_polar_line_stack.sing differs from the stack of the polar-line module")


def test_stack_script_changes_with_a_flipped_sign() -> None:
    flipped = {sigma: list(vector) for sigma, vector in module.VECTORS.items()}
    flipped[1][2] = -flipped[1][2]
    if stack_script(flipped) == SCRIPT.read_text():
        raise AssertionError("a flipped sign of p_1 leaves the replayed stack unchanged")


def replay(singular: str) -> list[str]:
    """The non-empty output lines of the script under a checked Singular run (exit 0, empty stderr, marker)."""
    lines = disc.run_checked(singular, SCRIPT, None, 600)
    return [line.strip() for line in lines if line.strip()]


def test_a_failed_singular_process_with_the_expected_output_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "Singular"
    path.write_text(
        "#!/bin/sh\n" + "".join(f"echo '{line}'\n" for line in EXPECTED) + "echo 'fatal: planted' >&2\nexit 7\n"
    )
    path.chmod(0o755)
    with pytest.raises(RuntimeError):
        replay(str(path))


@pytest.mark.audit
def test_singular_replay_gives_the_unit_ideals() -> None:
    if os.environ.get("SINGULAR") is None and shutil.which("Singular") is None:
        if os.environ.get("GOROROBA_SINGULAR_REQUIRED") == "1":
            raise AssertionError("GOROROBA_SINGULAR_REQUIRED=1 and Singular 4.4 is absent")
        pytest.skip("Singular 4.4 is absent; set SINGULAR to its path")
    lines = replay(disc._singular())
    if lines != EXPECTED:
        raise AssertionError(lines)
