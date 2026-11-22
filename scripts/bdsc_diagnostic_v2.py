"""The six-seed-slot successor of the Belenos crossed diagnostic: layout, case record and power statement.

scripts/bdsc_diagnostic.py keeps its bytes (six retained manifests bind its sha256 and ci/gates.json replays its
readout), so this module runs a fork of its functions: every function of that module is copied into one shared
globals dict (`fork`) whose overrides replace the layout constants. The copies call each other, so a callee that
reads SLOTS sees six without a per-function override list; the original module stays unmodified.

The layout changes from the frozen design in one parameter. SLOTS grows from 4 to 6, so a job holds 6 groups x 6
states = 36 iterations of 40000 samples under an 80000-shot cap
(results/quandela/cases/bdsc_diagnostic_packed_qpu_belenos/CASE.md, shape A). Block 1's first job runs the outward
groups of slots 0 to 2 with the reverse groups of slots 3 to 5, its second job the complement, and block 2 swaps the
two assignments, so b2-j1 repeats exactly the groups of b1-j2 and job position never aliases a seed or template
across blocks. The draw holds DRAW_VALUES = 6 + 2 x 2 x 6 x 6 = 150 uint16 values: values 0 to 5 are the seed slots
and value 6 + i orders block-1 instance i within its job.

The case record differs from the frozen one in its counts, its schema name, the authorization wording (free ANU
draws need no approval; AGENTS.md, "Hardware services") and the power statement of the six-slot design. Each
rewritten text is superseded from the frozen wording, so a change to the frozen record that this module does not
mirror is refused.
"""

from __future__ import annotations

import math
import types
from typing import Any

import bdsc_diagnostic as frozen
from billing_rule_v2 import supersede

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


def detectable_ratio(df: int, power: float, scale: int = 1, alpha: float = frozen.ALPHA) -> float:
    """The seed SD, in units of one fraction's counting error, that a pooled dispersion test reads at `power`.

    A statistic of `df` degrees of freedom whose summands carry independent seed effects of SD s about equal counting
    errors e is distributed (1 + scale (s / e)^2) times a central chi-square, so the test at `alpha` rejects with
    probability sf(isf(alpha) / (1 + scale (s / e)^2)); the ratio s / e at which that equals `power` follows from
    the two chi-square quantiles.
    """
    from scipy.stats import chi2

    ratio = float(chi2.isf(alpha, df) / chi2.isf(power, df)) - 1.0
    return math.sqrt(ratio / scale)


def power_rows(slots: int) -> dict[str, Any]:
    """Degrees of freedom and detectable seed SD of the three seed tests of a design with `slots` seed slots."""
    blocks = len(frozen.BLOCKS)
    steps = slots - 1
    tests = {
        # blocks x templates x 4 superposition states, each pooling the slots' fractions about their mean.
        "seed_superposition": (blocks * TEMPLATE_COUNT * STATE_COUNT * steps, 1),
        # blocks x templates fits; a seed offset common to the 4 states averages their counting errors.
        "seed_common": (blocks * TEMPLATE_COUNT * steps, STATE_COUNT),
        # blocks x templates fits of (states - 1) x (slots - 1) interaction degrees of freedom.
        "seed_interaction": (blocks * TEMPLATE_COUNT * (STATE_COUNT - 1) * steps, 1),
    }
    rows: dict[str, Any] = {}
    for name, (df, scale) in tests.items():
        rows[name] = {
            "df": df,
            "detectable_seed_sd_over_se": {
                f"power_{power}": round(detectable_ratio(df, power, scale), 3) for power in POWERS
            },
        }
    return rows


def power_statement() -> dict[str, Any]:
    """The preregistered power of the six-slot design against the frozen four-slot design."""
    return {
        "model": "each seed test is a pooled chi-square of seed effects about their group mean; independent seed "
        "effects of SD s over equal counting errors e scale its null distribution by 1 + k (s / e)^2 (k = 4 for "
        "seed_common, whose seed offset is shared by the 4 superposition states and so averages their counting "
        "errors, and 1 otherwise), so the test at alpha reads resolved with probability "
        "sf(isf(alpha, df) / (1 + k (s / e)^2), df)",
        "premises": "reference standard errors under independent Bernoulli trials, equal across the pooled cells, "
        "seed effects independent across seeds and (for seed_superposition and seed_interaction) across states; the "
        "provider contract establishes none of these, so the numbers plan the design and do not certify a reading",
        "alpha": frozen.ALPHA,
        "unit": f"s / e, with e the counting error of one fraction (about {REFERENCE_SE_AT_HALF} at p = 1/2 and "
        f"{frozen.TRIALS} trials)",
        "seed_slots": SLOTS,
        "six_slots": power_rows(SLOTS),
        "frozen_four_slots": power_rows(frozen.SLOTS),
    }


def build() -> dict[str, Any]:
    """The globals of the six-slot fork of scripts/bdsc_diagnostic.py, with its case record."""
    scope = fork(
        frozen,
        KEEP,
        SLOTS=SLOTS,
        DRAW_VALUES=DRAW_VALUES,
        outward_slots=outward_slots,
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
