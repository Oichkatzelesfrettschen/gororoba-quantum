"""The six-seed-slot successor of the Belenos crossed diagnostic: layout, case record and power statement.

scripts/bdsc_diagnostic.py keeps its bytes (six retained manifests bind its sha256 and ci/gates.json replays its
readout), so this module runs a fork of its functions: every function of that module is copied into one shared
globals dict (`fork`) whose overrides replace the layout constants. The copies call each other, so a callee that
reads SLOTS sees six without a per-function override list; the original module stays unmodified. Two functions carry
four-slot literals and are replaced: draw_values (its refusal text) and self_test (four-element seed vectors), which
refuses in favor of the synthetic six-slot runs of tests/scripts/test_bdsc_diagnostic_v2.py.

The layout changes from the frozen design in one parameter. SLOTS grows from 4 to 6, so a job holds 6 groups x 6
states = 36 iterations of 40000 samples under an 80000-shot cap
(results/quandela/cases/bdsc_diagnostic_packed_qpu_belenos/CASE.md, shape A). Block 1's first job runs the outward
groups of slots 0 to 2 with the reverse groups of slots 3 to 5, its second job the complement, and block 2 swaps the
two assignments, so b2-j1 repeats exactly the groups of b1-j2 and job position never aliases a seed or template
across blocks. The draw holds DRAW_VALUES = 6 + 2 x 2 x 6 x 6 = 150 uint16 values: values 0 to 5 are the seed slots
and value 6 + i orders block-1 instance i within its job; block-2 instances reuse their block-1 match's value, so
values 78 to 149 are drawn and unused, the frozen formula's count (CASE.md shape A).

The case record differs from the frozen one in its counts, its schema name, the authorization wording (free ANU
draws need no approval; AGENTS.md, "Hardware services") and the power statement of the six-slot design. Each
rewritten text is superseded from the frozen wording, so a change to the frozen record that this module does not
mirror is refused.
"""

from __future__ import annotations

import functools
import json
import types
from pathlib import Path
from typing import Any

import bdsc_diagnostic as frozen
from billing_rule_v2 import supersede

from parallel import ordered_map

SLOTS = 6
LABEL_COUNT = len(frozen.LABELS)
TEMPLATE_COUNT = 2
DRAW_VALUES = SLOTS + 2 * TEMPLATE_COUNT * SLOTS * LABEL_COUNT
# Functions that cross a process boundary by reference: a copy would not pickle to the module's own object.
KEEP = frozenset({"_params"})
# One fraction's counting error at p = 1/2 and n = 40000, the unit of the power statement.
REFERENCE_SE_AT_HALF = 0.0025
POWERS = (0.8, 0.95)
STATE_COUNT = len(frozen.SUPERPOSITIONS)
BLOCK_COUNT = len(frozen.BLOCKS)


def fork(module: types.ModuleType, keep: frozenset[str] = frozenset(), **overrides: Any) -> dict[str, Any]:
    """The globals of a copy of `module` whose functions share one dict, with `overrides` replacing module names.

    Every plain function that the module defines becomes a copy that reads its globals from the returned dict, and a
    name in `overrides` or `keep` stays as given. A copy that calls another function of the module reaches the
    copy, so an override of a constant or of a function reaches every caller (gororoba_quantum/rebound.py
    overrides the names of one function only).
    """
    scope: dict[str, Any] = {**vars(module), **overrides}
    for name, value in vars(module).items():
        if name in overrides or name in keep or not isinstance(value, types.FunctionType):
            continue
        if value.__module__ != module.__name__:
            continue
        clone = types.FunctionType(value.__code__, scope, name, value.__defaults__, value.__closure__)
        clone.__kwdefaults__ = value.__kwdefaults__
        clone.__doc__ = value.__doc__
        clone.__annotations__ = dict(value.__annotations__)
        scope[name] = clone
    return scope


def outward_slots(block: int) -> tuple[int, ...]:
    """Seed slots whose outward-ladder groups run in a block's first job; its reverse groups take the others."""
    return (0, 1, 2) if block == 1 else (3, 4, 5)


def rejection(ratio: float, df: int, scale: int = 1, alpha: float = frozen.ALPHA, blocks: int = BLOCK_COUNT) -> float:
    """Probability that a pooled dispersion test of `df` degrees of freedom rejects under a seed SD of `ratio` errors.

    Block 2 repeats block 1's returned circuits (scripts/bdsc_diagnostic.py, compilation_determinism), so one seed's
    effect is common to a summand's copies in every block. Rotating the `blocks` copies of each summand into their
    mean and `blocks - 1` contrasts splits the statistic into df / blocks summands that carry `blocks` times the seed
    variance and the remaining summands that carry none: under seed SD s over counting error e it is
    (1 + blocks scale (s / e)^2) X + Y, with X and Y independent central chi-squares of those degrees of freedom. The
    test rejects above isf(alpha, df) of the null chi-square.
    """
    from scipy.integrate import quad
    from scipy.stats import chi2

    if blocks < 2 or df % blocks:
        raise ValueError(f"df {df} does not split over {blocks} repeated blocks")
    common = df // blocks
    contrast = df - common
    critical = float(chi2.isf(alpha, df))
    weight = 1.0 + blocks * scale * ratio**2
    inside, _ = quad(
        lambda y: float(chi2.pdf(y, contrast) * chi2.sf((critical - y) / weight, common)),
        0.0,
        critical,
        epsabs=1e-13,
        epsrel=1e-11,
        limit=400,
    )
    return inside + float(chi2.sf(critical, contrast))


@functools.cache
def detectable_ratio(df: int, power: float, scale: int = 1, alpha: float = frozen.ALPHA) -> float:
    """The seed SD, in units of one fraction's counting error, at which `rejection` equals `power`."""
    from scipy.optimize import brentq

    return float(brentq(lambda ratio: rejection(ratio, df, scale, alpha) - power, 0.0, 20.0, xtol=1e-12))


def power_cell(cell: tuple[int, float, int]) -> float:
    """detectable_ratio of one (df, power, scale) cell, the unit ordered_map dispatches."""
    return detectable_ratio(*cell)


def power_rows(slots: int) -> dict[str, Any]:
    """Degrees of freedom and detectable seed SD of the three seed tests of a design with `slots` seed slots."""
    blocks = BLOCK_COUNT
    steps = slots - 1
    tests = {
        # blocks x templates x 4 superposition states, each pooling the slots' fractions about their mean.
        "seed_superposition": (blocks * TEMPLATE_COUNT * STATE_COUNT * steps, 1),
        # blocks x templates fits; a seed offset common to the 4 states averages their counting errors.
        "seed_common": (blocks * TEMPLATE_COUNT * steps, STATE_COUNT),
        # blocks x templates fits of (states - 1) x (slots - 1) interaction degrees of freedom.
        "seed_interaction": (blocks * TEMPLATE_COUNT * (STATE_COUNT - 1) * steps, 1),
    }
    cells = [(df, power, scale) for df, scale in tests.values() for power in POWERS]
    ratios = iter(ordered_map(power_cell, cells))
    rows: dict[str, Any] = {}
    for name, (df, _scale) in tests.items():
        rows[name] = {
            "df": df,
            "detectable_seed_sd_over_se": {f"power_{power}": round(next(ratios), 3) for power in POWERS},
        }
    return rows


def power_statement() -> dict[str, Any]:
    """The preregistered power of the six-slot design against the frozen four-slot design."""
    return {
        "model": "each seed test is a pooled chi-square of seed effects about their group mean over both blocks; "
        "block 2 repeats block 1's returned circuits, so a seed's effect is common to its copies in the two blocks, "
        "and under seed SD s over counting error e the statistic is (1 + 2 k (s / e)^2) X + Y with X and Y "
        "independent central chi-squares of df / 2 degrees of freedom (k = 4 for seed_common, whose seed offset is "
        "shared by the 4 superposition states and so averages their counting errors, and 1 otherwise); the test at "
        "alpha rejects above isf(alpha, df) of the null chi-square",
        "premises": "reference standard errors under independent Bernoulli trials, equal across the pooled cells, a "
        "seed's effect identical in both blocks and independent across seeds and (for seed_superposition and "
        "seed_interaction) across states; a seed effect that changes between blocks lowers the detectable ratio "
        "toward the independent-block value; the provider contract establishes none of these, so the numbers plan the "
        "design and do not certify a reading",
        "alpha": frozen.ALPHA,
        "unit": f"s / e, with e the counting error of one fraction (about {REFERENCE_SE_AT_HALF} at p = 1/2 and "
        f"{frozen.TRIALS} trials)",
        "seed_slots": SLOTS,
        "six_slots": power_rows(SLOTS),
        "frozen_four_slots": power_rows(frozen.SLOTS),
    }


def draw_values(path: Path | None) -> tuple[list[int], list[int]] | None:
    """(seeds of the SLOTS slots, order keys of the block-1 instances and beyond) from a keyed ANU record, or None."""
    if path is None:
        return None
    import anu_qrng

    record = json.loads(path.read_text(encoding="utf-8"))
    anu_qrng.admit(record)
    frozen.require(
        str(record.get("source", "")).startswith(anu_qrng.ENDPOINTS["aqn"]), f"{path}: not the keyed AQN service"
    )
    frozen.require(record["type"] == "uint16", f"{path}: type {record['type']!r}, the case draws uint16")
    values = list(record["values"])
    frozen.require(len(values) >= DRAW_VALUES, f"{path}: {len(values)} values, need {DRAW_VALUES}")
    seeds: list[int] = []
    for value in values[:SLOTS]:
        frozen.require(value not in seeds, f"{path}: seed values repeat; the case needs {SLOTS} distinct seeds")
        seeds.append(value)
    return seeds, values[SLOTS:DRAW_VALUES]


def self_test() -> int:
    """Refuses: the frozen self-test builds four-slot runs; the module's pytest file reads six-slot ones."""
    raise SystemExit(
        "the six-slot fork carries no --self-test: the frozen one builds four-slot seed vectors; "
        "tests/scripts/test_bdsc_diagnostic_v2.py reads synthetic six-slot runs into their branches"
    )


def build() -> dict[str, Any]:
    """The globals of the six-slot fork of scripts/bdsc_diagnostic.py, with its case record."""
    scope = fork(
        frozen,
        KEEP,
        SLOTS=SLOTS,
        DRAW_VALUES=DRAW_VALUES,
        outward_slots=outward_slots,
        draw_values=draw_values,
        self_test=self_test,
    )
    layout_record = scope["case_record"]

    def case_record() -> dict[str, Any]:
        """The frozen case record at six seed slots, with the counts and wording that follow from them."""
        record: dict[str, Any] = layout_record()
        old = frozen.case_record()
        supersede(record, ("schema",), "bdsc-diagnostic-case-v1", "bdsc-diagnostic-case-v2")
        supersede(
            record,
            ("authorization",),
            old["authorization"],
            "none: the case waits for the owner's approval of its written case for the provider jobs; the free ANU "
            "QRNG draw needs none",
        )
        supersede(
            record,
            ("design", "role"),
            old["design"]["role"],
            "diagnostic, not a confirmation design: six seeds do not determine the tails of a seed distribution, "
            "and the result decides whether further compilation replication is warranted",
        )
        supersede(
            record,
            ("qrng", "use"),
            old["qrng"]["use"],
            f"the first {SLOTS} values, which must be distinct, seed slots 0 to {SLOTS - 1}; value {SLOTS} + i orders "
            "block-1 instance i within its job, and a block-2 instance takes the order value of its block-1 match so "
            "matched pairs share a position",
        )
        residuals = len(frozen.BLOCKS) * TEMPLATE_COUNT * SLOTS * 2
        wording = {
            "seed_dispersion": [("of the four seeds", f"of the {SLOTS} seeds")],
            "seed_split": [
                ("(3 df each)", f"({SLOTS - 1} df each)"),
                ("(9 df each)", f"({(STATE_COUNT - 1) * (SLOTS - 1)} df each)"),
            ],
            "residual_margin": [("all 32 residuals", f"all {residuals} residuals")],
        }
        for key, replacements in wording.items():
            text = old["analysis"][key]
            new = text
            for before, after in replacements:
                if new.count(before) != 1:
                    raise ValueError(f"analysis/{key}: the frozen wording lacks {before!r} exactly once")
                new = new.replace(before, after)
            supersede(record, ("analysis", key), text, new)
        record["analysis"]["power"] = power_statement()
        return record

    scope["case_record"] = case_record
    return scope


SCOPE = build()
diag = types.SimpleNamespace(**SCOPE)
