"""Long-format table of the measured pathion (A_5, 32-dimensional Cayley-Dickson) readings on every platform.

One row is one reading: a value that a retained record carries (an IBM collect group, a Quantum Inspire series
analysis, a Quandela analysis), the ideal the analysis compares it with, and the standard error the record's own
estimator produces. The module computes no estimator of its own, with two exceptions that reproduce an existing
estimator on records that store the inputs, not the output:

- IBM per-output contrasts c(y) and ratios c(y) / V: ``pathion_coset_block.output_contrast`` and
  ``pathion_kernel_map.output_contrast`` applied to each replica's measured law, V the signed mean of c against the
  ideal sign, the standard error the standard deviation over replicas divided by the square root of their count (the
  arithmetic of ``qi_pathion_coset_block_cases.ibm_reference``, whose result a test compares);
- the standard error of an IBM summary value, the same replica statistic over ``summary_per_replica`` (the interval of
  ``variance.interval`` is a Student t half-width over the identical per-replica values).

Every reader takes decoded records and plain labels (paths, run names, the ledger text), so no job identifier lives
in a function. Values from ``measured_summary_readout_corrected`` carry no per-replica data and keep an empty
standard error. A value that is not a finite number is written with an empty measured field and status ``undefined``.

Columns (``COLUMNS``): ``run_dir`` the record's directory or analysis file; ``source_file`` the file the value was
read from; ``platform``, ``backend``, ``substrate`` (qpu or sim) and ``dimension`` (32 throughout); ``operand`` the
algebra element e_i + t e_j (or the four-term sum); ``control`` the reading's role (primary, null, twin, cocycle-free,
mutation, readout-flip, repeat, skeleton, anchor, reference); ``block`` the coset block (``k<coset>`` of an IBM or
Tuna block, ``<class>/<coset>`` of a four-term block); ``block_class`` the nullity class of a two-term block or the
census class of a four-term block; ``label`` the algebra output index and ``bin`` the output bin y; ``setting`` the
segment or setting name of a Quandela reading; ``arm`` the record's own arm (``+``, ``-``, ``+-`` for the contrast of
the two orientations, or a four-term arm T, D, D2, F, E0, E1, C, N); ``observable``; ``ideal``; ``measured``;
``standard_error``; ``n_replicas``; ``readout_corrected`` (true when the value passed a calibration normalization);
``calibration`` (raw, readout_corrected, anchor_dark_normalized, branch_odds_corrected, per_slot_anchor_dark);
``shots``; ``reference_backend`` (the device a D(y) row compares against); ``status``; ``ledger_row`` (every row of the
claim ledger whose evidence column cites the run).
"""

from __future__ import annotations

import csv
import importlib
import io
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import pathion_coset_block as pcb
import pathion_kernel_map as pkm

COLUMNS: tuple[str, ...] = (
    "run_dir",
    "source_file",
    "platform",
    "backend",
    "substrate",
    "dimension",
    "operand",
    "control",
    "block",
    "block_class",
    "label",
    "bin",
    "setting",
    "arm",
    "observable",
    "ideal",
    "measured",
    "standard_error",
    "n_replicas",
    "readout_corrected",
    "calibration",
    "shots",
    "reference_backend",
    "status",
    "ledger_row",
)
FLOAT_COLUMNS = ("ideal", "measured", "standard_error")
INT_COLUMNS = ("dimension", "label", "bin", "n_replicas", "shots")
DIMENSION = 32
Row = dict[str, Any]

# Factory of the experiments.Group that summarizes each IBM collect group, keyed by the record's `group` field.
IBM_GROUPS: dict[str, tuple[str, str]] = {
    "pathion_kernel_map": ("pathion_kernel_map", "pathion_kernel_map_group"),
    "pathion_coset_map": ("pathion_coset_block", "pathion_coset_map_group"),
    "pathion_parallel_coset": ("pathion_parallel_coset", "pathion_parallel_coset_group"),
}
BACKEND_NAMES = {"tuna_17": "tuna-17", "QXsinglenodesimulator": "qx-emulator"}
ARM_CONTROL = {
    "T": "primary",
    "D": "primary",
    "D2": "primary",
    "F": "primary",
    "E0": "null",
    "E1": "null",
    "C": "cocycle-free",
    "N": "mutation",
}
# Observables whose sign is part of the claim, so the sign agreement of a pivot is meaningful for them.
SIGNED_OBSERVABLES = frozenset(
    {"N_hat", "selector_contrast", "output_contrast", "output_ratio", "half_sum", "contrast_ratio", "visibility"}
)

_OPERAND = r"e\d+(?:pe|me)\d+"
_CMAP = re.compile(rf"^cmap_(?P<kind>twin_|xor_)?(?P<op>{_OPERAND})(?:_k(?P<k>\d+))?_(?P<stat>[a-z0-9_]+)$")
_KMAP = re.compile(rf"^kmap_(?:(?P<kind>twin_|xor_)|flip(?P<flip>\d+)_)?(?P<op>{_OPERAND})_(?P<stat>[a-z0-9_]+)$")
_FTB = re.compile(r"^ftb_(?P<cls>[A-Z]\d+)_c(?P<c>\d+)_(?P<stat>[A-Za-z0-9_]+)$")
_STANDALONE = re.compile(
    r"^(?:twin_nullity_difference(?:_e\d+me\d+)?|twin_difference_e\d+me\d+|nullity_ratio_\d+_over_\d+"
    r"|strut\d+_ratio_e\d+e\d+_over_e\d+e\d+|skeleton_p0)$"
)
# Summary statistics that stand for an observable; the rest of the families are named in _stat_observable.
_STAT_OBSERVABLE = {
    "nullity_estimate": "N_hat",
    "visibility": "visibility",
    "visibility_mean": "visibility",
    "half_sum": "half_sum",
    "half_sum_output_contrast": "half_sum",
    "selector_contrast": "selector_contrast",
    "contrast": "selector_contrast",
    "sign_agreement": "sign_count",
    "contrast_ratio": "contrast_ratio",
    "mean_abs_output_contrast": "mean_abs_output_contrast",
}
_FLIP_STATS = {
    "flip_selector_contrast": "selector_contrast",
    "flip_visibility": "visibility",
    "flip_half_sum": "half_sum",
    "flip_nullity_estimate": "N_hat",
}
_REPEAT_STATS = frozenset(
    {
        "repeat_nullity_estimate",
        "repeat_half_sum",
        "quad_half_sum",
        "quad_nullity_estimate",
        "pair_half_sum_gap",
        "within_minus_half_sum",
        "within_plus_half_sum",
    }
)
_ODD_EVEN_STATS = frozenset({"odd_half_sum", "even_half_sum", "odd_nullity", "even_nullity"})
_IDEAL_ONLY = re.compile(r"(?:_nullity_ideal|_contrast_ideal|_level_ideal_[A-Z0-9]+)$")


@dataclass(frozen=True)
class Parsed:
    """A decoded summary key: the observable it reports and the labels that place it in the table."""

    observable: str
    operand: str
    control: str
    block: str
    arm: str
    prefix: str


def operand_name(token: str) -> str:
    """e1pe18 is e1+e18 and e17me2 is e17-e2."""
    return token.replace("pe", "+e").replace("me", "-e")


def operand_tuple(token: str) -> tuple[int, int, int]:
    found = re.fullmatch(r"e(\d+)([pm])e(\d+)", token)
    if found is None:
        raise ValueError(f"unreadable operand token {token!r}")
    return int(found[1]), int(found[3]), 1 if found[2] == "p" else -1


def terms_text(terms: Mapping[str, int]) -> str:
    """The operand of a Quandela case: {"1": 1, "25": -1} reads e1-e25."""
    out = ""
    for index, coefficient in sorted((int(i), c) for i, c in terms.items()):
        if abs(coefficient) != 1:
            raise ValueError(f"term e{index} has coefficient {coefficient}, not +-1")
        out += ("+" if coefficient > 0 else "-") + f"e{index}"
    return out[1:] if out.startswith("+") else out


def backend_name(raw: str) -> str:
    return BACKEND_NAMES.get(raw, raw)


def finite(value: Any) -> float | None:
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def make_row(**fields: Any) -> Row:
    """One table row; every column not named is empty, and an unknown column is an error."""
    unknown = set(fields) - set(COLUMNS)
    if unknown:
        raise ValueError(f"unknown columns {sorted(unknown)}")
    row: Row = {column: None for column in COLUMNS}
    row["readout_corrected"] = False
    row["status"] = "ok"
    row["dimension"] = DIMENSION
    row.update(fields)
    for column, value in row.items():
        if value == "":
            row[column] = None
    if row["measured"] is not None and finite(row["measured"]) is None:
        row["measured"] = None
    if row["measured"] is None:
        row["status"] = "undefined"
    for column in FLOAT_COLUMNS:
        value = finite(row[column])
        row[column] = value
    if row["ideal"] is None and row["status"] == "ok":
        raise ValueError(f"{row['run_dir']}: {row['observable']} has no ideal")
    return row


def ledger_cites(ledger: Iterable[Mapping[str, str]], run_dir: str) -> str:
    """Ids of the ledger rows whose evidence column names the run directory or analysis file."""
    return ";".join(
        sorted(
            row["id"]
            for row in ledger
            if any(part == run_dir or part.startswith(run_dir + "/") for part in row["evidence"].split(";"))
        )
    )


def parse_ledger(text: str) -> list[dict[str, str]]:
    return [dict(row) for row in csv.DictReader(io.StringIO(text), delimiter="\t")]


# ---------------------------------------------------------------- IBM


def find_group(collect: Any) -> dict[str, Any]:
    """The one group entry of a collect record (the list also holds the submission summary)."""
    items = collect if isinstance(collect, list) else [collect]
    groups = [item for item in items if isinstance(item, dict) and "group" in item]
    if len(groups) != 1:
        raise ValueError(f"expected one group entry, found {len(groups)}")
    return groups[0]


def ideal_inputs(group_name: str) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    """The ideal summary and the ideal laws of one IBM group, from the same Group.summarize the run used."""
    if group_name not in IBM_GROUPS:
        raise ValueError(f"no ideal for group {group_name!r}")
    module, factory = IBM_GROUPS[group_name]
    group = getattr(importlib.import_module(module), factory)()
    laws = {member.name: np.asarray(member.ideal, dtype=float) for member in group.members}
    return group.summarize(laws), laws


def parse_key(key: str, operand_nullity: Mapping[str, float], four_term_operands: Mapping[str, str]) -> Parsed | None:
    """Decode one IBM summary key; None for an ideal-only key, an error for an unknown family."""
    if _IDEAL_ONLY.search(key):
        return None
    found = _FTB.match(key)
    if found is not None:
        stat = found["stat"]
        block = f"{found['cls']}/{found['c']}"
        operand = four_term_operands[found["cls"]]
        prefix = f"ftb_{found['cls']}_c{found['c']}"
        if stat == "visibility":
            return Parsed("visibility", operand, "primary", block, "T-D", prefix)
        split = re.fullmatch(r"(level|closure|separation|bin_tvd)_([A-Z0-9]+)", stat)
        if split is None:
            raise ValueError(f"unparsed four-term statistic {key!r}")
        arm = split[2]
        return Parsed(split[1], operand, ARM_CONTROL[arm], block, arm, prefix)
    if _STANDALONE.match(key):
        return Parsed(key, "", "primary", "", "+-", key)
    for pattern, family in ((_CMAP, "cmap"), (_KMAP, "kmap")):
        found = pattern.match(key)
        if found is None:
            continue
        token = found["op"]
        kind = found["kind"]
        control = {"twin_": "twin", "xor_": "cocycle-free"}.get(kind or "", "primary")
        if family == "kmap" and found["flip"] is not None:
            control = "mutation"
        block = f"k{found['k']}" if family == "cmap" and found["k"] is not None else ""
        operand = operand_name(token)
        stat = found["stat"]
        prefix_operand = f"{family}_{kind or ''}" + (
            f"flip{found['flip']}_" if family == "kmap" and found["flip"] else ""
        )
        prefix = f"{prefix_operand}{token}" + (f"_k{found['k']}" if block else "")
        if control == "primary" and operand_nullity.get(f"{family}_{token}") == 0.0:
            control = "null"
        arm = "+-"
        if stat in _STAT_OBSERVABLE:
            observable = _STAT_OBSERVABLE[stat]
        elif stat in _FLIP_STATS:
            observable, control = _FLIP_STATS[stat], "readout-flip"
        elif stat in _ODD_EVEN_STATS:
            observable, control = stat, "readout-flip"
        elif stat in _REPEAT_STATS:
            observable, control = stat, "repeat"
        elif stat in ("p0_minus", "p0_plus"):
            observable, arm = "p_selector0", "-" if stat.endswith("minus") else "+"
        elif stat == "nullity_ideal":
            return None
        else:
            raise ValueError(f"unparsed statistic {stat!r} of {key!r}")
        return Parsed(observable, operand, control, block, arm, prefix)
    raise ValueError(f"unparsed summary key {key!r}")


def operand_nullities(ideal: Mapping[str, float]) -> dict[str, float]:
    """Ideal nullity of each primary operand, keyed ``cmap_<token>`` or ``kmap_<token>``."""
    out: dict[str, float] = {}
    for key, value in ideal.items():
        found = re.fullmatch(rf"(cmap|kmap)_({_OPERAND})_nullity_ideal", key)
        if found is not None:
            out[f"{found[1]}_{found[2]}"] = float(value)
    return out


def shots_of(executed: Mapping[str, Any], prefix: str) -> int | None:
    """Shots per arm and replica of the first executed member of the block."""
    for name in sorted(executed):
        if name.startswith(prefix + "_") and isinstance(executed[name], dict) and "shots" in executed[name]:
            return int(executed[name]["shots"])
    return None


def block_class_of(prefix: str, ideal: Mapping[str, float], classes: Mapping[tuple[str, int], str]) -> str:
    """Census class of a four-term block, or the nullity class (ideal aligned XOR pairs) of a two-term block."""
    found = re.fullmatch(r"ftb_([A-Z]\d+)_c(\d+)", prefix)
    if found is not None:
        return classes.get((found[1], int(found[2])), "")
    key = f"{prefix}_nullity_ideal"
    return f"nullity-{round(ideal[key])}" if key in ideal else ""


def replica_se(values: Sequence[float]) -> tuple[float | None, int]:
    count = len(values)
    if count < 2 or not all(math.isfinite(v) for v in values):
        return None, count
    return float(np.std(values, ddof=1)) / math.sqrt(count), count


def ibm_summary_rows(
    group: Mapping[str, Any],
    ideal: Mapping[str, float],
    *,
    run_dir: str,
    source_file: str,
    four_term_operands: Mapping[str, str],
    block_classes: Mapping[tuple[str, int], str],
    ledger: Sequence[Mapping[str, str]] = (),
) -> list[Row]:
    """Every summary value of one IBM group, raw with its replica standard error and readout-corrected without."""
    statistics = group["measured_statistics"]
    summary = statistics["summary"]
    per_replica = statistics["summary_per_replica"]
    corrected = group["measured_summary_readout_corrected"]
    if set(summary) != set(ideal) or set(corrected) != set(ideal):
        raise ValueError(f"{run_dir}: the record's summary keys differ from the group's ideal summary")
    for key, value in ideal.items():
        if _IDEAL_ONLY.search(key):
            recorded = float(summary[key])
            if not (math.isnan(recorded) and math.isnan(float(value))) and abs(recorded - float(value)) > 1e-9:
                raise ValueError(f"{run_dir}: {key} is {recorded} in the record and {value} from the code")
    nullity = operand_nullities(ideal)
    cited = ledger_cites(ledger, run_dir)
    backend = str(group["backend"])
    rows: list[Row] = []
    for key in sorted(summary):
        parsed = parse_key(key, nullity, four_term_operands)
        if parsed is None:
            continue
        se, count = replica_se([float(r[key]) for r in per_replica])
        common = {
            "run_dir": run_dir,
            "source_file": source_file,
            "platform": "ibm",
            "backend": backend,
            "substrate": "qpu",
            "operand": parsed.operand,
            "control": parsed.control,
            "block": parsed.block,
            "block_class": block_class_of(parsed.prefix, ideal, block_classes) if parsed.block else "",
            "arm": parsed.arm,
            "observable": parsed.observable,
            "ideal": float(ideal[key]),
            "shots": shots_of(group["executed"], parsed.prefix),
            "ledger_row": cited,
        }
        rows.append(
            make_row(
                **common,
                measured=float(summary[key]),
                standard_error=se,
                n_replicas=count,
                calibration="raw",
            )
        )
        rows.append(
            make_row(
                **common,
                measured=float(corrected[key]),
                readout_corrected=True,
                n_replicas=count,
                calibration="readout_corrected",
            )
        )
    return rows


def _pair_prefixes(measured: Mapping[str, Any]) -> list[str]:
    out = []
    for name in sorted(measured):
        if not name.endswith("_plus") or not name.startswith(("cmap_", "kmap_")):
            continue
        prefix = name[: -len("_plus")]
        if f"{prefix}_minus" in measured:
            out.append(prefix)
    return out


def _block_labels(prefix: str) -> tuple[str, str, str, list[int]]:
    """(operand, control, block, algebra output labels) of one measured block or kernel-map circuit."""
    cmap = re.fullmatch(rf"cmap_(?P<kind>twin_|xor_)?(?P<op>{_OPERAND})_k(?P<k>\d+)", prefix)
    if cmap is not None:
        operand = operand_tuple(cmap["op"])
        basis = pcb.default_basis(operand)
        k0 = int(cmap["k"])
        labels = pcb.output_labels(pcb.Block(f"k{k0}", operand, basis, k0))
        control = {"twin_": "twin", "xor_": "cocycle-free"}.get(cmap["kind"] or "", "primary")
        return operand_name(cmap["op"]), control, f"k{k0}", labels
    kmap = re.fullmatch(rf"kmap_(?:(?P<kind>twin_|xor_)|flip(?P<flip>\d+)_)?(?P<op>{_OPERAND})", prefix)
    if kmap is None:
        raise ValueError(f"unparsed measured circuit {prefix!r}")
    control = {"twin_": "twin", "xor_": "cocycle-free"}.get(kmap["kind"] or "", "primary")
    if kmap["flip"] is not None:
        control = "mutation"
    return operand_name(kmap["op"]), control, "", list(range(pkm.DIM))


def ibm_bin_rows(
    group: Mapping[str, Any],
    ideal_laws: Mapping[str, np.ndarray],
    ideal: Mapping[str, float],
    *,
    run_dir: str,
    source_file: str,
    ledger: Sequence[Mapping[str, str]] = (),
) -> list[Row]:
    """Per-output contrast c(y) and ratio c(y) / V of every measured block or kernel-map circuit, over replicas."""
    measured = group["measured"]
    nullity = operand_nullities(ideal)
    cited = ledger_cites(ledger, run_dir)
    backend = str(group["backend"])
    rows: list[Row] = []
    for prefix in _pair_prefixes(measured):
        operand, control, block, labels = _block_labels(prefix)
        contrast = pcb.output_contrast if prefix.startswith("cmap_") else pkm.output_contrast
        plus, minus = np.asarray(measured[f"{prefix}_plus"]), np.asarray(measured[f"{prefix}_minus"])
        c = np.array([contrast(p, m) for p, m in zip(plus, minus, strict=True)])
        c_ideal = contrast(ideal_laws[f"{prefix}_plus"], ideal_laws[f"{prefix}_minus"])
        sign = np.sign(c_ideal)
        decided = np.abs(c_ideal) > pkm.ZERO
        visibility = (c[:, decided] * sign[decided]).mean(axis=1)
        count = len(c)
        if control == "primary" and nullity.get(f"{prefix.split('_k')[0]}") == 0.0:
            control = "null"
        key = f"{prefix}_nullity_ideal"
        klass = f"nullity-{round(ideal[key])}" if key in ideal else ""
        shots = shots_of(group["executed"], prefix)
        for y, label in enumerate(labels):
            column = c[:, y]
            if np.all(np.abs(visibility) > pkm.ZERO):
                ratio_values = column / visibility
                ratio = float(ratio_values.mean())
                ratio_se = float(ratio_values.std(ddof=1)) / math.sqrt(count) if count >= 2 else None
            else:
                ratio, ratio_se = float("nan"), None
            common = {
                "run_dir": run_dir,
                "source_file": source_file,
                "platform": "ibm",
                "backend": backend,
                "substrate": "qpu",
                "operand": operand,
                "control": control,
                "block": block,
                "block_class": klass if block else "",
                "label": label,
                "bin": y,
                "arm": "+-",
                "n_replicas": count,
                "calibration": "raw",
                "shots": shots,
                "ledger_row": cited,
            }
            rows.append(
                make_row(
                    **common,
                    observable="output_contrast",
                    ideal=float(c_ideal[y]),
                    measured=float(column.mean()),
                    standard_error=float(column.std(ddof=1)) / math.sqrt(count) if count >= 2 else None,
                )
            )
            rows.append(
                make_row(
                    **common,
                    observable="output_ratio",
                    ideal=float(sign[y]),
                    measured=ratio,
                    standard_error=ratio_se,
                )
            )
    return rows


# ---------------------------------------------------------------- Quantum Inspire


def tuna_rows(
    analysis: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    run_dir: str,
    source_file: str,
    ledger: Sequence[Mapping[str, str]] = (),
    stopped_run_dir: str | None = None,
) -> list[Row]:
    """Template readings of a coset-block or coin-arm series analysis, with the stored D(y) rows.

    `manifest` is any batch's cases.json of the series: its templates carry the ideal per-bin contrast and
    selector contrast the analysis scored against, and its labels table maps each bin to its algebra output index.
    `stopped_run_dir`, when given, names the first (stopped) series, whose pinned null selector contrast the coin
    analysis carries as `decisions.null.stopped_series_reference`."""
    backend = backend_name(str(analysis["backend"]))
    substrate = "sim" if backend == "qx-emulator" else "qpu"
    cited = ledger_cites(ledger, run_dir)
    shots = manifest.get("shots")
    rows: list[Row] = []
    labels_table = manifest["labels"]
    for name, template in analysis["templates"].items():
        spec = manifest["templates"][name]
        operand = operand_name_from_tuple(spec["operand"])
        ideal_c = [float(x) for x in spec["ideal_c"]]
        nullity_ideal = float(sum(ideal_c) / 2.0)
        control = "cocycle-free" if spec["cocycle_free"] else "null" if abs(nullity_ideal) < 0.5 else "primary"
        klass = f"nullity-{round(nullity_ideal)}"
        labels = labels_table[spec["block"]]["ibm_data_index_of_bin"]
        common = {
            "run_dir": run_dir,
            "source_file": source_file,
            "platform": "quantum_inspire",
            "backend": backend,
            "substrate": substrate,
            "operand": operand,
            "control": control,
            "block": name,
            "block_class": klass,
            "arm": "+-",
            "shots": int(shots) if shots is not None else None,
            "ledger_row": cited,
        }
        rows.append(
            make_row(
                **common,
                observable="selector_contrast",
                ideal=float(spec["ideal_selector_contrast"]),
                measured=template["selector_contrast"],
                standard_error=template["selector_se"],
                calibration="raw",
            )
        )
        for statistic, corrected in (("raw", False), ("readout_corrected", True)):
            stats = template["statistics"].get(statistic)
            if stats is None:
                continue
            tag = {"calibration": statistic, "readout_corrected": corrected}
            rows.append(
                make_row(
                    **common,
                    **tag,
                    observable="visibility",
                    ideal=1.0,
                    measured=stats["visibility"],
                    standard_error=stats.get("visibility_se"),
                )
            )
            if "nullity_estimate" in stats and "nullity_ideal" in template:
                rows.append(
                    make_row(
                        **common,
                        **tag,
                        observable="N_hat",
                        ideal=float(template["nullity_ideal"]),
                        measured=stats["nullity_estimate"],
                        standard_error=stats.get("nullity_se"),
                    )
                )
            for y in range(len(ideal_c)):
                bin_fields = {**common, **tag, "label": int(labels[y]), "bin": y}
                rows.append(
                    make_row(
                        **bin_fields,
                        observable="output_contrast",
                        ideal=ideal_c[y],
                        measured=stats["c"][y],
                        standard_error=stats["c_se"][y],
                    )
                )
                rows.append(
                    make_row(
                        **bin_fields,
                        observable="output_ratio",
                        ideal=float(np.sign(ideal_c[y])),
                        measured=stats["ratio"][y],
                        standard_error=stats["ratio_se"][y],
                    )
                )
    cross = analysis["decisions"]["cross_platform"].get("devices", {})
    for device, entry in sorted(cross.items()):
        for name, template in sorted(entry.get("templates", {}).items()):
            spec = manifest["templates"][name]
            for statistic in ("raw", "readout_corrected"):
                block = template.get(statistic)
                if not isinstance(block, dict) or "difference" not in block:
                    continue
                for y, label in enumerate(block["labels"]):
                    rows.append(
                        make_row(
                            run_dir=run_dir,
                            source_file=source_file,
                            platform="quantum_inspire",
                            backend=backend,
                            substrate=substrate,
                            operand=operand_name_from_tuple(spec["operand"]),
                            control="cocycle-free" if spec["cocycle_free"] else "primary",
                            block=name,
                            block_class=f"nullity-{round(sum(spec['ideal_c']) / 2.0)}",
                            label=int(label),
                            bin=y,
                            arm="+-",
                            observable="D_y",
                            ideal=0.0,
                            measured=block["difference"][y],
                            standard_error=block["se"][y],
                            readout_corrected=statistic == "readout_corrected",
                            calibration=statistic,
                            reference_backend=device,
                            ledger_row=cited,
                        )
                    )
    reference = analysis["decisions"]["null"].get("stopped_series_reference")
    if reference is not None and stopped_run_dir is not None:
        spec = manifest["templates"]["b0"]
        rows.append(
            make_row(
                run_dir=stopped_run_dir,
                source_file=source_file,
                platform="quantum_inspire",
                backend=backend,
                substrate=substrate,
                operand=operand_name_from_tuple(spec["operand"]),
                control="null",
                block="b0",
                block_class="nullity-0",
                arm="+-",
                observable="selector_contrast",
                ideal=float(spec["ideal_selector_contrast"]),
                measured=reference["selector_contrast"],
                standard_error=reference["se"],
                calibration="raw",
                ledger_row=ledger_cites(ledger, stopped_run_dir),
            )
        )
    return rows


def operand_name_from_tuple(operand: Sequence[int]) -> str:
    i, j, t = operand
    return f"e{i}{'+' if t > 0 else '-'}e{j}"


# ---------------------------------------------------------------- Quandela


def class_table(analysis: Mapping[str, Any]) -> dict[tuple[str, int], str]:
    """Census class of each pathion block the four-term analysis names: (operand class, coset) -> census-<id>."""
    out: dict[tuple[str, int], str] = {}
    for entry in analysis.get("classes", []):
        for operand, coset in entry["blocks"]:
            out[(str(operand), int(coset))] = f"census-{entry['class_id']}"
    return out


def ascella_rows(
    analysis: Mapping[str, Any],
    operands: Mapping[str, Mapping[str, int]],
    *,
    run_dir: str,
    source_file: str,
    classes: Mapping[tuple[str, int], str],
    ledger: Sequence[Mapping[str, str]] = (),
) -> list[Row]:
    """Level and mirror-difference rows of an Ascella pathion analysis (four-term blocks or coset-block pairs)."""
    schema = str(analysis["schema"])
    if schema not in (
        "ascella-pathion-four-term-blocks-analysis-v1",
        "ascella-pathion-coset-block-pairs-analysis-v1",
    ):
        raise ValueError(f"{run_dir}: unknown schema {schema!r}")
    four_term = "four-term" in schema
    backend = str(analysis["backend"])
    substrate = "sim" if backend.startswith("sim:") else "qpu"
    cited = ledger_cites(ledger, run_dir)
    texts = {name: terms_text(terms) for name, terms in operands.items()}
    rows: list[Row] = []
    for reading in analysis["readings"]:
        if four_term:
            name, coset = str(reading["operand"]), int(reading["block"])
            setting = str(reading["segment"])
            role = str(reading["role"])
            shots = int(reading["success"]) + int(reading["failure"])
        else:
            name, coset = str(reading["block"]).split("/")[0], int(str(reading["block"]).split("/")[1])
            setting = str(reading["setting"])
            role = str(reading["role"])
            shots = None
        arm = str(reading["arm"])
        control = "null" if arm in ("E0", "E1") else ARM_CONTROL[arm]
        if role in ("anchor", "reference"):
            control = role
        klass = classes.get((name, coset), "")
        if role == "anchor":
            klass = f"census-{_anchor_class(analysis)}" if _anchor_class(analysis) else klass
        common = {
            "run_dir": run_dir,
            "source_file": source_file,
            "platform": "quandela",
            "backend": backend,
            "substrate": substrate,
            "operand": texts[name],
            "control": control,
            "block": f"{name}/{coset}",
            "block_class": klass,
            "setting": setting,
            "arm": arm,
            "observable": "level",
            "ideal": float(reading["ideal"]),
            "shots": shots,
            "ledger_row": cited,
        }
        rows.append(make_row(**common, measured=reading["a"], calibration="raw"))
        rows.append(
            make_row(
                **common,
                measured=reading["a_prime"],
                readout_corrected=True,
                calibration="anchor_dark_normalized",
            )
        )
        if four_term:
            rows.append(
                make_row(
                    **common,
                    measured=reading["a_prime_odds_corrected"],
                    readout_corrected=True,
                    calibration="branch_odds_corrected",
                )
            )
        else:
            rows.append(
                make_row(
                    **common,
                    measured=reading["l_hat"],
                    standard_error=reading["se"],
                    readout_corrected=True,
                    calibration="per_slot_anchor_dark",
                )
            )
            if reading.get("mirror_difference") is not None:
                rows.append(
                    make_row(
                        **{**common, "observable": "mirror_difference", "ideal": 0.0},
                        measured=reading["mirror_difference"],
                        readout_corrected=True,
                        calibration="per_slot_anchor_dark",
                    )
                )
    return rows


def _anchor_class(analysis: Mapping[str, Any]) -> int | None:
    for entry in analysis.get("classes", []):
        if not entry["blocks"]:
            return int(entry["class_id"])
    return None


# ---------------------------------------------------------------- table I/O


def sort_key(row: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple("" if row[c] is None else str(row[c]) for c in COLUMNS)


def render_csv(rows: Iterable[Mapping[str, Any]]) -> str:
    """The table as LF-terminated CSV text, rows sorted by every column, floats in repr form."""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in sorted(rows, key=sort_key):
        writer.writerow([format_cell(c, row[c]) for c in COLUMNS])
    return buffer.getvalue()


def format_cell(column: str, value: Any) -> str:
    if value is None:
        return ""
    if column == "readout_corrected":
        return "true" if value else "false"
    if column in FLOAT_COLUMNS:
        return repr(float(value))
    return str(value)


def parse_table(text: str) -> list[Row]:
    """Typed rows from the CSV text: floats, integers, booleans and None for an empty cell."""
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise ValueError("the table header differs from COLUMNS")
    rows: list[Row] = []
    for raw in reader:
        row: Row = {}
        for column in COLUMNS:
            cell = raw[column]
            if column == "readout_corrected":
                row[column] = cell == "true"
            elif cell == "":
                row[column] = None
            elif column in FLOAT_COLUMNS:
                row[column] = float(cell)
            elif column in INT_COLUMNS:
                row[column] = int(cell)
            else:
                row[column] = cell
        rows.append(row)
    return rows


def write_table(rows: Iterable[Mapping[str, Any]], path: Path) -> None:
    path.write_text(render_csv(rows), encoding="utf-8", newline="")
