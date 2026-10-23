"""Null-controlled IQM Garnet cases of the signed kernel probe: the sign of t against the t = 0 offset.

The signed probe that ran on Garnet (scripts/iqm_signed_probe.py) read odd parts (Z(t) - Z(-t))/2 of
+0.0220 at |t| = 0.25 and +0.0058 at |t| = 0.05, with every +t circuit listed before its -t circuit
and no arm at t = 0. Its observable t/(2 + |t|) holds for every unit vector u
(scripts/iqm_probe_audit.py), so these cases measure the device, not the kernel: whether the odd part
grows with t once two artifacts are removed.

- Batch position: the +t and -t circuits alternate +, -, -, + in the list.
- Null offset: the t = +0 and t = -0 circuits bind the same compile at a vanishing signed amplitude
  with sign phase 0 and pi. The ideal odd part there is exactly zero and every first-order coherent
  error leaves it zero, but incoherent noise acting on circuits that differ in their rotation angles
  does not: the calibration model reads +0.014 at t = 0 against +0.016 at |t| = 0.05. Each case
  therefore measures D(t) = odd(t) - odd(0).

Variants, by the case directory's name:

- signed-kernel-null-retest: |t| = 0.25 and t = 0, two +, -, -, + blocks each, 20000 shots, plus a
  calibration job (QB7 readout, prx trains on QB6 and QB11, 4000 shots). It asks whether the sign
  Garnet carried at |t| = 0.25 survives the null subtraction and balanced order.
- signed-kernel-weak-resolve: |t| = 0.05 and t = 0 with enough blocks to resolve D(0.05) at
  Z_RESOLVE standard errors for the measured visibility, split into jobs of at most 100 circuits.

Preregistered decisions (Z_RESOLVE standard errors): at each nonzero |t|, D(t) resolves the sign when
it lies Z_RESOLVE above zero and falsifies the signed law when it lies Z_RESOLVE below; within that,
D(t) is unresolved. The null odd part is reported with its significance and decides nothing.

Usage: "$PYTHON" scripts/iqm_signed_resolve.py (build DIR [--live] | check DIR | analyze RUN_DIR... --out FILE
       [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_cancellation_probe import decide, exact_z, fetch_calibration, measure, prx, read, train, z_of  # noqa: E402
from iqm_jobs import CASE_SCHEMA, ceiling_credits, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import target_of, to_iqm  # noqa: E402

import signed_kernel_probe as skp  # noqa: E402
from parallel import ordered_map  # noqa: E402

QC = "garnet"
QCS = ["garnet:mock", "garnet"]
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
# The retained probe's compile: transpiler seed 2 of the matched probe on Garnet's couplers (199 CZ).
SEED = 2
OPTIONS: dict[str, Any] = {"heralding_mode": "zeros", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
PROBE_SHOTS = 20000
CALIBRATION_SHOTS = 4000
MAX_CIRCUITS = 100
# The two heralded Garnet probe jobs differ by 31 us per requested shot; this bounds the schedule.
SHOT_SECONDS = 0.000031
# Measured on the retained probe: heralding kept 55.9 % of shots and the pooled visibility was 0.206.
RETENTION = 0.559
VISIBILITY = 0.206
Z_RESOLVE = 3.0
# QB11's over-rotation the retained even offsets imply once the visibility damps them, used for the
# coherent-augmented prediction (docs/design/iqm-garnet-signed-kernel-probe.md, adversarial audit).
COHERENT = {"QB11": 0.027}
CONTROL = "QB7"
TRAIN_QUBITS = ("QB6", "QB11")
AMPLIFY_K = (0, 1, 2, 3)
VARIANTS: dict[str, dict[str, Any]] = {
    "signed-kernel-null-retest": {"t": 0.25, "blocks": 2},
    "signed-kernel-weak-resolve": {"t": 0.05, "blocks": None},
}


def law(t: float) -> float:
    return t / (2 + abs(t))


def blocks_to_resolve(t: float) -> int:
    """+, -, -, + blocks per arm for D(t) at Z_RESOLVE standard errors at VISIBILITY and RETENTION.

    With k kept shots per sign at t and at 0, se(D) = 1/sqrt(k), so k = (Z_RESOLVE / (V law(t)))^2.
    """
    kept = (Z_RESOLVE / (VISIBILITY * law(t))) ** 2
    return math.ceil(kept / (RETENTION * PROBE_SHOTS) / 2)


def compile_probe(calibration_dir: Path) -> QuantumCircuit:
    _, coupling = target_of(iqm_sim.Calibration.from_directory(calibration_dir))
    return transpile(
        skp.matched_signed_probe(),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=3,
        seed_transpiler=SEED,
    )


def bind(compiled: QuantumCircuit, t: float, negative: bool) -> QuantumCircuit:
    values = skp.matched_values(abs(t))
    values[skp.SIGN_PHASE] = math.pi if negative else 0.0
    return compiled.assign_parameters(values)


def arm_name(t: float, negative: bool, block: int, slot: str) -> str:
    return f"t{'-' if negative else '+'}{abs(t):.2f}-{block:02d}{slot}"


def arms(t: float, blocks: int) -> list[tuple[str, float, bool]]:
    """Blocks of +, -, -, + at |t| and at 0, interleaved block by block."""
    out = []
    for block in range(blocks):
        for size in (t, 0.0):
            for slot, negative in (("a", False), ("b", True), ("c", True), ("d", False)):
                out.append((arm_name(size, negative, block, slot), size, negative))
    return out


def predict(item: tuple[float, bool, str, dict[str, float]]) -> float:
    """<Z> of QB7 as read, exact under the calibration's gate noise, ALAP idle relaxation and
    herald-conditioned readout, with optional relative over-rotations (iqm_cancellation_probe.exact_z)."""
    t, negative, calibration_dir, over = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    circuit = to_iqm(bind(compile_probe(Path(calibration_dir)), t, negative), "arm", calibration.qubits)
    return read(exact_z((circuit, calibration_dir, over)), *calibration.readout(CONTROL, heralded=True))


def split(names: list[str]) -> list[list[str]]:
    """Consecutive runs of at most MAX_CIRCUITS circuits, each a whole number of blocks of eight."""
    per_job = MAX_CIRCUITS // 8 * 8
    return [names[i : i + per_job] for i in range(0, len(names), per_job)]


def build_from(calibration_dir: Path, case: str) -> tuple[dict[str, str], dict[str, Any]]:
    variant = VARIANTS[case]
    t = variant["t"]
    blocks = variant["blocks"] or blocks_to_resolve(t)
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    compiled = compile_probe(calibration_dir)
    files: dict[str, str] = {}
    probe = arms(t, blocks)
    for name, size, negative in probe:
        files[f"circuits/{name}.json"] = dump(to_iqm(bind(compiled, size, negative), name, calibration.qubits))
    calibrate = [("ro0", [measure(CONTROL)]), ("ro1", [prx(CONTROL, math.pi), measure(CONTROL)])]
    calibrate += [(f"amp-{q}-{k}", train(q, k)) for q in TRAIN_QUBITS for k in AMPLIFY_K]
    for name, instructions in calibrate:
        files[f"circuits/{name}.json"] = dump({"name": name, "instructions": instructions})
    jobs: list[dict[str, Any]] = []
    groups = [(f"probe-{n}", group, PROBE_SHOTS) for n, group in enumerate(split([n for n, _, _ in probe]))]
    groups.append(("calibrate", [n for n, _ in calibrate], CALIBRATION_SHOTS))
    for job, names, shots in groups:
        expected = round(len(names) * shots * SHOT_SECONDS, 3)
        jobs.append(
            {
                "job": job,
                "circuits": [
                    {"file": f"circuits/{n}.json", "sha256": sha256(files[f"circuits/{n}.json"].encode())}
                    for n in names
                ],
                "shots": shots,
                "options": {**OPTIONS, "calibration_set_id": {QC: calibration.set_id}},
                "expected_seconds": expected,
                "max_credits": {qc: ceiling_credits(expected, price) for qc, price in PRICE.items()},
            }
        )
    points = [(size, negative) for size in (t, 0.0) for negative in (False, True)]
    models = {"calibration": {}, "coherent": COHERENT}
    z: dict[str, dict[str, float]] = {}
    for label, over in models.items():
        values = ordered_map(predict, [(size, negative, str(calibration_dir), over) for size, negative in points])
        z[label] = {
            f"{'-' if negative else '+'}{size:.2f}": value
            for (size, negative), value in zip(points, values, strict=True)
        }
    predicted: dict[str, dict[str, float]] = {}
    for label, readings in z.items():
        odd_t = (readings[f"+{t:.2f}"] - readings[f"-{t:.2f}"]) / 2
        odd_0 = (readings["+0.00"] - readings["-0.00"]) / 2
        predicted[label] = {"odd_t": odd_t, "odd_0": odd_0, "d_t": odd_t - odd_0}
    kept = RETENTION * PROBE_SHOTS * 2 * blocks
    credits = sum(job["max_credits"][QC] for job in jobs)
    prediction = {
        "calibration_set": calibration.set_id,
        "seed": SEED,
        "cz": compiled.count_ops().get("cz", 0),
        "t": t,
        "blocks": blocks,
        "z": z,
        "parts": predicted,
        "planning": {
            "visibility": VISIBILITY,
            "retention": RETENTION,
            "expected_d_t": VISIBILITY * law(t),
            "se_d_t": 1 / math.sqrt(kept),
            "expected_z": VISIBILITY * law(t) * math.sqrt(kept),
            "ceiling_credits_garnet": credits,
        },
        "model": (
            "iqm_sim depolarizing PRX and CZ, herald-conditioned readout, ALAP idle T1/T2, exact density matrix; "
            "coherent adds relative over-rotations"
        ),
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": case,
            "question": (
                f"Does Garnet's odd part of the signed kernel probe at |t| = {t} exceed its t = 0 null offset, "
                "D(t) = odd(t) - odd(0) > 0, with the +t and -t circuits in balanced order?"
            ),
            "ideal": {f"{size:+.2f}": law(size) for size in (t, -t, 0.0)},
            "qcs": QCS,
            "jobs": jobs,
        }
    )
    files["prediction.json"] = dump(prediction)
    return files, prediction


def write(directory: Path, live: bool = False) -> None:
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        fetch_calibration(calibration_dir)
    else:
        for name in CALIBRATION_FILES:
            shutil.copyfile(iqm_sim.EVIDENCE / QC / "calibration" / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir, directory.name)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({k: prediction[k] for k in ("t", "blocks", "parts", "planning")}, indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration", directory.name)
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration")


def evaluate(counts: dict[str, tuple[int, int]], t: float) -> dict[str, Any]:
    """The odd parts at |t| and 0 pooled over blocks, D(t) and its decision."""
    parts: dict[str, dict[str, Any]] = {}
    for size in (t, 0.0):
        plus = [n for n in counts if n.startswith(f"t+{size:.2f}-")]
        minus = [n for n in counts if n.startswith(f"t-{size:.2f}-")]
        (zp, sp, kp), (zm, sm, km) = z_of(counts, *plus), z_of(counts, *minus)
        parts[f"{size}"] = {"odd": (zp - zm) / 2, "even": (zp + zm) / 2, "se": math.hypot(sp, sm) / 2, "kept": [kp, km]}
    odd_t, odd_0 = parts[f"{t}"], parts["0.0"]
    d = odd_t["odd"] - odd_0["odd"]
    se = math.hypot(odd_t["se"], odd_0["se"])
    return {
        "parts": parts,
        "null_z": odd_0["odd"] / odd_0["se"] if odd_0["se"] > 0 else 0.0,
        "d_t": d,
        "se": se,
        # decide() resolves below zero; the signed law here predicts D(t) > 0, so its sign is turned.
        "decision": decide(-d, se),
        "visibility": d / law(t),
    }


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    import iqm_jobs

    if len({run_dir.resolve() for run_dir in run_dirs}) != len(run_dirs):
        raise ValueError("a run directory is named twice; each acquisition counts once")
    prediction = json.loads((sorted(run_dirs)[0] / "prediction.json").read_text(encoding="utf-8"))
    digests = {sha256((run_dir / "cases.json").read_bytes()) for run_dir in run_dirs}
    if len(digests) != 1:
        raise ValueError(f"the runs copy {len(digests)} different cases.json; one analysis reads one case")
    counts: dict[str, tuple[int, int]] = {}
    runs = []
    for run_dir in sorted(run_dirs):
        facts = iqm_jobs.run_facts(run_dir)
        submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
        if submission["qc"] != QC:
            raise ValueError(f"{run_dir}: ran on {submission['qc']}; the analysis reads {QC} runs only")
        record = json.loads((run_dir / "raw/job.json").read_bytes())
        if record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
            raise ValueError(
                f"{run_dir}: compiled against another set than the predicted {prediction['calibration_set']}"
            )
        case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        row = next(r for r in case["jobs"] if r["job"] == submission["job"])
        names = [Path(entry["file"]).stem for entry in row["circuits"]]
        for name, circuit in zip(names, json.loads((run_dir / "raw/measurements.json").read_bytes()), strict=True):
            bits = [shot[0] for shot in circuit["c"]]
            ones, n = counts.get(name, (0, 0))
            counts[name] = (ones + sum(bits), n + len(bits))
        runs.append({"run": run_dir.name, "job": submission["job"], "charge": facts["charge"]})
    probe = {n: v for n, v in counts.items() if n.startswith("t")}
    return {
        "schema": "iqm-signed-resolve-analysis-v1",
        "runs": runs,
        **evaluate(probe, prediction["t"]),
        "credits_charged": round(sum(r["charge"] for r in runs), 6),
    }


def synthetic(t: float, blocks: int, d: float, null: float, seed: int) -> dict[str, tuple[int, int]]:
    """Kept-shot counts of a device with odd parts null + d at |t| and null at 0, and a drift that adds
    -0.01 per circuit along the list, which the +, -, -, + order cancels."""
    rng = np.random.default_rng(seed)
    kept = round(RETENTION * PROBE_SHOTS)
    counts = {}
    for position, (name, size, negative) in enumerate(arms(t, blocks)):
        odd = null + (d if size else 0.0)
        z = (-odd if negative else odd) + 0.02 - 0.01 * position / len(arms(t, blocks))
        counts[name] = (int(rng.binomial(kept, (1 - z) / 2)), kept)
    return counts


def self_test() -> str:
    for case in VARIANTS:
        files, prediction = build_from(iqm_sim.EVIDENCE / QC / "calibration", case)
        if prediction["cz"] != 199:
            raise RuntimeError(f"{case}: the recompile has {prediction['cz']} CZ, not the retained probe's 199")
        jobs = json.loads(files["cases.json"])["jobs"]
        if any(len(job["circuits"]) > MAX_CIRCUITS for job in jobs):
            raise RuntimeError(f"{case}: a job exceeds {MAX_CIRCUITS} circuits")
        names = [Path(c["file"]).stem for job in jobs for c in job["circuits"] if Path(c["file"]).stem.startswith("t")]
        signs = [n[1] for n in names]
        if signs[:8] != ["+", "-", "-", "+"] * 2:
            raise RuntimeError(f"{case}: arms are not listed +, -, -, +")
    t, blocks = VARIANTS["signed-kernel-null-retest"]["t"], 2
    signal = VISIBILITY * law(t)
    honest = evaluate(synthetic(t, blocks, signal, 0.012, 1), t)
    if honest["decision"] != "resolved" or abs(honest["d_t"] - signal) > 4 * honest["se"]:
        raise RuntimeError(f"an honest device reads {honest}")
    artifact = evaluate(synthetic(t, blocks, 0.0, 0.022, 2), t)
    if artifact["decision"] == "resolved":
        raise RuntimeError("an odd part made only of the null offset resolved the sign")
    reversed_ = evaluate(synthetic(t, blocks, -signal, 0.0, 3), t)
    if reversed_["decision"] != "falsified":
        raise RuntimeError(f"a reversed sign reads {reversed_['decision']}")
    return (
        f"signed resolve: both variants 199 CZ in +, -, -, + order; weak resolve needs "
        f"{blocks_to_resolve(VARIANTS['signed-kernel-weak-resolve']['t'])} blocks; an honest device resolves, "
        "a null-only odd part does not, a reversed sign falsifies"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--live", action="store_true", help="read Garnet's current calibration (network, read-only)")
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dirs", type=Path, nargs="+")
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.live)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = json.dumps(analyze(args.run_dirs), indent=1, sort_keys=True) + "\n"
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{args.out} differs from the replayed analysis")
            print(f"{args.out}: matches the replayed analysis")
        else:
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out}")
    else:
        parser.error("choose build, check, analyze or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
