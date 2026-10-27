"""Post-hoc analyses of the retained case-3 records (no QPU): a pooled band offset and q147's shot history.

Both were chosen after the stage-2 results were read, so both are descriptive and outside the preregistration.

Pooled offset. For each of the seven null-subtracted coefficients, the residual of path k is
r_k = (o_k - c_k) / s_k, with o the stage-2 bias of stage2-falsification.json and c, s the decision's
shift_center and shift_spread (stage1-decision.json). The common offset is the inverse-variance mean
delta = sum (o - c) / s^2 / sum 1 / s^2, standard error 1 / sqrt(sum 1 / s^2); the excitation envelope is a
systematic allowance and stays out of s. Coefficient 01 was picked because its deviations were seen to lean
positive, so each delta is judged at a Bonferroni level over the seven coefficients. The four band misses read
as one shared offset only when each lies inside its unchanged band after its coefficient's delta is subtracted.
The fit runs over all 22 paths, without 147-148-149, and with that path's center moved to its measured lambda
(terminal + lambda (split - terminal)).
Prediction: delta_01 > 0 at the Bonferroni level, and all four misses return inside. Falsifier: delta_01
consistent with zero, or a miss on another coefficient that no delta moves inside.

Shot history. IBM executes a job column-wise, every circuit of shot s in order before shot s + 1
(docs/notes/ibm_quantum/repetition-rate-execution.md), so a circuit's previous shot is the circuit executed before
it at the same shot index, and the first circuit's is the last one at shot s - 1. The same note gives no
guarantee on PUB order, so the analysis reads the order from the data:
- x_history: one circuit (init, measure, x), so its predecessor is its own previous shot, which ends excited
  exactly when that shot's initial readout was 0. A carried population predicts P(read 1 | previous read 1)
  near prep0's fraction and P(read 1 | previous read 0) near hd + prep0.
- stage 2: the readout arms that prepare q147 in |0> (labels 0, 2, 4, 6) split by q147's read in another PUB at
  the same shot. Under submitted order, the predecessor (lag -1) carries an excess near hd (1 - e01 - e10) and
  the successor (lag +1) none, since a later circuit cannot act on an earlier one.
- lambda reading: each circuit has exactly one predecessor, so the mean predecessor excited fraction equals the
  mean of q147's end-excited fraction over all PUBs, whatever their order. Read against x_history's
  end-excited fraction it gives f, which the reading predicts equal to lambda 0.66 +- 0.25. lambda's 2-sigma
  range is about 0.16 to 1.16, so only f near 0 or above about 1.2 would contradict the reading.

Three items were added after the first pass read the output, and are labeled so in the record: the scatter
chi-square showed the spreads understate the path-to-path scatter, so each delta also carries a standard error
scaled by sqrt(chi-square / dof) and its significance is judged on that scaled error, against Student's t with
dof degrees of freedom when the scale is estimated (chi-square above dof); the x_history test also
conditions at lags 1 to 5 and on the previous two shots; the stage-2 readout-arm test reports each arm alone,
because a pooled split mixes predecessors with different base rates, and every |0> arm's predecessor leaves
q147 excited in about 0.8 of its shots, so the arms cannot separate the predecessor's role. A second review
added three more: the band recheck subtracts a leave-one-out delta fitted on the other paths, so a miss does not
pull its own offset; the same fit runs on case 2 (same circuits, estimators, paths and delay), on its retained
centers without the four high-excitation paths whose centers its ablation found mis-built and on all 21 paths
recentered under the split law (case2_offsets), so a fixed model offset (same sign in both runs) separates
from a shift of one run; and g88_readout_0, which prepares every path in |000> as the prep0
control does, gives q147's in-job preparation excess against the ceiling of any law that scales the excess
with q147's own end-state history, hd / (1 - x_history fraction). hd assumes the calibrated |1> read efficiency
1 - e01 in the x_history jobs, so the ceiling is also given at the in-job efficiency of the stage-2 |1> arms
(their read-1 fraction over 1 minus the |0> arms' read-1 fraction, the start-excited shots that X sends to |0>).
"""

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

from qiskit import qpy
from scipy import stats

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import primorial_probe_case as ppc  # noqa: E402
import state_prep_excess as spe  # noqa: E402
import state_prep_split as sps  # noqa: E402

import parallel  # noqa: E402

E = ROOT / "docs/evidence/primorial_cover/case3"
STAGE2 = ROOT / "results/live/2026-10-27T013626.332783Z"
X_HISTORY = [ROOT / "results/live/2026-10-27T010917.104805Z", ROOT / "results/live/2026-10-27T011025.944327Z"]
KEYS = ("0", "1", "2", "01", "02", "12", "012")
QUBIT = 147
POSITIVE_PATH = [147, 148, 149]
ZERO_LABELS = (0, 2, 4, 6)
CASE2 = ROOT / "docs/evidence/primorial_cover/case2"
CASE2_EXCLUDED = ([58, 71, 72], [15, 19, 35], [100, 101, 102], [132, 133, 134])
CASE2_CONTROLS = [ROOT / "results/live/2026-10-26T190449.023973Z", ROOT / "results/live/2026-10-26T190506.325237Z"]


def normal_two_sided(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def sign_test(positive: int, total: int) -> float:
    tail = sum(math.comb(total, k) for k in range(max(positive, total - positive), total + 1)) / 2.0**total
    return min(1.0, 2.0 * tail)


def pooled(rows: list[tuple[float, float, float]]) -> dict[str, float]:
    """rows of (observed, center, spread) -> the inverse-variance offset, its z, and the scatter about it."""
    weight = sum(1.0 / s**2 for _, _, s in rows)
    delta = sum((o - c) / s**2 for o, c, s in rows) / weight
    se = 1.0 / math.sqrt(weight)
    chi = sum(((o - c - delta) / s) ** 2 for o, c, s in rows)
    positive = sum(1 for o, c, _ in rows if o > c)
    dof = len(rows) - 1
    scaled = se * math.sqrt(max(1.0, chi / dof))
    t = delta / scaled
    p_scaled = float(2.0 * stats.t.sf(abs(t), dof)) if chi > dof else normal_two_sided(t)
    return {
        "delta": delta,
        "se": se,
        "z": delta / se,
        "p_two_sided": normal_two_sided(delta / se),
        "se_scatter_scaled": scaled,
        "z_scatter_scaled": delta / scaled,
        "p_two_sided_scatter_scaled": p_scaled,
        "positive": positive,
        "paths": len(rows),
        "sign_test_p": sign_test(positive, len(rows)),
        "scatter_chi_square": chi,
        "scatter_dof": len(rows) - 1,
    }


def offset_test(falsification: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    decided = {tuple(v["layout"]): v for v in decision["decisions"]}
    lam = {tuple(r["path"]): r["discrimination"]["lambda"] for r in falsification["paths"] if "discrimination" in r}
    alpha = 0.05 / len(KEYS)
    out: dict[str, Any] = {"bonferroni_alpha": alpha, "coefficients": {}}
    deltas: dict[str, float] = {}
    for key in KEYS:
        variants: dict[str, list[tuple[float, float, float]]] = {"all": [], "without_147": [], "147_at_lambda": []}
        for row in falsification["paths"]:
            path = tuple(row["path"])
            fal = decided[path]["falsifier"]
            o, c, s = row["observed_bias"][key], fal["shift_center"][key], fal["shift_spread"][key]
            variants["all"].append((o, c, s))
            if list(path) == POSITIVE_PATH:
                t = decided[path]["terminal_center"][key]
                variants["147_at_lambda"].append((o, t + lam[path] * (c - t), s))
            else:
                variants["without_147"].append((o, c, s))
                variants["147_at_lambda"].append((o, c, s))
        fits = {name: pooled(rows) for name, rows in variants.items()}
        for fit in fits.values():
            fit["significant"] = fit["p_two_sided_scatter_scaled"] < alpha
        out["coefficients"][key] = fits
        deltas[key] = fits["all"]["delta"]
    misses = []
    inside_after = 0
    for row in falsification["paths"]:
        others = [r for r in falsification["paths"] if r["path"] != row["path"]]
        for key, (low, high) in row["bands"].items():
            rest = []
            for other in others:
                fal = decided[tuple(other["path"])]["falsifier"]
                rest.append((other["observed_bias"][key], fal["shift_center"][key], fal["shift_spread"][key]))
            loo = pooled(rest)
            shifted = row["observed_bias"][key] - loo["delta"]
            inside = low <= shifted <= high
            inside_after += inside
            if key in row["outside"] or not inside:
                half = (high - low) / 2.0
                center = (high + low) / 2.0
                misses.append(
                    {
                        "path": row["path"],
                        "coefficient": key,
                        "preregistered_outside": key in row["outside"],
                        "half_widths_from_center": (row["observed_bias"][key] - center) / half,
                        "after_offset_half_widths": (shifted - center) / half,
                        "inside_after_offset": inside,
                        "leave_one_out_delta": loo["delta"],
                        "leave_one_out_z_scatter_scaled": loo["z_scatter_scaled"],
                        "leave_one_out_significant": loo["p_two_sided_scatter_scaled"] < alpha,
                    }
                )
    out["band_recheck"] = {
        "offset": "each coefficient's delta over the other paths subtracted from its observed bias, bands unchanged",
        "inside_after_offset": inside_after,
        "coefficients": sum(len(r["bands"]) for r in falsification["paths"]),
        "rows": misses,
    }
    return out


def case2_offsets() -> dict[str, Any]:
    """The case-2 offsets under its retained centers and under split-law centers.

    Case 2's centers applied each path's largest excitation as an initial X error on all three qubits; the
    excitation term moves 01, 02, 12 and 012 and leaves 0, 1 and 2 within 0.005 spreads (case 3's envelope), so
    only 0, 1 and 2 compare across the two laws as retained. The split-law variant swaps each path's retained
    incoherent shift for the one the split law gives from case 2's own controls, as the case-2 ablation did, and
    keeps every spread (half-width over z, no envelope), so all 21 paths enter.
    """
    falsification = json.loads((CASE2 / "stage2-falsification.json").read_text(encoding="utf-8"))
    decision = json.loads((CASE2 / "stage1-decision.json").read_text(encoding="utf-8"))
    snapshot = json.loads((CASE2 / "stage1-snapshot.json").read_text(encoding="utf-8"))
    decided = {tuple(v["layout"]): v for v in decision["decisions"]}
    controls = [spe.read_control(d, ROOT) for d in CASE2_CONTROLS]
    law = sps.split(controls, spe.DEFAULT_ALPHA)
    rows = falsification["paths"]
    excitations = [ppc.split_excitation(law, snapshot, r["path"], "point") for r in rows]
    budgets = ppc.path_budgets(snapshot, [r["path"] for r in rows], excitations)
    alpha = 0.05 / len(KEYS)
    out: dict[str, Any] = {
        "controls": [str(d.relative_to(ROOT)) for d in CASE2_CONTROLS],
        "bonferroni_alpha": alpha,
        "retained_centers": {"excluded": list(CASE2_EXCLUDED), "coefficients": {}},
        "split_centers": {"excluded": [], "coefficients": {}},
    }
    for key in KEYS:
        retained, recentered = [], []
        for row, budget in zip(rows, budgets, strict=True):
            low, high = row["bands"][key]
            entry = decided[tuple(row["path"])]
            spread = (high - low) / (2.0 * float(entry["falsifier"]["z"]))
            center = (low + high) / 2.0
            moved = center - entry["budget"]["incoherent_shift"][key] + budget["incoherent_shift"][key]
            recentered.append((row["observed_bias"][key], moved, spread))
            if row["path"] not in CASE2_EXCLUDED:
                retained.append((row["observed_bias"][key], center, spread))
        for name, triples in (("retained_centers", retained), ("split_centers", recentered)):
            fit = pooled(triples)
            fit["significant"] = fit["p_two_sided_scatter_scaled"] < alpha
            out[name]["coefficients"][key] = fit
    return out


def q147_bit(isa: Path, qubit: int) -> list[tuple[str, int]]:
    """Per circuit of ``isa``, the (register, bit) that the final measurement of ``qubit`` writes."""
    with isa.open("rb") as handle:
        circuits = qpy.load(handle)
    out = []
    for circuit in circuits:
        found = [
            (circuit.find_bit(item.clbits[0]).registers[0][0].name, circuit.find_bit(item.clbits[0]).registers[0][1])
            for item in circuit.data
            if item.operation.name == "measure" and circuit.find_bit(item.qubits[0]).index == qubit
        ]
        if not found:
            raise SystemExit(f"{isa}: circuit {circuit.name} measures no qubit {qubit}")
        out.append(found[-1])
    return out


def shot_bits(item: tuple[Path, str, int]) -> list[int]:
    """One PUB file -> the shot-ordered reads of one register bit, bit b the b-th character from the right."""
    path, register, bit = item
    data = json.loads(path.read_text(encoding="utf-8"))["registers"][register]
    strings = data["bitstrings"]
    if len(strings) != int(data["num_shots"]):
        raise SystemExit(f"{path}: {len(strings)} bitstrings for {data['num_shots']} shots")
    return [int(s[-1 - bit]) for s in strings]


def raw_pubs(run: Path) -> list[Path]:
    (job,) = sorted((run / "raw").iterdir())
    index = json.loads((job / "index.json").read_text(encoding="utf-8"))["files"]
    pubs = sorted((name for name in index if name.startswith("pub_")), key=lambda n: int(n[4:-5]))
    return [job / name for name in pubs]


def two_proportion(hit_a: int, n_a: int, hit_b: int, n_b: int) -> dict[str, Any]:
    pa, pb = hit_a / n_a, hit_b / n_b
    pool = (hit_a + hit_b) / (n_a + n_b)
    se = math.sqrt(pool * (1 - pool) * (1 / n_a + 1 / n_b))
    diff_se = math.sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)
    z = (pa - pb) / se if se > 0 else 0.0
    return {"p_given_1": pa, "n_given_1": n_a, "p_given_0": pb, "n_given_0": n_b, "difference": pa - pb,
            "difference_se": diff_se, "z": z, "p_two_sided": normal_two_sided(z)}  # fmt: skip


def conditional(target: list[int], given: list[int]) -> dict[str, Any]:
    ones = [t for t, g in zip(target, given, strict=True) if g]
    zeros = [t for t, g in zip(target, given, strict=True) if not g]
    return two_proportion(sum(ones), len(ones), sum(zeros), len(zeros))


def x_history_run(run: Path) -> dict[str, Any]:
    """One x_history control run -> q147's shot-history conditionals."""
    (where,) = q147_bit(run / "isa.qpy", QUBIT)
    (pub,) = raw_pubs(run)
    bits = shot_bits((pub, *where))
    pairs: dict[str, list[int]] = {}
    for s in range(2, len(bits)):
        pairs.setdefault(f"{bits[s - 2]}{bits[s - 1]}", []).append(bits[s])
    return {
        "run": run.name,
        "excited_fraction": statistics.fmean(bits),
        "by_lag": {str(lag): conditional(bits[lag:], bits[:-lag]) for lag in range(1, 6)},
        "by_previous_two": {
            key: {"shots": len(v), "excited_fraction": statistics.fmean(v)} for key, v in sorted(pairs.items())
        },
    }


def x_history_test() -> dict[str, Any]:
    return {"runs": parallel.ordered_map(x_history_run, X_HISTORY, min_items=1)}


def stage2_test(split: dict[str, Any]) -> dict[str, Any]:
    record = json.loads((STAGE2 / "record.json").read_text(encoding="utf-8"))
    names = [pub["components"][0]["member"] for pub in record["execution_pubs"]]
    wheres = q147_bit(STAGE2 / "isa.qpy", QUBIT)
    files = raw_pubs(STAGE2)
    if len(files) != len(names) or len(wheres) != len(names):
        raise SystemExit(f"{len(files)} raw PUBs, {len(wheres)} circuits, {len(names)} execution PUBs")
    reads = parallel.ordered_map(shot_bits, [(f, *w) for f, w in zip(files, wheres, strict=True)], min_items=1)
    fractions = [statistics.fmean(r) for r in reads]
    for label in range(8):
        k = names.index(f"g88_readout_{label}")
        if (fractions[k] > 0.5) != bool(label & 1):
            raise SystemExit(f"g88_readout_{label} reads q{QUBIT} excited in {fractions[k]:.3f} of its shots")
    count, shots = len(reads), len(reads[0])
    # Column-wise execution in submitted order: shot s of PUB k is the (s * count + k)-th circuit executed.
    sequence = [reads[k][s] for s in range(shots) for k in range(count)]
    arms: dict[str, Any] = {}
    for label in ZERO_LABELS:
        k = names.index(f"g88_readout_{label}")
        arm: dict[str, Any] = {"excited_fraction": fractions[k]}
        for lag in (-1, 1):
            target, given = [], []
            for s in range(shots):
                j = s * count + k + lag
                if 0 <= j < len(sequence):
                    target.append(reads[k][s])
                    given.append(sequence[j])
            neighbor = names[(k + lag) % count]
            arm[str(lag)] = {"neighbor": neighbor, "neighbor_excited_fraction": fractions[names.index(neighbor)]}
            arm[str(lag)].update(conditional(target, given))
        arms[f"g88_readout_{label}"] = arm

    q = split["qubits"][str(QUBIT)]
    readout = q["readouts"]["x_history"][0][0]
    e01, e10 = float(readout["prob_meas0_prep1"]), float(readout["prob_meas1_prep0"])
    mean_read = statistics.fmean(fractions)
    end_excited = (mean_read - e10) / (1.0 - e01 - e10)
    zero = statistics.fmean(fractions[names.index(f"g88_readout_{lb}")] for lb in ZERO_LABELS)
    one = statistics.fmean(fractions[names.index(f"g88_readout_{lb}")] for lb in range(8) if lb & 1)
    x_end = 1.0 - float(q["fractions"]["x_history"])
    k0 = names.index("g88_readout_0")
    path_qubits = record["fusion_placement"]["pin_replicas"]
    slots = [(f"g0_r{r}_c", b, qubit) for r, path in enumerate(path_qubits) for b, qubit in enumerate(path)]
    zero_reads = parallel.ordered_map(shot_bits, [(files[k0], register, b) for register, b, _ in slots], min_items=1)
    others = {
        str(qubit): {
            "readout_0": statistics.fmean(bits),
            "prep0": float(split["qubits"][str(qubit)]["fractions"]["prep0"]),
        }
        for (_, _, qubit), bits in zip(slots, zero_reads, strict=True)
    }
    excess = fractions[k0]
    excess_se = math.sqrt(excess * (1 - excess) / shots)
    prep0, history = float(q["fractions"]["prep0"]), float(q["fractions"]["x_history"])
    ceiling = float(q["hd"]) / x_end + prep0
    efficiency = one / (1.0 - zero)
    ceiling_in_job = (history - prep0) / (efficiency - prep0) / x_end + prep0
    return {
        "pubs": count,
        "shots": len(reads[0]),
        "zero_arm_conditional": arms,
        "zero_arms_read_excited_fraction": zero,
        "one_arms_read_excited_fraction": one,
        "readout_0": {
            "q147_read_excited_fraction": excess,
            "se": excess_se,
            "end_state_ceiling": ceiling,
            "z_above_ceiling": (excess - ceiling) / excess_se,
            "in_job_one_efficiency": efficiency,
            "end_state_ceiling_in_job_efficiency": ceiling_in_job,
            "z_above_ceiling_in_job_efficiency": (excess - ceiling_in_job) / excess_se,
            "ceiling_rule": "hd / (1 - x_history fraction) + prep0 fraction: every earlier shot left q147 excited",
            "other_qubits_against_prep0": others,
        },
        "predicted_lag_minus_1_difference": float(q["hd"]) * (1.0 - e01 - e10),
        "mean_read_excited_fraction": mean_read,
        "readout_e01": e01,
        "readout_e10": e10,
        "mean_end_excited_fraction": end_excited,
        "x_history_end_excited_fraction": x_end,
        "f": end_excited / x_end,
        "f_raw_read": mean_read / x_end,
        "per_pub_read_excited_fraction": [
            {"pub_index": k, "member": name, "read_excited_fraction": fraction}
            for k, (name, fraction) in enumerate(zip(names, fractions, strict=True))
        ],
    }


def main() -> int:
    falsification = json.loads((E / "stage2-falsification.json").read_text(encoding="utf-8"))
    decision = json.loads((E / "stage1-decision.json").read_text(encoding="utf-8"))
    split = json.loads((E / "split.json").read_text(encoding="utf-8"))
    result = {
        "status": "post-hoc, descriptive; outside the case-3 preregistration",
        "pooled_offset": offset_test(falsification, decision),
        "x_history_shot_history": x_history_test(),
        "stage2_shot_history": stage2_test(split),
        "case2_pooled_offset": case2_offsets(),
        "lambda": falsification["discrimination"],
    }
    (E / "offset-and-history.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
