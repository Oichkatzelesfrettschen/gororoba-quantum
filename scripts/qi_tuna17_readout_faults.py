"""Falsification tests of the Tuna-17 readout faults of 2026-10-17 on Q0, Q6 and Q9, from named retained runs.

Every input is a run named below, so retaining a new run leaves the record
unchanged. Four blocks:

- Q9 assignment bounds. With excited population p, assignment errors e0
  (0 read as 1) and e1, scale s = 1 - e0 - e1 > 0, an idle readout gives
  P(1|idle) = e0 + s p and an X that inverts at most fully gives
  P(1|X) <= e0 + s (1 - p) for p <= 1/2; relaxation during a wait before
  readout only lowers P(1|X). Hence e0 >= P(1|idle) + P(1|X) - 1 whatever p
  and e1, e0 <= P(1|idle), s >= P(1|X) - P(1|idle), and
  p <= (1 - P(1|X)) / (P(1|X) - P(1|idle)). Both readouts come from one batch.
- Q9 herald conditioning. A series-Q arm measures every target into
  b[17 + q], waits tau, plays X90, two idle cycles and X90, and reads b[q].
  With two idle cycles the X90 pair acts as X, so a shot left in |0> by the
  opening readout ends near the X level and a shot left in |1> ends near the
  idle floor A (batch-00 readout-0). The excited fraction among opening-1
  shots is w = (P(f|h0) - P(f|h1)) / (P(f|h0) - A); misassignment that leaves
  the qubit in |0> gives w = 0, and an excitation that the readout reports,
  present before it or caused by it, gives w = 1.
- Q0 and Q6 short-T1 test. If the zero-wait loss of P(1|1) after the
  platform calibration were relaxation inside the readout window
  (READOUT_SECONDS, the Tuna measurement duration in
  docs/notes/quantum_inspire/cqasm.md) at the earlier assignment scale, then
  the excited survival r = (P11 - P10) / (P11_pre - P10_pre) bounds
  T1 <= READOUT_SECONDS / ln(1 / r), and a 2 us wait before readout keeps at
  most P10 + (P11 - P10) exp(-2 us / T1_max). The test compares that ceiling
  with the wait runs; it assumes the device stayed unchanged between the wait
  runs and the later zero-wait runs.
- Q0 and Q6 Ramsey under the matched calibration. Post-calibration X and Y
  arms at d = 77 are inverted with the post-calibration readout pair, whose
  2 us wait matches the arms'. An X whose rotation angle is 2 beta instead of
  pi gives raw quadratures sin^2(beta) (1 + cos phi) / 2 and
  sin^2(beta) (1 + sin phi) / 2, the form a readout scale gives, so the
  inverted visibility separates neither under-rotation from |1>
  misassignment; the record lists it as context and states the discriminator
  a hardware run needs: P1 after X X, which under-rotation predicts at
  P10 + S_pre sin^2(2 beta) and misassignment at P10.

The 05:23Z endpoint is the last job of series-Q batch-04, whose opening
readout of Q9 (b[26]) is listed beside the jobs' finish times.

Usage: "$PYTHON" scripts/qi_tuna17_readout_faults.py [--check] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from qi_coupler_zz_map import bit, retained_path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results/quantum_inspire/runs"
OUT = ROOT / "results/quantum_inspire/tuna_17_readout_faults.json"
SCHEMA = "qi-tuna17-readout-faults-v1"
SIGNIFICANT = 6
NQUBITS = 17
OPENING_OFFSET = 17
READOUT_SECONDS = 800e-9
WAIT_SECONDS = 2e-6

P_SERIES = "2026-10-17T032034Z-readout_ringdown_tuna_17_P-"
Q_SERIES = "2026-10-17T032034Z-readout_ringdown_tuna_17_Q-"
PRE_CALIBRATION_RUNS = ("2026-10-16T221133Z-zero_divisor_tuna_17", "2026-10-16T224924Z-coupler_zz_tuna_17-batch-00")
POST_CALIBRATION_RUNS = (
    "2026-10-17T052547Z-zero_divisor_tuna_17-batch-00",
    "2026-10-17T052915Z-zero_divisor_tuna_17-batch-01",
    "2026-10-17T053226Z-zero_divisor_tuna_17-batch-02",
)
Q9_WAIT_RUN = Q_SERIES + "batch-00"
WAIT_RUNS = (P_SERIES + "recal-041520", P_SERIES + "recal-042425")
HERALD_ARMS = (
    (Q_SERIES + "batch-01", "tau000-x-d002.cq"),
    (Q_SERIES + "batch-01", "tau005-x-d002.cq"),
    (Q_SERIES + "batch-02", "tau015-x-d002.cq"),
    (Q_SERIES + "batch-02", "tau040-x-d002.cq"),
    (Q_SERIES + "batch-02", "tau100-x-d002.cq"),
)
HERALD_FLOOR_RUN = Q_SERIES + "batch-00"
ENDPOINT_RUN = Q_SERIES + "batch-04"
RAMSEY_PAIRS = (
    ("reference", P_SERIES + "batch-05-rerun1", P_SERIES + "batch-07"),
    ("tau000", P_SERIES + "batch-05-rerun1", P_SERIES + "batch-07"),
    ("tau005", P_SERIES + "batch-05-rerun1", P_SERIES + "batch-07"),
    ("tau015", P_SERIES + "batch-06-rerun1", P_SERIES + "batch-08"),
    ("tau040", P_SERIES + "batch-06-rerun1", P_SERIES + "batch-08"),
    ("tau100", P_SERIES + "batch-06-rerun1", P_SERIES + "batch-08"),
)
RAMSEY_DELAY = "d077"
FAULT_QUBITS = (0, 6)
Q9 = 9


def quantized(value: Any) -> Any:
    """value with every float rounded to SIGNIFICANT significant digits."""
    if isinstance(value, float):
        return float(f"{value:.{SIGNIFICANT}g}")
    if isinstance(value, dict):
        return {key: quantized(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [quantized(item) for item in value]
    return value


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def shots(run: str, circuit: str) -> list[str]:
    path = RUNS / run / "raw" / f"{circuit}.json"
    if not path.is_file():
        raise SystemExit(f"{retained_path(path)} is missing")
    return list(read_json(path))


def rate(sample: list[str], qubit: int) -> tuple[float, int]:
    return sum(bit(s, qubit) for s in sample) / len(sample), len(sample)


def se(p: float, n: int) -> float:
    return math.sqrt(p * (1 - p) / n)


def readout_pair(run: str, qubit: int) -> dict[str, Any]:
    p10, n = rate(shots(run, "readout-0.cq"), qubit)
    p11, _ = rate(shots(run, "readout-1.cq"), qubit)
    return {"run": retained_path(RUNS / run), "shots": n, "p1_given_0": p10, "p1_given_1": p11}


def q9_assignment() -> dict[str, Any]:
    pre = [readout_pair(run, Q9) for run in PRE_CALIBRATION_RUNS]
    post = []
    for run in (Q9_WAIT_RUN, *POST_CALIBRATION_RUNS):
        row = readout_pair(run, Q9)
        idle, flipped = row["p1_given_0"], row["p1_given_1"]
        row["e0_lower"] = idle + flipped - 1
        row["e0_upper"] = idle
        row["scale_lower"] = flipped - idle
        row["population_upper"] = (1 - flipped) / (flipped - idle)
        post.append(row)
    return {
        "assumptions": "p <= 1/2, X inverts at most fully, s > 0, idle and X readouts from one batch",
        "pre_change": [{**row, "e0_upper": row["p1_given_0"]} for row in pre],
        "post_change": post,
        "e0_lower_min": min(row["e0_lower"] for row in post),
        "e0_upper_pre_max": max(row["p1_given_0"] for row in pre),
        "population_upper_max": max(row["population_upper"] for row in post),
    }


def herald(qubit: int, floor: float, floor_n: int) -> dict[str, Any]:
    rows = []
    totals = {0: [0, 0], 1: [0, 0]}
    for run, circuit in HERALD_ARMS:
        sample = shots(run, circuit)
        split: dict[int, list[str]] = {0: [], 1: []}
        for s in sample:
            split[bit(s, OPENING_OFFSET + qubit)].append(s)
        level = {h: rate(split[h], qubit)[0] for h in (0, 1)}
        for h in (0, 1):
            totals[h][0] += sum(bit(s, qubit) for s in split[h])
            totals[h][1] += len(split[h])
        rows.append(
            {
                "run": retained_path(RUNS / run),
                "circuit": circuit,
                "opening_1_fraction": len(split[1]) / len(sample),
                "p_final_1_given_opening_0": level[0],
                "p_final_1_given_opening_1": level[1],
                "excited_fraction_w": (level[0] - level[1]) / (level[0] - floor),
            }
        )
    h0, n0 = totals[0][0] / totals[0][1], totals[0][1]
    h1, n1 = totals[1][0] / totals[1][1], totals[1][1]
    w = (h0 - h1) / (h0 - floor)
    # Delta-method standard error of w in the three independent binomial rates.
    gradient = ((h1 - floor) / (h0 - floor) ** 2, -1 / (h0 - floor), (h0 - h1) / (h0 - floor) ** 2)
    variances = (se(h0, n0) ** 2, se(h1, n1) ** 2, se(floor, floor_n) ** 2)
    w_se = math.sqrt(sum(g**2 * v for g, v in zip(gradient, variances, strict=True)))
    return {
        "qubit": qubit,
        "idle_floor": floor,
        "arms": rows,
        "pooled": {"opening_0_shots": n0, "opening_1_shots": n1, "w": w, "w_se": w_se},
    }


def herald_block() -> dict[str, Any]:
    cases = read_json(RUNS / HERALD_ARMS[0][0] / "cases.json")
    floor_shots = shots(HERALD_FLOOR_RUN, "readout-0.cq")
    targets = []
    for q in cases["targets"]:
        floor, floor_n = rate(floor_shots, q)
        targets.append(herald(q, floor, floor_n))
    return {
        "floor_run": retained_path(RUNS / HERALD_FLOOR_RUN),
        "falsifier": "w >= 0.5 for Q9 would put at least half of its opening-1 shots in |1>; w near 0 is misassignment",
        "targets": targets,
    }


def short_t1() -> dict[str, Any]:
    out = {}
    for q in FAULT_QUBITS:
        pre = [readout_pair(run, q) for run in PRE_CALIBRATION_RUNS]
        post = [readout_pair(run, q) for run in POST_CALIBRATION_RUNS]
        waited = [readout_pair(run, q) for run in WAIT_RUNS]
        pre_scale = sum(r["p1_given_1"] - r["p1_given_0"] for r in pre) / len(pre)
        floor = sum(r["p1_given_0"] for r in post) / len(post)
        excited = sum(r["p1_given_1"] for r in post) / len(post) - floor
        survival = excited / pre_scale
        t1_max = READOUT_SECONDS / math.log(1 / survival)
        wait_floor = sum(r["p1_given_0"] for r in waited) / len(waited)
        ceiling = wait_floor + excited * math.exp(-WAIT_SECONDS / t1_max)
        observed = [r["p1_given_1"] for r in waited]
        z = [(value - ceiling) / se(value, r["shots"]) for value, r in zip(observed, waited, strict=True)]
        out[str(q)] = {
            "pre_change": pre,
            "no_wait": post,
            "two_us_wait": waited,
            "readout_survival": survival,
            "t1_max_us": t1_max * 1e6,
            "two_us_ceiling": ceiling,
            "two_us_observed": observed,
            "excess_z": z,
            "hypothesis_rejected": min(z) > 3,
        }
    return {
        "hypothesis": "the post-calibration zero-wait loss of P(1|1) is relaxation inside the readout window",
        "readout_seconds": READOUT_SECONDS,
        "assumption": "the device is unchanged between the 2 us wait runs (04:15-04:24Z) and the zero-wait runs "
        "(05:26-05:33Z)",
        "qubits": out,
    }


def ramsey() -> dict[str, Any]:
    calibrations = {q: [readout_pair(run, q) for run in WAIT_RUNS] for q in range(NQUBITS)}
    cases = read_json(RUNS / RAMSEY_PAIRS[0][1] / "cases.json")
    out = {}
    for q in cases["targets"]:
        p10 = sum(r["p1_given_0"] for r in calibrations[q]) / len(WAIT_RUNS)
        p11 = sum(r["p1_given_1"] for r in calibrations[q]) / len(WAIT_RUNS)
        n_cal = sum(r["shots"] for r in calibrations[q])
        arms = []
        for arm, x_run, y_run in RAMSEY_PAIRS:
            px, nx = rate(shots(x_run, f"{arm}-x-{RAMSEY_DELAY}.cq"), q)
            py, ny = rate(shots(y_run, f"{arm}-y-{RAMSEY_DELAY}.cq"), q)

            def visibility(e: float, f: float, a: float = px, b: float = py) -> float:
                return math.hypot(2 * (a - e) / (f - e) - 1, 2 * (b - e) / (f - e) - 1)

            h = 1e-7
            partials = [
                ((visibility(p10, p11, px + h, py) - visibility(p10, p11, px - h, py)) / (2 * h), se(px, nx)),
                ((visibility(p10, p11, px, py + h) - visibility(p10, p11, px, py - h)) / (2 * h), se(py, ny)),
                ((visibility(p10 + h, p11) - visibility(p10 - h, p11)) / (2 * h), se(p10, n_cal)),
                ((visibility(p10, p11 + h) - visibility(p10, p11 - h)) / (2 * h), se(p11, n_cal)),
            ]
            x = 2 * (px - p10) / (p11 - p10) - 1
            y = 2 * (py - p10) / (p11 - p10) - 1
            arms.append(
                {
                    "arm": arm,
                    "raw_x": px,
                    "raw_y": py,
                    "visibility": visibility(p10, p11),
                    "visibility_se": math.sqrt(sum((g * s) ** 2 for g, s in partials)),
                    "phase_deg": math.degrees(math.atan2(y, x)),
                }
            )
        out[str(q)] = {"calibration_p1_given_0": p10, "calibration_p1_given_1": p11, "arms": arms}
    return {
        "x_runs": sorted({retained_path(RUNS / x) for _, x, _ in RAMSEY_PAIRS}),
        "y_runs": sorted({retained_path(RUNS / y) for _, _, y in RAMSEY_PAIRS}),
        "calibration_runs": [retained_path(RUNS / run) for run in WAIT_RUNS],
        "degeneracy": "an X of angle 2 beta gives raw quadratures sin^2(beta) (1 + cos phi) / 2 and "
        "sin^2(beta) (1 + sin phi) / 2, the readout-scale form, so the inverted visibility does not separate "
        "under-rotation from |1> misassignment",
        "targets": out,
    }


def discriminator(t1: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for q in FAULT_QUBITS:
        block = t1["qubits"][str(q)]
        pre_scale = sum(r["p1_given_1"] - r["p1_given_0"] for r in block["pre_change"]) / len(block["pre_change"])
        floor = sum(r["p1_given_0"] for r in block["no_wait"]) / len(block["no_wait"])
        excited = sum(r["p1_given_1"] for r in block["no_wait"]) / len(block["no_wait"]) - floor
        beta = math.asin(math.sqrt(min(1.0, excited / pre_scale)))
        out[str(q)] = {
            "pre_change_scale": pre_scale,
            "half_angle_beta_rad": beta,
            "xx_p1_under_rotation": floor + pre_scale * math.sin(2 * beta) ** 2,
            "xx_p1_misassignment": floor,
        }
    return {
        "observable": "P1 after X X with no wait, in the same batch as a readout-0 and readout-1 pair",
        "qubits": out,
    }


def endpoint() -> dict[str, Any]:
    result = read_json(RUNS / ENDPOINT_RUN / "results.json")
    circuits = sorted(p.name for p in (RUNS / ENDPOINT_RUN).glob("*.cq"))
    return {
        "run": retained_path(RUNS / ENDPOINT_RUN),
        "job_finished_at": sorted(job["job"]["finished_at"] for job in result["jobs"]),
        "q9_opening_readout_p1": {c: rate(shots(ENDPOINT_RUN, c), OPENING_OFFSET + Q9)[0] for c in circuits},
    }


def build() -> dict[str, Any]:
    t1 = short_t1()
    return {
        "schema": SCHEMA,
        "profile": "tuna_17",
        "q9_assignment": q9_assignment(),
        "q9_herald": herald_block(),
        "short_t1": t1,
        "ramsey_matched_calibration": ramsey(),
        "xx_discriminator": discriminator(t1),
        "q9_endpoint": endpoint(),
    }


def render() -> str:
    return json.dumps(quantized(build()), indent=1) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="recompute the record and compare bytes")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    text = render()
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != text:
            print(f"{args.out} differs from its recomputation", file=sys.stderr)
            return 1
        print(f"{args.out}: readout-fault tests reproduce")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(f"readout-fault tests -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
