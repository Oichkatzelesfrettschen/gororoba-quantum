"""Kernel cancellation probe on Tuna-17: the zero-divisor sign on Tuna's pi/36 rotation grid, and its QX twin.

gororoba_quantum/kernel_cancellation.py reads <Z> of a control qubit as cos(2 theta) for the certified
sedenion kernel vector u = (e4 - e15)/sqrt2 of L(e1 + e10) (the eigenvalue -1 of L_e1^T L_e10) and as 1
for the bright vector (e4 + e15)/sqrt2, with theta = pi/4 + phi the selector angle between e1 and e10.
Garnet resolved the sign at phi = 0.1 and 0.3 (docs/design/iqm-garnet-kernel-cancellation-probe.md).

Tuna rounds every single-qubit rotation angle to the nearest multiple of pi/36 (docs/notes/quantum_inspire/
backends.md), so this case sets phi on that grid: phi = pi/36 and pi/12, where the selector rotation
RY(pi/2 + 2 phi) is 20 and 24 grid steps and the kernel reads -sin(pi/18) = -0.174 and -sin(pi/6) = -0.5.
Every other rotation of the circuit is a Clifford+T phase, a multiple of pi/4 = 9 grid steps. The
parametrized circuit compiles once onto a five-qubit region of Tuna-17 (basis cz, rz, sx, x; the region
and transpiler seed with the fewest CZ, avoiding the excluded qubits of qi_zero_divisor_cases), every arm
binds that one compile, and the build refuses an emitted angle off the grid by more than ANGLE_TOLERANCE,
so the device runs exactly the compiled circuit.

A hardware batch holds at most three circuits and a batch boundary is a calibration boundary, so each
contrast runs over two consecutive batches, (+phi, -phi, readout-0) then (-phi, +phi, readout-1): the
arms run +, -, -, + across the pair and the pair measures the control's readout assignment.

| batches | contrast |
|---|---|
| 00, 01 | kernel, phi = pi/36 |
| 02, 03 | kernel, phi = pi/12 |
| 04, 05 | bright, phi = pi/36 |

Preregistered decisions (Z_RESOLVE standard errors, odd part (Z(+phi) - Z(-phi))/2 of the control, pooled
over its two batches):
- H1 zero-divisor sign: at each phi the kernel odd part resolves the sign when it lies Z_RESOLVE below
  zero and falsifies the cancellation law when it lies Z_RESOLVE above.
- H2 bright control: a bright odd part Z_RESOLVE standard errors from zero marks a circuit artifact.
- H3 sine law: the contrast odd(pi/12) - (sin(pi/6)/sin(pi/18)) odd(pi/36) lies Z_RESOLVE standard errors
  from zero.

The QX twin runs the same compiled arms, each on register qubits 0-4, as one series of the same six
batches on the ideal emulator: it checks the platform's handling of the emitted cQASM and must read each
arm's ideal <Z> within its shot error.

Usage: "$PYTHON" scripts/qi_cancellation_cases.py (--write DIR | --check DIR | --analyze RUN_DIR... --out FILE
       [--replay] | --self-test)
--write DIR writes DIR/kernel_cancellation_tuna_17/ and DIR/kernel_cancellation_qx/, each a series of batch-NN/
cases under a series cases.json; --check DIR regenerates both and compares bytes and file sets. Bit strings
put qubit 0 at the rightmost character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_zero_divisor_cases as zd  # noqa: E402

import kernel_cancellation as kc  # noqa: E402
from parallel import ordered_map  # noqa: E402

TUNA_SERIES = "kernel_cancellation_tuna_17"
QX_SERIES = "kernel_cancellation_qx"
NQUBITS = 17
SHOTS = 16384
QX_QUBITS = 10
QX_SHOTS = 2048
SEEDS = range(16)
BASIS = ["cz", "rz", "sx", "x"]
GRID = math.pi / 36
ANGLE_TOLERANCE = 1e-9
PHI = {"pi/36": math.pi / 36, "pi/12": math.pi / 12}
Z_RESOLVE = 3.0
CONTROL = 4
# (batch, contrast label, bright, phi label, list of (slot, sign)) and the readout circuit closing it.
BATCHES = (
    ("batch-00", "kernel pi/36", False, "pi/36", (+1, -1), "readout-0"),
    ("batch-01", "kernel pi/36", False, "pi/36", (-1, +1), "readout-1"),
    ("batch-02", "kernel pi/12", False, "pi/12", (+1, -1), "readout-0"),
    ("batch-03", "kernel pi/12", False, "pi/12", (-1, +1), "readout-1"),
    ("batch-04", "bright pi/36", True, "pi/36", (+1, -1), "readout-0"),
    ("batch-05", "bright pi/36", True, "pi/36", (-1, +1), "readout-1"),
)


class Route:
    """One seeded compile of the parametrized probe onto a region; a module-level callable for the pool."""

    def __init__(self, topology: tuple[tuple[int, int], ...]) -> None:
        self.topology = topology

    def __call__(self, item: tuple[tuple[int, ...], int]) -> tuple[int, int, tuple[int, ...], int, Any]:
        from qiskit import transpile
        from qiskit.transpiler import CouplingMap

        region, seed = item
        local = {q: n for n, q in enumerate(region)}
        edges = [[local[a], local[b]] for a, b in self.topology if a in local and b in local]
        coupling = CouplingMap(edges + [[b, a] for a, b in edges])
        probe = kc.cancellation_probe().remove_final_measurements(inplace=False)
        # Level 1 keeps every constant rotation a Clifford+T phase; level 2 resynthesizes two-qubit blocks
        # into generic angles that Tuna would round to its grid.
        compiled = transpile(
            probe, coupling_map=coupling, basis_gates=BASIS, optimization_level=1, seed_transpiler=seed
        )
        off_grid = sum(
            1
            for instruction in compiled.data
            if instruction.operation.name == "rz"
            and not getattr(instruction.operation.params[0], "parameters", None)
            and not on_grid(float(instruction.operation.params[0]))
        )
        return off_grid, compiled.count_ops().get("cz", 0), region, seed, compiled


def compile_probe(topology: tuple[tuple[int, int], ...]) -> tuple[tuple[int, ...], int, Any]:
    """The region and seed with the fewest CZ among compiles whose constant rotations all lie on the grid,
    first in (region, seed) order on a tie; regions and seeds compile independently through the pool."""
    items = [(region, seed) for region in zd.connected_regions(topology, 5) for seed in SEEDS]
    results = [r for r in ordered_map(Route(topology), items) if r[0] == 0]
    if not results:
        raise ValueError("no region and seed compiles onto the pi/36 grid")
    _, cz, region, seed, compiled = min(results, key=lambda r: (r[1], r[2], r[3]))
    return region, seed, compiled


def arm(compiled: Any, phi: float, bright: bool) -> Any:
    """The compile bound at one arm. A compile from a pool worker carries that worker's Parameter objects,
    whose identities differ from this process's, so the values bind by parameter name."""
    by_name = {parameter.name: value for parameter, value in kc.values(phi, bright).items()}
    return compiled.assign_parameters({parameter: by_name[parameter.name] for parameter in compiled.parameters})


def on_grid(angle: float) -> bool:
    steps = angle / GRID
    return abs(steps - round(steps)) * GRID <= ANGLE_TOLERANCE


def control_index(compiled: Any) -> int:
    """Region-local index the logical control (qubit CONTROL) ends on after routing."""
    return int(compiled.layout.final_index_layout()[CONTROL])


def emit(circuit: Any, place: dict[int, int]) -> list[str]:
    """cQASM lines of a bound compile; place maps region-local qubit indices to register indices."""
    lines = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [place[circuit.find_bit(q).index] for q in instruction.qubits]
        if name == "cz":
            lines.append(f"CZ q[{qubits[0]}], q[{qubits[1]}]")
        elif name == "rz":
            angle = float(instruction.operation.params[0])
            if not on_grid(angle):
                raise ValueError(f"Rz({angle}) lies off the pi/36 grid")
            lines.append(f"Rz({angle!r}) q[{qubits[0]}]")
        elif name == "sx":
            lines.append(f"X90 q[{qubits[0]}]")
        elif name == "x":
            lines.append(f"X q[{qubits[0]}]")
        elif name != "barrier":
            raise ValueError(f"{name} is outside the Tuna gate map")
    return lines


def ideal_control_z(bound: Any) -> float:
    from qiskit.quantum_info import Statevector

    probabilities = Statevector(bound).probabilities([control_index(bound)])
    return float(probabilities[0] - probabilities[1])


def readout(nqubits: int, excited: bool) -> str:
    lines = zd.header(nqubits)
    if excited:
        lines += [f"X q[{q}]" for q in range(nqubits)] + [""]
    return "\n".join(lines + ["barrier q", "b = measure q", ""])


def series(
    compiled: Any,
    region: tuple[int, ...],
    seed: int,
    place: dict[int, int],
    backend: dict[str, Any],
    nqubits: int,
    shots: int,
) -> dict[str, str]:
    """batch-NN/ cases of one series and its series cases.json."""
    control = place[control_index(compiled)]
    files: dict[str, str] = {}
    texts: dict[str, str] = {
        "readout-0.cq": readout(nqubits, False),
        "readout-1.cq": readout(nqubits, True),
    }
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "shots": shots,
        "region": list(region),
        "seed": seed,
        "cz": compiled.count_ops().get("cz", 0),
        "control": control,
        "phi": PHI,
        "preregistered": {
            "odd_part": "(Z(+phi) - Z(-phi))/2 of the control, pooled over the contrast's two batches",
            "h1": f"kernel odd part below -{Z_RESOLVE} se resolves the sign, above +{Z_RESOLVE} se falsifies",
            "h2": f"bright odd part beyond {Z_RESOLVE} se from zero marks an artifact",
            "h3": f"odd(pi/12) - (sin(pi/6)/sin(pi/18)) odd(pi/36) beyond {Z_RESOLVE} se from zero",
        },
    }
    batches = []
    for batch, contrast, bright, label, signs, ro in BATCHES:
        rows: list[dict[str, Any]] = []
        for slot, sign in enumerate(signs):
            phi = sign * PHI[label]
            name = f"{'b' if bright else 'k'}{'+' if sign > 0 else '-'}{label.replace('/', '_')}-{batch[-2:]}{slot}.cq"
            bound = arm(compiled, phi, bright)
            ideal = ideal_control_z(bound)
            if abs(ideal - kc.law(phi, bright)) > 1e-9:
                raise ValueError(f"{name}: ideal <Z> {ideal}, not {kc.law(phi, bright)}")
            body = zd.header(nqubits) + [f"// region {list(region)} seed {seed} control q[{control}]"]
            texts[name] = "\n".join(body + emit(bound, place) + ["", "barrier q", "b = measure q", ""])
            rows.append({"file": name, "kind": "arm", "contrast": contrast, "phi": phi, "ideal_z": round(ideal, 12)})
        rows.append({"file": f"{ro}.cq", "kind": "readout"})
        for row in rows:
            row["sha256"] = hashlib.sha256(texts[row["file"]].encode()).hexdigest()
            files[f"{batch}/{row['file']}"] = texts[row["file"]]
        manifest = {"schema": "qi-kernel-cancellation-cases-v1", **common, "batch": batch, "circuits": rows}
        files[f"{batch}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": batch, "files": [row["file"] for row in rows]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-kernel-cancellation-series-v1", "backend": backend["identifier"], "batches": batches},
            indent=1,
        )
        + "\n"
    )
    return files


def build() -> dict[str, dict[str, str]]:
    tuna, qx = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    region, seed, compiled = compile_probe(topology)
    excluded = set(zd.excluded_qubits())
    if set(region) & excluded:
        raise ValueError(f"region {region} uses an excluded qubit of {sorted(excluded)}")
    return {
        TUNA_SERIES: series(compiled, region, seed, dict(enumerate(region)), tuna, NQUBITS, SHOTS),
        QX_SERIES: series(compiled, region, seed, {n: n for n in range(5)}, qx, QX_QUBITS, QX_SHOTS),
    }


def write(directory: Path) -> None:
    for name, files in build().items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path) -> None:
    for name, files in build().items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and not p.name.startswith(".")
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def evaluate(shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, Any]:
    """H1-H3 from per-file shot lists of one series; manifest is any batch's cases.json."""
    control = manifest["control"]

    def z_of(files: list[str]) -> tuple[float, float, int]:
        bits = [bit(s, control) for f in files for s in shots[f]]
        n = len(bits)
        if n == 0:
            return 0.0, math.inf, 0
        z = 1 - 2 * sum(bits) / n
        return z, math.sqrt(max(1 - z * z, 1.0 / n) / n), n

    contrasts: dict[str, dict[str, Any]] = {}
    for label in ("kernel pi/36", "kernel pi/12", "bright pi/36"):
        files = [f for f in shots if f.startswith(("k", "b")) and manifest_contrast(f) == label]
        plus = [f for f in files if f[1] == "+"]
        minus = [f for f in files if f[1] == "-"]
        (zp, sp, np_), (zm, sm, nm) = z_of(plus), z_of(minus)
        contrasts[label] = {
            "z_plus": zp,
            "z_minus": zm,
            "kept": [np_, nm],
            "odd": (zp - zm) / 2,
            "se": math.hypot(sp, sm) / 2,
        }

    def decide(c: dict[str, Any]) -> str:
        r = c["odd"] / c["se"]
        return "resolved" if r <= -Z_RESOLVE else "falsified" if r >= Z_RESOLVE else "unresolved"

    k1, k3, b1 = contrasts["kernel pi/36"], contrasts["kernel pi/12"], contrasts["bright pi/36"]
    sine = math.sin(math.pi / 6) / math.sin(math.pi / 18)
    h3_se = math.hypot(k3["se"], sine * k1["se"])
    h3 = k3["odd"] - sine * k1["odd"]
    ro0, ro1 = z_of([f for f in shots if f == "readout-0.cq"]), z_of([f for f in shots if f == "readout-1.cq"])
    e01, e10 = (1 - ro0[0]) / 2, (1 + ro1[0]) / 2
    falsified = [
        name
        for name, hit in (
            ("H1", "falsified" in (decide(k1), decide(k3))),
            ("H2", abs(b1["odd"] / b1["se"]) >= Z_RESOLVE),
            ("H3", abs(h3 / h3_se) >= Z_RESOLVE),
        )
        if hit
    ]
    return {
        "contrasts": contrasts,
        "h1_zero_divisor_sign": {"pi/36": decide(k1), "pi/12": decide(k3)},
        "h2_bright_z": b1["odd"] / b1["se"],
        "h3_sine_law": {"law": sine, "contrast": h3, "se": h3_se, "z": h3 / h3_se},
        "readout": {"e01": e01, "e10": e10},
        "visibility": k1["odd"] / (-math.sin(math.pi / 18) * (1 - e01 - e10)),
        "falsified_hypotheses": falsified,
    }


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """H1-H3 of one series from its collected batch run directories: every batch of the series once, one
    backend, one shared design; readout shots pool across the batches."""
    shared: dict[str, Any] | None = None
    shots: dict[str, list[str]] = {}
    batches = []
    for run_dir in sorted(run_dirs):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        fields = {k: v for k, v in cases.items() if k not in ("batch", "circuits")}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise ValueError(f"{run_dir}/cases.json describes a different series")
        results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
        if any(job["job"]["status"] != "completed" for job in results["jobs"]):
            raise ValueError(f"{run_dir}: a job did not complete")
        batches.append(cases["batch"])
        for row in cases["circuits"]:
            listed = json.loads((run_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            if row["kind"] == "arm" and row["file"] in shots:
                raise ValueError(f"{run_dir}: arm {row['file']} appears in two batches")
            shots.setdefault(row["file"], []).extend(listed)
    expected = sorted(batch for batch, *_ in BATCHES)
    if sorted(batches) != expected:
        raise ValueError(f"the runs hold batches {sorted(batches)}, not {expected}")
    if shared is None:
        raise ValueError("a series needs its run directories")
    return {
        "schema": "qi-kernel-cancellation-analysis-v1",
        "backend": shared["backend"],
        "batches": len(batches),
        **evaluate(shots, shared),
    }


def manifest_contrast(file: str) -> str:
    return f"{'bright' if file[0] == 'b' else 'kernel'} {file[2:].split('-')[0].replace('_', '/')}"


def self_test() -> str:
    files = build()[TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    arms = [rel for rel in files if rel.endswith(".cq") and "/readout" not in rel]
    if len(arms) != 12 or any(len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) > 3 for n in range(6)):
        raise RuntimeError("the series does not hold twelve arms in six batches of at most three circuits")
    angles = [
        float(line[3:].split(")")[0]) for rel in arms for line in files[rel].splitlines() if line.startswith("Rz(")
    ]
    if not all(on_grid(a) for a in angles):
        raise RuntimeError("an emitted angle lies off the pi/36 grid")
    if on_grid(math.pi / 8) or not on_grid(math.pi / 2 + 2 * math.pi / 36):
        raise RuntimeError("the grid test misreads pi/8 or the pi/36 selector rotation")
    # A model device: ideal <Z> of each arm times visibility V through readout (e01, e10), sampled.
    import numpy as np

    rng = np.random.default_rng(20261023)
    control = manifest["control"]

    def device(v: float, reverse: bool, bright_odd: float) -> dict[str, list[str]]:
        shots: dict[str, list[str]] = {}
        for rel in files:
            if not rel.endswith(".cq"):
                continue
            name = rel.split("/")[1]
            if name.startswith("readout"):
                z = 1.0 if name == "readout-0.cq" else -1.0
            else:
                row = next(
                    r for r in json.loads(files[rel.split("/")[0] + "/cases.json"])["circuits"] if r["file"] == name
                )
                z = v * row["ideal_z"] * (-1 if reverse and name[0] == "k" else 1)
                z += bright_odd * (1 if name[1] == "+" else -1) if name[0] == "b" else 0.0
            p1 = (1 - (0.94 * z + 0.02)) / 2
            ones = rng.binomial(1, p1, SHOTS)
            shots.setdefault(name, [])
            shots[name] += [("1" if o else "0") + "0" * control for o in ones]
        return shots

    honest = evaluate(device(0.3, False, 0.0), manifest)
    if honest["h1_zero_divisor_sign"] != {"pi/36": "resolved", "pi/12": "resolved"} or honest["falsified_hypotheses"]:
        raise RuntimeError(f"an honest device reads {honest}")
    if "H1" not in evaluate(device(0.3, True, 0.0), manifest)["falsified_hypotheses"]:
        raise RuntimeError("a reversed sign left H1 standing")
    if "H2" not in evaluate(device(0.3, False, 0.05), manifest)["falsified_hypotheses"]:
        raise RuntimeError("a bright odd part of 0.05 left H2 standing")
    return (
        f"qi cancellation: region {manifest['region']} seed {manifest['seed']} {manifest['cz']} CZ, control "
        f"q[{control}], {len(angles)} Rz on the pi/36 grid; an honest device resolves H1, a reversed sign "
        "falsifies H1, a bright artifact falsifies H2"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    else:
        if args.out is None:
            parser.error("--analyze needs --out")
        text = json.dumps(analyze(args.analyze), indent=1, sort_keys=True) + "\n"
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{args.out} differs from the replayed analysis")
            print(f"{args.out}: matches the replayed analysis")
        else:
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
