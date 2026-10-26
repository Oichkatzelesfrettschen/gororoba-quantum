"""IQM Garnet pre-flight probe of the measurement-sequence pinching case: four circuits, one stop rule.

The probe job runs four circuits of the main case, copied byte for byte from its circuits/ directory, on the same six
qubits: ro0 (the initialized state), ro1 (prx(pi)), unitary-n16-s0p (sixteen pi/2-pair steps, no measurement) and
measure-n16-s0p (the same steps with a measure after each). Every circuit waits 2.0 us before the final measure `f`.
The raw P(0) of `f` per qubit is compared with the raw model of the same circuit over an initialization excitation
from 0 to 0.068 (`raw_band` of the main case's prediction.json), the band the diagnostic job found to hold the
starting excitation of the qubits it read (docs/design/iqm-garnet-measurement-sequence-pinching.md, "Pre-flight stop
rule").

Stop rule (judge), per qubit. A reading outside its band by Z_DECIDE = 3 binomial standard errors fails, the standard
error taken at the nearest band edge and the probe's shot count; the ro0 minus ro1 contrast must be at least
CONTRAST_FLOOR = 0.6; every key a circuit declares (f, and m0 to m15 in measure-n16-s0p) must return one outcome per
shot for every qubit. The probe proceeds to the main submission only if every qubit passes. The check gates the
submission and never enters the main case's analysis.

Usage: "$PYTHON" scripts/iqm_measurement_preflight.py (build DIR [--shots N] | check DIR
       | analyze RUN_DIR --out FILE [--replay] [--mock] | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_measurement_sequence as seq  # noqa: E402
from iqm_jobs import CANCEL_MARGIN, CASE_SCHEMA, dump, run_facts  # noqa: E402
from iqm_platform import sha256  # noqa: E402

CASE = "measurement-sequence-pinching-probe"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
JOB = "probe"
EXCERPT = seq.EXCERPT
MAIN_CASE = ROOT / "results/iqm/cases" / seq.CASE
SHOTS = 1000
MAX_CREDITS = {"garnet": 1.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}
Z_DECIDE = seq.Z_DECIDE
CONTRAST_FLOOR = 0.6
# Probe circuit -> the key of raw_band (the circuit names of the band carry no sign tag).
BAND_KEY = {"ro0": "ro0", "ro1": "ro1", "unitary-n16-s0p": "unitary-16", "measure-n16-s0p": "measure-16"}
NAMES = tuple(BAND_KEY)


def billing(circuits: list[dict[str, Any]], shots: int, model: str = "v2") -> dict[str, Any]:
    """The seq.BILLING_MODELS fit at the probe's ceiling."""
    fit = seq.BILLING_MODELS[model]
    schedule = shots * sum(seq.estimator_shot_seconds(c) for c in circuits)
    records = shots * sum(seq.mid_measures(c) for c in circuits)
    execution = (
        schedule + fit["fixed"] + fit["per_circuit_shot"] * len(circuits) * shots + fit["per_mid_record"] * records
    )
    worst = execution + fit["residual"] + fit["runtime_over"]
    threshold = MAX_CREDITS[QC] / PRICE[QC] - CANCEL_MARGIN
    return {
        "shots": shots,
        "circuits": len(circuits),
        "compiled_schedule_seconds": schedule,
        "execution_seconds": execution,
        "worst_case_runtime_seconds": worst,
        "billed_seconds": math.ceil(worst),
        "credits": math.ceil(worst) * PRICE[QC],
        "cancel_threshold_seconds": threshold,
        "cancel_margin_seconds": threshold - worst,
    }


def build_files(main: Path, shots: int, model: str = "v2") -> dict[str, str]:
    """The probe case from the main case directory `main`: its four circuits verbatim, the band per qubit, the job."""
    main_cases = (main / "cases.json").read_bytes()
    main_prediction = seq.load_json(main / "prediction.json")
    files: dict[str, str] = {}
    for name in NAMES:
        files[f"circuits/{name}.json"] = (main / f"circuits/{name}.json").read_text(encoding="utf-8")
    circuits = [json.loads(files[f"circuits/{name}.json"]) for name in NAMES]
    bill = billing(circuits, shots, model)
    if bill["billed_seconds"] > 1 or bill["credits"] > MAX_CREDITS[QC] or bill["cancel_margin_seconds"] <= 0:
        raise ValueError(f"the probe bills {bill}")
    excerpt_text = (main / EXCERPT).read_text(encoding="utf-8")
    prediction = {
        "calibration_set": main_prediction["calibration_set"],
        "main_cases_sha256": sha256(main_cases),
        "shots": shots,
        "excitation_band": list(seq.RAW_EXCITATION_BAND),
        "band_source": "prediction.json of the main case, raw_band per qubit",
        "rule": {
            "z_decide": Z_DECIDE,
            "contrast_floor": CONTRAST_FLOOR,
            "reading": "raw P(0) of key f; a reading outside its band is judged at the binomial standard error of the "
            "nearest band edge and the probe's shot count; ro0 minus ro1 raw P(0) is at least the contrast floor; "
            "every declared key returns one outcome per shot for every qubit",
        },
        "qubits": {q: {"raw_band": row["raw_band"]} for q, row in main_prediction["qubits"].items()},
        "billing": bill,
        **({"billing_model": model} if model == "v2" else {}),
    }
    files["prediction.json"] = dump(prediction)
    job = {
        "job": JOB,
        "circuits": [
            {"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items() if "circuits/" in rel
        ],
        "shots": shots,
        "options": {**OPTIONS, "calibration_set_id": {QC: main_prediction["calibration_set"]}},
        "expected_seconds": round(bill["execution_seconds"], 3),
        "max_credits": MAX_CREDITS,
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Do the ro0, ro1, N = 16 unitary and N = 16 measure circuits of the rebuilt pinching case read on "
                f"{', '.join(prediction['qubits'])} within their raw model bands, with every key returned?"
            ),
            "qcs": QCS,
            "jobs": [job],
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    files[EXCERPT] = excerpt_text
    return files


def write(directory: Path, main: Path, shots: int) -> None:
    files = build_files(main, shots)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    prediction = json.loads(files["prediction.json"])
    print(json.dumps({"circuits": len(NAMES), "shots": shots, **prediction["billing"]}))


def check(directory: Path) -> None:
    shots = seq.load_json(directory / "cases.json")["jobs"][0]["shots"]
    model = seq.load_json(directory / "prediction.json").get("billing_model", "v1")
    files = build_files(MAIN_CASE, shots, model)
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if present != set(files):
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ set(files))}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from {MAIN_CASE.name}")


def judge(p0: float, band: list[float], shots: int) -> dict[str, Any]:
    """The reading's distance outside its band in binomial standard errors at the nearest band edge (0 inside)."""
    low, high = band
    if low <= p0 <= high:
        return {"p0": p0, "band": band, "z": 0.0, "passes": True}
    edge = low if p0 < low else high
    z = (p0 - edge) / math.sqrt(edge * (1 - edge) / shots)
    return {"p0": p0, "band": band, "z": z, "passes": abs(z) < Z_DECIDE}


def keys_present(circuit: dict[str, Any], result: dict[str, Any], shots: int, width: int) -> bool:
    declared = {o["args"]["key"] for o in circuit["instructions"] if o["name"] == "measure"}
    return declared <= set(result) and all(
        len(result[k]) == shots and all(len(shot) == width for shot in result[k]) for k in declared
    )


def evaluate(
    circuits: list[dict[str, Any]], results: list[dict[str, Any]], prediction: dict[str, Any], shots: int
) -> dict[str, Any]:
    """The stop rule over the probe's circuits and their per-key outcomes."""
    for c, r in zip(circuits, results, strict=True):
        if not r.get(seq.FINAL_KEY):
            raise ValueError(f"{c['name']}: no outcomes for the final key {seq.FINAL_KEY}; the probe stops")
    finals = [{"name": c["name"], "instructions": c["instructions"][-1:]} for c in circuits]
    counts = seq.tally(finals, [{seq.FINAL_KEY: r.get(seq.FINAL_KEY, [])} for r in results])
    by_name = {c["name"]: (c, r) for c, r in zip(circuits, results, strict=True)}
    qubits: dict[str, Any] = {}
    for q, row in prediction["qubits"].items():
        readings: dict[str, Any] = {}
        for name in NAMES:
            k0, k1 = counts[name]["final"][q]
            circuit, result = by_name[name]
            width = len(seq.qubits_of(circuit))
            readings[name] = {
                **judge(k0 / (k0 + k1), row["raw_band"][BAND_KEY[name]], shots),
                "keys": keys_present(circuit, result, shots, width),
            }
        contrast = readings["ro0"]["p0"] - readings["ro1"]["p0"]
        passes = all(r["passes"] and r["keys"] for r in readings.values()) and contrast >= CONTRAST_FLOOR
        qubits[q] = {
            "readings": readings,
            "contrast": contrast,
            "contrast_passes": contrast >= CONTRAST_FLOOR,
            "passes": passes,
        }
    return {"qubits": qubits, "proceed": all(r["passes"] for r in qubits.values())}


def table(analysis: dict[str, Any]) -> str:
    """The per-qubit pass or fail lines of an analysis."""
    lines = [f"{'qubit':<6}{'ro0':>9}{'ro1':>9}{'unitary-16':>12}{'measure-16':>12}{'contrast':>10}  result"]
    for q, row in analysis["qubits"].items():
        cells = "".join(f"{row['readings'][name]['p0']:>{w}.3f}" for name, w in zip(NAMES, (9, 9, 12, 12), strict=True))
        worst = max(abs(r["z"]) for r in row["readings"].values())
        verdict = "PASS" if row["passes"] else "FAIL"
        lines.append(f"{q:<6}{cells}{row['contrast']:>10.3f}  {verdict} (largest |z| {worst:.2f})")
    lines.append("proceed" if analysis["proceed"] else "stop")
    return "\n".join(lines)


def analyze(run_dir: Path, mock: bool = False) -> dict[str, Any]:
    """The stop rule over a garnet run of the probe; with mock the same pipeline over a garnet:mock run, whose random
    outcomes decide nothing."""
    facts = run_facts(run_dir)
    submission = seq.load_json(run_dir / "submission.json")
    case = seq.load_json(run_dir / "cases.json")
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    qc = f"{QC}:mock" if mock else QC
    if submission["qc"] != qc or case.get("case") != CASE:
        raise ValueError(f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {CASE} run on {qc}")
    prediction = json.loads(prediction_bytes)
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [seq.load_json(run_dir / entry["file"]) for entry in row["circuits"]]
    results = json.loads((run_dir / "raw/measurements.json").read_bytes())
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    return {
        "schema": "iqm-measurement-preflight-analysis-v1",
        "run": run_dir.name,
        "mock": mock,
        "calibration_set": record["compilation"]["calibration_set_id"],
        "main_cases_sha256": prediction["main_cases_sha256"],
        "charge": facts["charge"],
        "shots": row["shots"],
        **evaluate(circuits, results, prediction, row["shots"]),
    }


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def synthetic(
    circuits: list[dict[str, Any]], prediction: dict[str, Any], shots: int, reading: dict[str, dict[str, float]]
) -> list[dict[str, Any]]:
    """Per-circuit outcomes of model devices: reading[q][circuit] is the expected P(0); bits follow the circuit's
    qubit order with the first round(shots * P(0)) shots at 0."""
    out = []
    for c in circuits:
        qubits = seq.qubits_of(c)
        keys = [o["args"]["key"] for o in c["instructions"] if o["name"] == "measure"]
        result = {}
        for key in keys:
            ones = {q: shots - round(shots * reading[q][c["name"]]) for q in qubits}
            result[key] = [[int(shot >= shots - ones[q]) for q in qubits] for shot in range(shots)]
        out.append(result)
    return out


def self_test() -> str:
    seq_prediction = seq.load_json(MAIN_CASE / "prediction.json")
    files = build_files(MAIN_CASE, SHOTS)
    expect(files == build_files(MAIN_CASE, SHOTS), "the build is not deterministic")
    for name in NAMES:
        expect(
            files[f"circuits/{name}.json"] == (MAIN_CASE / f"circuits/{name}.json").read_text(encoding="utf-8"),
            f"{name} differs from the main case",
        )
    expect(
        sha256((MAIN_CASE / "cases.json").read_bytes()) == json.loads(files["prediction.json"])["main_cases_sha256"],
        "main digest",
    )
    cases = json.loads(files["cases.json"])
    expect(
        cases["jobs"][0]["max_credits"] == MAX_CREDITS and cases["jobs"][0]["shots"] == SHOTS, "job ceiling or shots"
    )
    prediction = json.loads(files["prediction.json"])
    expect(prediction["billing"]["credits"] <= MAX_CREDITS[QC], f"billing {prediction['billing']}")
    expect(
        all(
            prediction["qubits"][q]["raw_band"] == seq_prediction["qubits"][q]["raw_band"] for q in prediction["qubits"]
        ),
        "band",
    )
    circuits = [json.loads(files[f"circuits/{name}.json"]) for name in NAMES]
    qubits = list(prediction["qubits"])
    excerpt = json.loads(files[EXCERPT])

    def reading(p_init: float) -> dict[str, dict[str, float]]:
        return {q: {name: seq.raw_p0(BAND_KEY[name], excerpt["qubits"][q], p_init) for name in NAMES} for q in qubits}

    # A model device at either end of the excitation band passes on every qubit.
    for p_init in seq.RAW_EXCITATION_BAND:
        passed = evaluate(circuits, synthetic(circuits, prediction, SHOTS, reading(p_init)), prediction, SHOTS)
        expect(passed["proceed"], f"a model device at p = {p_init} stops: {table(passed)}")
    # Each planted fault stops exactly its qubit.
    faults = {
        "collapsed T1 (ro1 at 0.52)": ("ro1", 0.52),
        "unitary excess (0.38)": ("unitary-n16-s0p", 0.38),
        "measure below band": ("measure-n16-s0p", 0.70),
        "ro0 below band": ("ro0", 0.80),
    }
    for label, (name, value) in faults.items():
        planted = reading(0.03)
        planted[qubits[0]][name] = value
        stopped = evaluate(circuits, synthetic(circuits, prediction, SHOTS, planted), prediction, SHOTS)
        expect(not stopped["proceed"] and not stopped["qubits"][qubits[0]]["passes"], f"{label} passes")
        expect(all(stopped["qubits"][q]["passes"] for q in qubits[1:]), f"{label} stops another qubit")
    # A missing key stops the qubit's circuit.
    outcomes = synthetic(circuits, prediction, SHOTS, reading(0.03))
    del outcomes[NAMES.index("measure-n16-s0p")]["m7"]
    missing = evaluate(circuits, outcomes, prediction, SHOTS)
    expect(not missing["proceed"], "a missing key passes")
    # The contrast floor.
    near = judge(0.5, [0.4, 0.6], SHOTS)
    expect(near["passes"] and near["z"] == 0.0, "inside the band")
    edge = judge(0.6 + 3 * math.sqrt(0.6 * 0.4 / SHOTS), [0.4, 0.6], SHOTS)
    expect(not edge["passes"] and abs(edge["z"] - 3) < 1e-9, f"3 SE above the edge {edge}")
    return (
        f"measurement preflight: {len(NAMES)} circuits on {', '.join(qubits)}, {SHOTS} shots, "
        f"{prediction['billing']['worst_case_runtime_seconds']:.3f} s worst-case runtime, "
        f"{prediction['billing']['credits']} credits; the circuits match the main case byte for byte, the model band "
        "ends pass, and each planted fault stops its qubit"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--shots", type=int, default=SHOTS)
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    an.add_argument("--mock", action="store_true", help="analyze a garnet:mock run; its numbers decide nothing")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, MAIN_CASE, args.shots)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        analysis = analyze(args.run_dir, args.mock)
        text = dump(analysis)
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
            print(table(analysis))
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
