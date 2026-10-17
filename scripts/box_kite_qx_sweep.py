"""Exhaustive box-kite family (a) on the qxelarator state-vector emulator, and its offline replay.

The remote QX backend runs the QX simulator, an ideal state-vector emulator,
so a remote run of family (a) adds nothing beyond the platform's compile path,
which the QX smoke set covers; the full family runs here, on qxelarator 0.10.0
(the QX simulator's Python binding) on a Kaggle CPU kernel, under the
repository rule that simulations of 14 qubits or fewer run on Kaggle.

--run OUT regenerates the 848 family (a) circuits in process
(box_kite_cases.series("a", "qx"), the bytes gate core-420 regenerates),
runs each cQASM text through qxelarator.execute_string at QX_SHOTS shots
with seed BASE_SEED + its index in series order, and writes one JSON record:
per circuit its series path, sha256, seed, the selector qubit of each replica
and selector_counts, the histogram of the selector bits (character s of a key
is the selector bit of replica slot s; qxelarator puts qubit 0 at the
rightmost character of its keys), and per replica the census row, its
p_selector_zero, the count of selector-0 shots, z and the verdict. The
program's falsifier decides each verdict: one shot with selector 0 on a
P = 0 replica or selector 1 on a P = 1 replica refutes it, and a P = 1/2
replica with |z| >= Z_LIMIT (Bonferroni over the family's P = 1/2 replicas
at family error 0.01) refutes it. qiskit and qxelarator run in one
interpreter: the Kaggle image's Python 3.13 with the kernel's qiskit 2.5.2
and the qx-emulator pin group, or the Quantum Inspire environment locally.
--limit N keeps the first N replicas of each sub-family.

--replay RECORD re-derives every verdict from the retained counts and the
census alone: census digest, each replica's prediction against its census
row, complete coverage of every sub-family's census rows in series order,
seeds, shot totals, selector-0 counts, z, verdicts and the summary. --bind
also regenerates the circuits and requires each sha256 and selector list to
equal the record's, which binds the record to this checkout's generator.
--require-pass fails when any replica is refuted.

--emulate CASE_DIR... runs every circuit of the given case directories on
qxelarator at its manifest's shots (seed BASE_SEED + its index) and applies
the same falsifier to every replica check box_kite_cases.replica_checks
derives (selector and control marginals, the coherence settings' conditional
data marginals), and to the readout pair (readout-0 all zero, readout-1 all
one); this is the local run of the identical Tuna-17 bytes before a batch.

--self-test builds a synthetic complete record from the census, requires the
replay to accept it, and requires mutated counts, seeds, predictions,
coverage and digests to be rejected.

Usage: "$PYTHON" scripts/box_kite_qx_sweep.py --run OUT [--limit N]
       "$PYTHON" scripts/box_kite_qx_sweep.py --replay RECORD [--bind] [--require-pass]
       "$PYTHON" scripts/box_kite_qx_sweep.py --emulate CASE_DIR... [--out FILE]
       "$PYTHON" scripts/box_kite_qx_sweep.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import sys
import warnings
from fractions import Fraction
from pathlib import Path
from typing import Any

# qxelarator 0.10.0 is a SWIG 4.3 module whose builtin types lack __module__;
# Python 3.13 reports that as a DeprecationWarning at import and again during
# interpreter shutdown, where -W error turns it into a crash.
warnings.filterwarnings(
    "ignore",
    message=r"builtin type (SwigPyPacked|SwigPyObject|swigvarlink) has no __module__ attribute",
    category=DeprecationWarning,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import box_kite_cases as cases  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "box-kite-qx-sweep-v1"
EMULATE_SCHEMA = "box-kite-qx-emulation-v1"
QXELARATOR = "0.10.0"
BASE_SEED = 20261017
SHOTS = cases.QX_SHOTS
Z_LIMIT = cases.Z_LIMIT
FALSIFIER = (
    "one shot with selector 0 on a P = 0 replica or selector 1 on a P = 1 replica refutes it; a P = 1/2 "
    f"replica with |z| >= {Z_LIMIT}, z = (zeros - n/2) / sqrt(n/4), refutes it"
)


def verdict(p: str, zeros: int, shots: int) -> tuple[str, float | None]:
    """The falsifier on k selector-0 shots of n: deterministic rows exactly, others by binomial z."""
    prob = Fraction(p)
    if prob in (0, 1):
        return ("pass" if zeros == prob * shots else "refuted"), None
    if shots == 0:
        return "refuted", None
    z = round((zeros - shots * float(prob)) / math.sqrt(shots * float(prob) * (1 - float(prob))), 6)
    return ("pass" if abs(z) < Z_LIMIT else "refuted"), z


def slot_zeros(histogram: dict[str, int], slot: int) -> int:
    return sum(count for key, count in histogram.items() if key[slot] == "0")


def family_circuits(limit: int | None) -> list[dict[str, Any]]:
    """Series path, sub-family, text and replicas (census id, prediction, selector) of every family (a) circuit."""
    files = cases.series("a", "qx", limit=limit)
    out = []
    for batch in json.loads(files["cases.json"])["batches"]:
        manifest = json.loads(files[f"{batch['batch']}/cases.json"])
        for row in manifest["circuits"]:
            path = f"{batch['batch']}/{row['file']}"
            out.append(
                {
                    "file": path,
                    "sub_family": row["sub_family"],
                    "text": files[path],
                    "replicas": [
                        {"slot": r["slot"], "census": r["census"], "p_selector_zero": r["p_selector_zero"],
                         "selector": r["roles"]["selector"]}
                        for r in row["replicas"]
                    ],
                }
            )  # fmt: skip
    return out


def emulate(item: tuple[str, int, int]) -> dict[str, int]:
    """Pool worker: qxelarator's outcome histogram of one cQASM text (qubit 0 at the rightmost character)."""
    import qxelarator

    text, shots, seed = item
    result = qxelarator.execute_string(text, iterations=shots, seed=seed)
    if isinstance(result, qxelarator.SimulationError) or result.shots_done != shots:
        raise RuntimeError(f"qxelarator: {result}")
    return {str(key): int(value) for key, value in result.results.items()}


def bit(key: str, qubit: int) -> str:
    return key[len(key) - 1 - qubit]


def selector_histogram(outcomes: dict[str, int], selectors: list[int]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for key, count in sorted(outcomes.items()):
        reduced = "".join(bit(key, q) for q in selectors)
        histogram[reduced] = histogram.get(reduced, 0) + count
    return dict(sorted(histogram.items()))


def judge(circuit: dict[str, Any], shots: int) -> dict[str, Any]:
    """Selector-0 counts, z and verdicts of one circuit's replicas from its selector_counts."""
    replicas = []
    for replica in circuit["replicas"]:
        zeros = slot_zeros(circuit["selector_counts"], replica["slot"])
        result, z = verdict(replica["p_selector_zero"], zeros, shots)
        replicas.append({**replica, "selector_zeros": zeros, "z": z, "verdict": result})
    passed = all(r["verdict"] == "pass" for r in replicas)
    return {**circuit, "replicas": replicas, "verdict": "pass" if passed else "refuted"}


def summarize(circuits: list[dict[str, Any]]) -> dict[str, Any]:
    replicas = [r for c in circuits for r in c["replicas"]]
    refuted = [f"{c['file']} slot {r['slot']}" for c in circuits for r in c["replicas"] if r["verdict"] != "pass"]
    return {
        "circuits": len(circuits),
        "replicas": len(replicas),
        "half_replicas": sum(Fraction(r["p_selector_zero"]) == Fraction(1, 2) for r in replicas),
        "max_abs_z": max((abs(r["z"]) for r in replicas if r["z"] is not None), default=None),
        "refuted": refuted,
        "verdict": "pass" if not refuted else "refuted",
    }


def run(out: Path, limit: int | None) -> dict[str, Any]:
    from importlib import metadata

    circuits = family_circuits(limit)
    seeds = [BASE_SEED + index for index in range(len(circuits))]
    outcomes = parallel.ordered_map(emulate, [(c["text"], SHOTS, s) for c, s in zip(circuits, seeds, strict=True)])
    judged = []
    for circuit, seed, result in zip(circuits, seeds, outcomes, strict=True):
        selectors = [r["selector"] for r in circuit["replicas"]]
        row = {
            "file": circuit["file"],
            "sub_family": circuit["sub_family"],
            "sha256": hashlib.sha256(circuit["text"].encode()).hexdigest(),
            "seed": seed,
            "selectors": selectors,
            "selector_counts": selector_histogram(result, selectors),
            "replicas": circuit["replicas"],
        }
        judged.append(judge(row, SHOTS))
    census = cases.load_census()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "family": "a",
        "generator": "scripts/box_kite_cases.py series('a', 'qx')",
        "census": cases.census_record(cases.CENSUS, census),
        "emulator": {"package": "qxelarator", "version": metadata.version("qxelarator")},
        "environment": {
            "python": platform.python_version(),
            "qiskit": metadata.version("qiskit"),
            "numpy": metadata.version("numpy"),
            "workers": parallel.workers(),
        },
        "shots": SHOTS,
        "base_seed": BASE_SEED,
        "seed_rule": "seed = base_seed + the circuit's index in series order",
        "limit": limit,
        "z_limit": Z_LIMIT,
        "falsifier": FALSIFIER,
        "counts_key": "character s of a selector_counts key is the selector bit of replica slot s",
        "circuits": judged,
        "summary": summarize(judged),
    }
    if record["emulator"]["version"] != QXELARATOR:
        raise SystemExit(f"qxelarator {record['emulator']['version']} is installed; the sweep pins {QXELARATOR}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def expected_coverage(rows: dict[str, list[cases.Row]], limit: int | None) -> dict[str, list[str]]:
    out = {}
    for sub_family, sources, _ in cases.SUB_FAMILIES:
        ids = [f"{source}[{row['index']}]" for source in sources for row in rows[source]]
        out[sub_family] = ids if limit is None else ids[:limit]
    return out


def replay(record: dict[str, Any], bind: bool = False) -> dict[str, Any]:
    """Every verdict of a sweep record re-derived from its counts and the census; raises on a difference."""
    if record.get("schema") != SCHEMA:
        raise ValueError(f"record schema {record.get('schema')!r}, expected {SCHEMA}")
    census_path = ROOT / record["census"]["path"]
    if hashlib.sha256(census_path.read_bytes()).hexdigest() != record["census"]["sha256"]:
        raise ValueError(f"{record['census']['path']} differs from the census the sweep ran against")
    rows = cases.validate_census(cases.load_census(census_path))
    by_id = {f"{source}[{row['index']}]": row for source, source_rows in rows.items() for row in source_rows}
    shots, limit = record["shots"], record["limit"]
    if (shots, record["z_limit"], record["base_seed"]) != (SHOTS, Z_LIMIT, BASE_SEED):
        raise ValueError("record shots, z_limit or base seed differ from the sweep's")
    covered: dict[str, list[str]] = {}
    for index, circuit in enumerate(record["circuits"]):
        name = circuit["file"]
        if circuit["seed"] != BASE_SEED + index:
            raise ValueError(f"{name}: seed {circuit['seed']} breaks the seed rule")
        histogram = circuit["selector_counts"]
        width = len(circuit["replicas"])
        if sum(histogram.values()) != shots or any(
            len(key) != width or set(key) - {"0", "1"} or type(count) is not int or count < 0
            for key, count in histogram.items()
        ):
            raise ValueError(f"{name}: selector_counts do not hold {shots} shots over {width} selector bits")
        if [r["selector"] for r in circuit["replicas"]] != circuit["selectors"] or len(
            set(circuit["selectors"])
        ) != width:
            raise ValueError(f"{name}: replica selectors differ from the circuit's distinct selector list")
        for slot, replica in enumerate(circuit["replicas"]):
            row = by_id.get(replica["census"])
            if replica["slot"] != slot or row is None or row["p_selector_zero"] != replica["p_selector_zero"]:
                raise ValueError(f"{name} slot {slot}: prediction differs from census {replica['census']}")
            covered.setdefault(circuit["sub_family"], []).append(replica["census"])
        rejudged = judge({k: v for k, v in circuit.items() if k != "verdict"}, shots)
        if rejudged != circuit:
            raise ValueError(f"{name}: recorded selector-0 counts, z or verdicts differ from the counts")
    if covered != expected_coverage(rows, limit):
        raise ValueError("record replicas do not cover each sub-family's census rows once, in series order")
    if summarize(record["circuits"]) != record["summary"]:
        raise ValueError("record summary differs from its circuits")
    if bind:
        regenerated = family_circuits(limit)
        if [c["file"] for c in regenerated] != [c["file"] for c in record["circuits"]]:
            raise ValueError("regenerated circuit files differ from the record")
        for new, old in zip(regenerated, record["circuits"], strict=True):
            if hashlib.sha256(new["text"].encode()).hexdigest() != old["sha256"]:
                raise ValueError(f"{old['file']}: regenerated bytes differ from the swept circuit")
            if [r["selector"] for r in new["replicas"]] != old["selectors"]:
                raise ValueError(f"{old['file']}: regenerated selectors differ from the record")
    return record["summary"]


def measured(text: str) -> str:
    """A Ry program with a bit register and a final measure, which qxelarator needs to record outcomes.

    The Ry emulator measures every atom at the end of a program that carries
    neither; qxelarator records nothing without them.
    """
    lines = text.splitlines()
    width = next(int(line[6:-3]) for line in lines if line.startswith("qubit[") and line.endswith("] q"))
    at = next(n for n, line in enumerate(lines) if line.startswith("qubit["))
    return "\n".join([*lines[: at + 1], f"bit[{width}] b", *lines[at + 1 :], "", "b = measure q", ""])


def emulate_cases(directories: list[Path]) -> dict[str, Any]:
    """qxelarator runs of retained case circuits, judged replica by replica, and of their readout pairs."""
    jobs = []
    for directory in directories:
        for manifest_path in sorted(directory.rglob("cases.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest.get("circuits"), list):
                continue
            for row in manifest["circuits"]:
                text = (manifest_path.parent / row["file"]).read_text(encoding="utf-8")
                path = (manifest_path.parent / row["file"]).relative_to(ROOT).as_posix()
                if manifest.get("dialect") == "ry":
                    text = measured(text)
                jobs.append((path, row, text, manifest["shots"]))
    outcomes = parallel.ordered_map(
        emulate, [(text, shots, BASE_SEED + n) for n, (_, _, text, shots) in enumerate(jobs)]
    )
    results = []
    for (path, row, _, shots), outcome in zip(jobs, outcomes, strict=True):
        checks: list[dict[str, Any]] = []
        if "expected_leftmost" in row:
            leftmost = {key[::-1]: count for key, count in outcome.items()}
            stray = sum(count for key, count in leftmost.items() if key not in row["expected_leftmost"])
            checks.append(
                {"check": "no outcome of probability 0", "zeros": stray, "verdict": "pass" if not stray else "refuted"}
            )
            for key, want in row["expected_leftmost"].items():
                result, z = verdict(want, leftmost.get(key, 0), shots)
                checks.append({"check": f"outcome {key}", "prediction": want, "z": z, "verdict": result})
        if row["kind"] == "readout":
            want = "0" if row["file"] == "readout-0.cq" else "1"
            ok = all(set(key) == {want} for key in outcome)
            checks.append({"check": f"readout all {want}", "verdict": "pass" if ok else "refuted"})
        for replica in row.get("replicas", []):
            for kind, qubits, want in cases.replica_checks(replica):
                if kind == "cz_count":
                    continue
                if kind == "p_zero":
                    n, k = shots, sum(c for key, c in outcome.items() if bit(key, qubits[0]) == "0")
                else:
                    post = {key: c for key, c in outcome.items() if bit(key, qubits[0]) == "0"}
                    n, k = sum(post.values()), sum(c for key, c in post.items() if bit(key, qubits[1]) == "0")
                result, z = verdict(want, k, n)
                checks.append(
                    {"slot": replica["slot"], "check": kind, "qubits": list(qubits), "prediction": want,
                     "zeros": k, "shots": n, "z": z, "verdict": result}
                )  # fmt: skip
        results.append({"file": path, "shots": shots, "checks": checks})
    refuted = [r["file"] for r in results if any(c["verdict"] != "pass" for c in r["checks"])]
    return {
        "schema": EMULATE_SCHEMA,
        "emulator": "qxelarator",
        "base_seed": BASE_SEED,
        "circuits": results,
        "refuted": refuted,
        "verdict": "pass" if not refuted else "refuted",
    }


# ---------------------------------------------------------------- self-test


def synthetic_record() -> dict[str, Any]:
    """A complete record whose counts follow the census predictions, packed as series('a', 'qx') packs."""
    census = cases.load_census()
    rows = cases.validate_census(census)
    circuits: list[dict[str, Any]] = []
    batch = 0
    for sub_family, sources, encoding in cases.SUB_FAMILIES:
        members = [(encoding, row) for source in sources for row in rows[source]]
        for number, group in enumerate(cases.pack(members, cases.WIDTH[encoding]), start=1):
            replicas = [
                {"slot": slot, "census": f"{row['source']}[{row['index']}]", "p_selector_zero": row["p_selector_zero"],
                 "selector": cases.replica_roles(enc, place)["selector"]}
                for slot, ((enc, row), place) in enumerate(group)
            ]  # fmt: skip
            # Shot s reads selector 0 on slot r while s < zeros(r); P = 1/2 replicas read 1000 + 7 r zeros.
            zeros = [{"0": 0, "1": SHOTS}.get(r["p_selector_zero"], 1000 + 7 * r["slot"]) for r in replicas]
            histogram: dict[str, int] = {}
            for shot in range(SHOTS):
                key = "".join("0" if shot < z else "1" for z in zeros)
                histogram[key] = histogram.get(key, 0) + 1
            row = {
                "file": f"batch-{batch:03d}/{sub_family}-{number:03d}.cq",
                "sub_family": sub_family,
                "sha256": hashlib.sha256(f"{sub_family}-{number}".encode()).hexdigest(),
                "seed": BASE_SEED + len(circuits),
                "selectors": [r["selector"] for r in replicas],
                "selector_counts": dict(sorted(histogram.items())),
                "replicas": replicas,
            }
            circuits.append(judge(row, SHOTS))
            batch += 1
    return {
        "schema": SCHEMA,
        "family": "a",
        "census": cases.census_record(cases.CENSUS, census),
        "shots": SHOTS,
        "base_seed": BASE_SEED,
        "limit": None,
        "z_limit": Z_LIMIT,
        "circuits": circuits,
        "summary": summarize(circuits),
    }


def self_test() -> None:
    record = synthetic_record()
    summary = replay(record)
    if summary["verdict"] != "pass" or summary["circuits"] != 848:
        raise AssertionError(f"the synthetic record replays as {summary}")
    rejected = 0

    def reject(label: str, mutate: Any) -> None:
        nonlocal rejected
        mutated = copy.deepcopy(record)
        mutate(mutated)
        try:
            replay(mutated)
        except ValueError:
            rejected += 1
            return
        raise AssertionError(f"{label} was accepted")

    dark = next(
        (n, s)
        for n, c in enumerate(record["circuits"])
        for s, r in enumerate(c["replicas"])
        if r["p_selector_zero"] == "0"
    )
    half = next(
        (n, s)
        for n, c in enumerate(record["circuits"])
        for s, r in enumerate(c["replicas"])
        if r["p_selector_zero"] == "1/2"
    )

    def move_shot(record_: dict[str, Any], position: tuple[int, int], to: str) -> None:
        """Move one shot of the circuit to a key whose bit at the replica's slot reads `to`."""
        circuit = record_["circuits"][position[0]]
        source = next(k for k in sorted(circuit["selector_counts"]) if k[position[1]] != to)
        target = source[: position[1]] + to + source[position[1] + 1 :]
        circuit["selector_counts"][source] -= 1
        circuit["selector_counts"][target] = circuit["selector_counts"].get(target, 0) + 1
        circuit["selector_counts"] = {k: v for k, v in sorted(circuit["selector_counts"].items()) if v}

    reject("one selector-0 shot on a P = 0 replica", lambda r: move_shot(r, dark, "0"))

    def skew(record_: dict[str, Any]) -> None:
        for _ in range(200):
            move_shot(record_, half, "0")

    reject("a P = 1/2 replica pushed past the z limit", skew)
    reject(
        "a lost shot",
        lambda r: r["circuits"][0]["selector_counts"].update(
            {"11": r["circuits"][0]["selector_counts"].get("11", 0) - 1}
        ),
    )
    reject("a broken seed", lambda r: r["circuits"][3].update({"seed": BASE_SEED}))
    reject(
        "a changed prediction", lambda r: r["circuits"][dark[0]]["replicas"][dark[1]].update({"p_selector_zero": "1"})
    )
    reject("a dropped circuit", lambda r: (r["circuits"].pop(), r.update({"summary": summarize(r["circuits"])})))
    reject("a changed census digest", lambda r: r["census"].update({"sha256": "0" * 64}))
    reject("an edited summary", lambda r: r["summary"].update({"verdict": "refuted"}))

    # An honest record of a refutation replays and reports the refuted replica.
    honest = copy.deepcopy(record)
    move_shot(honest, dark, "0")
    honest["circuits"][dark[0]] = judge({k: v for k, v in honest["circuits"][dark[0]].items() if k != "verdict"}, SHOTS)
    honest["summary"] = summarize(honest["circuits"])
    if replay(honest)["verdict"] != "refuted":
        raise AssertionError("an honest refuted record replays as passing")
    for p, zeros, want in (("0", 0, "pass"), ("0", 1, "refuted"), ("1", SHOTS, "pass"), ("1/2", 1024, "pass")):
        if verdict(p, zeros, SHOTS)[0] != want:
            raise AssertionError(f"verdict({p}, {zeros}) is not {want}")
    edge = round(SHOTS / 2 + Z_LIMIT * math.sqrt(SHOTS / 4))
    if verdict("1/2", edge, SHOTS)[0] != "refuted" or verdict("1/2", edge - 2, SHOTS)[0] != "pass":
        raise AssertionError("the z limit does not separate the P = 1/2 verdicts")
    print(f"box-kite QX sweep: synthetic 848-circuit record replays; {rejected} mutations rejected")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", type=Path, metavar="OUT")
    mode.add_argument("--replay", type=Path, metavar="RECORD")
    mode.add_argument("--emulate", type=Path, nargs="+", metavar="CASE_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--limit", type=int, help="with --run: the first N replicas of each sub-family")
    parser.add_argument("--bind", action="store_true", help="with --replay: regenerate and compare circuit bytes")
    parser.add_argument("--require-pass", action="store_true", help="with --replay: fail on a refuted replica")
    parser.add_argument("--out", type=Path, help="with --emulate: write the emulation record here")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.run:
        summary = run(args.run, args.limit)["summary"]
        print(
            f"box-kite QX sweep: {summary['circuits']} circuits, {summary['replicas']} replicas, {summary['verdict']}"
        )
        return 0 if summary["verdict"] == "pass" else 1
    if args.emulate:
        record = emulate_cases([path.resolve() for path in args.emulate])
        text = json.dumps(record, indent=1) + "\n"
        if args.out:
            args.out.write_text(text, encoding="utf-8")
        checks = sum(len(c["checks"]) for c in record["circuits"])
        print(f"box-kite emulation: {len(record['circuits'])} circuits, {checks} checks, {record['verdict']}")
        for file in record["refuted"]:
            print(f"refuted: {file}")
        return 0 if record["verdict"] == "pass" else 1
    try:
        summary = replay(json.loads(args.replay.read_text(encoding="utf-8")), bind=args.bind)
    except ValueError as error:
        raise SystemExit(f"{args.replay}: {error}") from error
    print(
        f"box-kite QX sweep replay: {summary['circuits']} circuits, {summary['replicas']} replicas, "
        f"max |z| {summary['max_abs_z']}, {summary['verdict']}"
    )
    return 1 if args.require_pass and summary["verdict"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
