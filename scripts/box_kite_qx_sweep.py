"""Exhaustive box-kite families on the qxelarator state-vector emulator, and their offline replay.

The remote QX backend runs the QX simulator, an ideal state-vector emulator,
so a remote run of an exhaustive family adds nothing beyond the platform's
compile path, which the QX smoke sets cover; the full families run here, on
qxelarator 0.10.0 (the QX simulator's Python binding) on a Kaggle CPU
kernel, under the repository rule that simulations of 14 qubits or fewer run
on Kaggle. Two families exist:

- a: the 848 family (a) circuits of box_kite_cases.series("a", "qx"), the
  zero-product success of every Design B row in both encodings;
- de: the 149 circuits of box_kite_cases.series_de(), the associator-sign
  witnesses (d1)-(d3) and the full-encoding coherence settings (e).

--run DIR [--family a de] regenerates each family's circuits in process
(the bytes gate core-420's generator code emits, the same functions), runs
each cQASM text through qxelarator.execute_string at QX_SHOTS shots with seed
BASE_SEED + its index in series order, and writes DIR/family-<name>.json:
per circuit its series path, sha256, seed, the readout qubits its checks
read and the histogram of those bits (character n of a key is the bit of
readout_qubits[n]; qxelarator puts qubit 0 at the rightmost character of
its own keys), and per replica its census entry, parameters and checks
(box_kite_cases.replica_checks): P(q = 0) of a selector or control, or
P(data parity even | selector = 0) of a coherence setting, each with its
prediction, the counted k of n, z and the verdict. The falsifier of the
program decides each verdict: one shot off a deterministic prediction
refutes it, and any other prediction refutes it at |z| >= Z_LIMIT. qiskit
and qxelarator run in one interpreter: the Kaggle image's Python 3.13 with
the kernel's qiskit 2.5.2 and the qx-emulator pin group, or the Quantum
Inspire environment locally. --limit N keeps the first N replicas of each
sub-family.

--replay RECORD re-derives every verdict from the retained counts and the
census alone: census digest, each replica's census entry, parameters and
predictions against the census in series order (complete coverage of every
sub-family), seeds, shot totals, counts, z, verdicts and the summary. --bind
also regenerates the circuits and requires each sha256 and each replica's
checks, qubits included, to equal the record's, which binds the record to
this checkout's generator and re-checks every prediction by state vector.
--require-pass fails when any check is refuted or the record ran with
--limit, so an evidence replay accepts only the exhaustive family.

--emulate CASE_DIR... runs every circuit of the given case directories on
qxelarator at its manifest's shots (seed BASE_SEED + its index), applies the
same falsifier to every replica check, to each Ry diagnostic's expected
distribution and to the readout pair (readout-0 all zero, readout-1 all
one); this is the local run of the identical Tuna-17 bytes before a batch.

--self-test builds synthetic complete records of both families from the
census, requires the replay to accept them, and requires mutated counts,
seeds, predictions, coverage and digests to be rejected.

Usage: "$PYTHON" scripts/box_kite_qx_sweep.py --run DIR [--family a de] [--limit N]
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
from collections.abc import Callable
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
EMULATOR = {"package": "qxelarator", "version": QXELARATOR}
BASE_SEED = 20261017
SHOTS = cases.QX_SHOTS
Z_LIMIT = cases.Z_LIMIT
FAMILIES = ("a", "de")
PARAMS = ("triple", "omit_last_block", "pair", "i", "pauli")
FALSIFIER = (
    "one shot off a deterministic prediction (P = 0 or 1) refutes the circuit's implementation; any other "
    f"prediction p refutes it at |z| >= {Z_LIMIT}, z = (k - n p) / sqrt(n p (1 - p))"
)
Check = dict[str, Any]


def verdict(p: str, zeros: int, shots: int) -> tuple[str, float | None]:
    """The falsifier on k counted shots of n: deterministic predictions exactly, others by binomial z."""
    prob = Fraction(p)
    if prob in (0, 1):
        return ("pass" if zeros == prob * shots else "refuted"), None
    if shots == 0:
        return "refuted", None
    z = round((zeros - shots * float(prob)) / math.sqrt(shots * float(prob) * (1 - float(prob))), 6)
    return ("pass" if abs(z) < Z_LIMIT else "refuted"), z


def count_check(kind: str, bits: Callable[[str], list[str]], histogram: dict[str, int]) -> tuple[int, int]:
    """(k, n) of one check; bits(key) gives the check qubits' bits of an outcome key in check-qubit order."""
    n = k = 0
    for key, count in histogram.items():
        values = bits(key)
        if kind == "p_zero":
            n += count
            k += count * (values[0] == "0")
        elif kind in ("p_zero_given_zero", "parity_zero_given_zero") and values[0] == "0":
            n += count
            if kind == "p_zero_given_zero":
                k += count * (values[1] == "0")
            else:
                k += count * (values[1:].count("1") % 2 == 0)
        elif kind not in ("p_zero_given_zero", "parity_zero_given_zero"):
            raise ValueError(f"unknown check {kind!r}")
    return k, n


def bit(key: str, qubit: int) -> str:
    """The bit of `qubit` in a QX or qxelarator key, qubit 0 at the rightmost character."""
    return key[len(key) - 1 - qubit]


def key_bits(places: list[int]) -> Callable[[str], list[str]]:
    """Characters of a record counts key at the given positions."""
    return lambda key: [key[i] for i in places]


def qubit_bits(qubits: tuple[int, ...]) -> Callable[[str], list[str]]:
    """Bits of the given qubits in a QX key, in the order given."""
    return lambda key: [bit(key, q) for q in qubits]


def family_files(family: str, limit: int | None) -> dict[str, str]:
    if family == "a":
        return cases.series("a", "qx", limit=limit)
    if family == "de":
        return cases.series_de(limit=limit)
    raise ValueError(f"unknown family {family!r}")


def replica_entry(replica: dict[str, Any]) -> dict[str, Any]:
    """A manifest replica as the record keeps it: census entry, parameters and checks without counts."""
    checks = [
        {"kind": kind, "qubits": list(qubits), "prediction": want}
        for kind, qubits, want in cases.replica_checks(replica)
        if kind != "cz_count"
    ]
    params = {key: replica[key] for key in PARAMS if key in replica}
    return {"slot": replica["slot"], "census": replica["census"], "params": params, "checks": checks}


def readout_qubits(replicas: list[dict[str, Any]]) -> list[int]:
    out: list[int] = []
    for replica in replicas:
        for check in replica["checks"]:
            out += [q for q in check["qubits"] if q not in out]
    return out


def family_circuits(family: str, limit: int | None) -> list[dict[str, Any]]:
    """Series path, sub-family, text and record replicas of every circuit of one family."""
    files = family_files(family, limit)
    out = []
    for batch in json.loads(files["cases.json"])["batches"]:
        manifest = json.loads(files[f"{batch['batch']}/cases.json"])
        for row in manifest["circuits"]:
            path = f"{batch['batch']}/{row['file']}"
            replicas = [replica_entry(r) for r in row["replicas"]]
            out.append(
                {
                    "file": path,
                    "sub_family": row["sub_family"],
                    "text": files[path],
                    "readout_qubits": readout_qubits(replicas),
                    "replicas": replicas,
                }
            )
    return out


def emulate(item: tuple[str, int, int]) -> dict[str, int]:
    """Pool worker: qxelarator's outcome histogram of one cQASM text (qubit 0 at the rightmost character)."""
    import qxelarator

    text, shots, seed = item
    result = qxelarator.execute_string(text, iterations=shots, seed=seed)
    if isinstance(result, qxelarator.SimulationError) or result.shots_done != shots:
        raise RuntimeError(f"qxelarator: {result}")
    return {str(key): int(value) for key, value in result.results.items()}


def reduce_histogram(outcomes: dict[str, int], qubits: list[int]) -> dict[str, int]:
    """The histogram of the given qubits' bits, character n the bit of qubits[n]."""
    histogram: dict[str, int] = {}
    for key, count in sorted(outcomes.items()):
        reduced = "".join(bit(key, q) for q in qubits)
        histogram[reduced] = histogram.get(reduced, 0) + count
    return dict(sorted(histogram.items()))


def judge(circuit: dict[str, Any]) -> dict[str, Any]:
    """Counted k of n, z and verdict of every check of one circuit from its counts."""
    position = {q: n for n, q in enumerate(circuit["readout_qubits"])}
    replicas = []
    for replica in circuit["replicas"]:
        checks = []
        for check in replica["checks"]:
            places = [position[q] for q in check["qubits"]]
            k, n = count_check(check["kind"], key_bits(places), circuit["counts"])
            result, z = verdict(check["prediction"], k, n)
            checks.append({**check, "k": k, "n": n, "z": z, "verdict": result})
        passed = all(c["verdict"] == "pass" for c in checks)
        replicas.append({**replica, "checks": checks, "verdict": "pass" if passed else "refuted"})
    passed = all(r["verdict"] == "pass" for r in replicas)
    return {**circuit, "replicas": replicas, "verdict": "pass" if passed else "refuted"}


def bare(circuit: dict[str, Any]) -> dict[str, Any]:
    """A judged circuit with every derived field removed, the input judge() re-derives them from."""
    replicas = [
        {
            **{k: v for k, v in r.items() if k != "verdict"},
            "checks": [{k: v for k, v in c.items() if k in ("kind", "qubits", "prediction")} for c in r["checks"]],
        }
        for r in circuit["replicas"]
    ]
    return {**{k: v for k, v in circuit.items() if k != "verdict"}, "replicas": replicas}


def summarize(circuits: list[dict[str, Any]]) -> dict[str, Any]:
    checks = [c for circuit in circuits for r in circuit["replicas"] for c in r["checks"]]
    refuted = [
        f"{circuit['file']} slot {r['slot']} {c['kind']}"
        for circuit in circuits
        for r in circuit["replicas"]
        for c in r["checks"]
        if c["verdict"] != "pass"
    ]
    return {
        "circuits": len(circuits),
        "replicas": sum(len(circuit["replicas"]) for circuit in circuits),
        "checks": len(checks),
        "probabilistic_checks": sum(Fraction(c["prediction"]) not in (0, 1) for c in checks),
        "max_abs_z": max((abs(c["z"]) for c in checks if c["z"] is not None), default=None),
        "refuted": refuted,
        "verdict": "pass" if not refuted else "refuted",
    }


def run(directory: Path, family: str, limit: int | None) -> dict[str, Any]:
    from importlib import metadata

    if metadata.version("qxelarator") != QXELARATOR:
        raise SystemExit(f"qxelarator {metadata.version('qxelarator')} is installed; the sweep pins {QXELARATOR}")
    circuits = family_circuits(family, limit)
    seeds = [BASE_SEED + index for index in range(len(circuits))]
    outcomes = parallel.ordered_map(emulate, [(c["text"], SHOTS, s) for c, s in zip(circuits, seeds, strict=True)])
    judged = []
    for circuit, seed, result in zip(circuits, seeds, outcomes, strict=True):
        row = {
            "file": circuit["file"],
            "sub_family": circuit["sub_family"],
            "sha256": hashlib.sha256(circuit["text"].encode()).hexdigest(),
            "seed": seed,
            "readout_qubits": circuit["readout_qubits"],
            "counts": reduce_histogram(result, circuit["readout_qubits"]),
            "replicas": circuit["replicas"],
        }
        judged.append(judge(row))
    census = cases.load_census()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "family": family,
        "generator": "scripts/box_kite_cases.py " + ("series('a', 'qx')" if family == "a" else "series_de()"),
        "census": cases.census_record(cases.CENSUS, census),
        "emulator": EMULATOR,
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
        "counts_key": "character n of a counts key is the bit of readout_qubits[n]",
        "circuits": judged,
        "summary": summarize(judged),
    }
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"family-{family}.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def expected_replicas(family: str, census: dict[str, Any], limit: int | None) -> dict[str, list[Any]]:
    """Per sub-family, (census entry, parameters, [(kind, prediction)]) of every replica, from the census alone."""
    rows = cases.validate_census(census)
    out: dict[str, list[Any]] = {}
    if family == "a":
        for sub_family, sources, _ in cases.SUB_FAMILIES:
            entries: list[Any] = [
                (f"{source}[{row['index']}]", {}, [("p_zero", row["p_selector_zero"])])
                for source in sources
                for row in rows[source]
            ]
            out[sub_family] = entries if limit is None else entries[:limit]
        return out
    for sub_family, specs in cases.de_specs(census, rows).items():
        entries = []
        for spec in specs:
            checks = [("p_zero", spec["p_selector_zero"])]
            if "p_parity_even_given_selector_zero" in spec:
                checks.append(("parity_zero_given_zero", spec["p_parity_even_given_selector_zero"]))
            entries.append((spec["census"], {key: spec[key] for key in PARAMS if key in spec}, checks))
        out[sub_family] = entries if limit is None else entries[:limit]
    return out


def replay(record: dict[str, Any], bind: bool = False, exhaustive: bool = False) -> dict[str, Any]:
    """Every verdict of a sweep record re-derived from its counts and the census; raises on a difference.

    exhaustive refuses a record made with --limit, which covers only the first N replicas of each
    sub-family; evidence replay of the family requires it.
    """
    if record.get("schema") != SCHEMA or record.get("family") not in FAMILIES:
        raise ValueError(f"record schema {record.get('schema')!r} or family {record.get('family')!r} is unknown")
    census_path = ROOT / record["census"]["path"]
    if hashlib.sha256(census_path.read_bytes()).hexdigest() != record["census"]["sha256"]:
        raise ValueError(f"{record['census']['path']} differs from the census the sweep ran against")
    census = cases.load_census(census_path)
    if record.get("emulator") != EMULATOR:
        raise ValueError(f"record emulator {record.get('emulator')!r} is not the pinned {EMULATOR}")
    shots, limit = record["shots"], record["limit"]
    if exhaustive and limit is not None:
        raise ValueError(f"record ran with --limit {limit}, so it covers only part of each sub-family")
    if (shots, record["z_limit"], record["base_seed"]) != (SHOTS, Z_LIMIT, BASE_SEED):
        raise ValueError("record shots, z_limit or base seed differ from the sweep's")
    covered: dict[str, list[Any]] = {}
    for index, circuit in enumerate(record["circuits"]):
        name = circuit["file"]
        if circuit["seed"] != BASE_SEED + index:
            raise ValueError(f"{name}: seed {circuit['seed']} breaks the seed rule")
        histogram, width = circuit["counts"], len(circuit["readout_qubits"])
        if sum(histogram.values()) != shots or any(
            len(key) != width or set(key) - {"0", "1"} or type(count) is not int or count < 0
            for key, count in histogram.items()
        ):
            raise ValueError(f"{name}: counts do not hold {shots} shots over {width} readout bits")
        replicas = circuit["replicas"]
        if readout_qubits(replicas) != circuit["readout_qubits"]:
            raise ValueError(f"{name}: readout qubits differ from the replicas' checks")
        selectors = [r["checks"][0]["qubits"][0] for r in replicas]
        if len(set(selectors)) != len(selectors):
            raise ValueError(f"{name}: one selector serves two replicas")
        for slot, replica in enumerate(replicas):
            if replica["slot"] != slot:
                raise ValueError(f"{name}: replica slots out of order")
            covered.setdefault(circuit["sub_family"], []).append(
                (replica["census"], replica["params"], [(c["kind"], c["prediction"]) for c in replica["checks"]])
            )
        if judge(bare(circuit)) != circuit:
            raise ValueError(f"{name}: recorded counts, z or verdicts differ from the counts")
    if covered != expected_replicas(record["family"], census, limit):
        raise ValueError("record replicas do not match each sub-family's census entries and predictions in order")
    if summarize(record["circuits"]) != record["summary"]:
        raise ValueError("record summary differs from its circuits")
    if bind:
        regenerated = family_circuits(record["family"], limit)
        if [c["file"] for c in regenerated] != [c["file"] for c in record["circuits"]]:
            raise ValueError("regenerated circuit files differ from the record")
        for new, old in zip(regenerated, record["circuits"], strict=True):
            if hashlib.sha256(new["text"].encode()).hexdigest() != old["sha256"]:
                raise ValueError(f"{old['file']}: regenerated bytes differ from the swept circuit")
            if new["replicas"] != bare(old)["replicas"]:
                raise ValueError(f"{old['file']}: regenerated replica checks differ from the record")
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
    """qxelarator runs of retained case circuits, judged check by check, and of their readout pairs."""
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
        checks: list[Check] = []
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
                k, n = count_check(kind, qubit_bits(qubits), outcome)
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


def synthetic_shots(replica: dict[str, Any]) -> list[str]:
    """Per-shot readout bits of one replica whose counts meet its predictions; non-deterministic ones off by -24."""
    checks = {c["kind"]: c for c in replica["checks"]}
    p = Fraction(checks["p_zero"]["prediction"])
    zeros = int(p * SHOTS) if p in (0, 1) else int(p * SHOTS) - 24 + 7 * replica["slot"]
    width = len(readout_qubits([replica]))
    parity = checks.get("parity_zero_given_zero")
    even = zeros
    if parity is not None:
        q = Fraction(parity["prediction"])
        even = int(q * zeros) if q in (0, 1) else int(q * zeros) - 8
    shots = []
    for shot in range(SHOTS):
        selector = "0" if shot < zeros else "1"
        data = "0" * (width - 1) if shot < even or shot >= zeros else "1" + "0" * (width - 2)
        shots.append(selector + data)
    return shots


def synthetic_record(family: str) -> dict[str, Any]:
    """A complete record of one family whose counts follow the census predictions, packed as its series packs."""
    census = cases.load_census()
    rows = cases.validate_census(census)
    groups: list[tuple[str, list[dict[str, Any]]]] = []
    if family == "a":
        for sub_family, sources, encoding in cases.SUB_FAMILIES:
            members = [(encoding, row) for source in sources for row in rows[source]]
            for group in cases.pack(members, cases.WIDTH[encoding]):
                groups.append(
                    (
                        sub_family,
                        [cases.replica_record(s, enc, row, place) for s, ((enc, row), place) in enumerate(group)],
                    )
                )
    else:
        for sub_family, specs in cases.de_specs(census, rows).items():
            for group in cases.pack(specs, cases.de_width(sub_family)):
                groups.append(
                    (sub_family, [{"slot": s, **spec, "roles": cases.de_roles(sub_family, place)}
                                  for s, (spec, place) in enumerate(group)])
                )  # fmt: skip
    circuits = []
    for index, (sub_family, manifest_replicas) in enumerate(groups):
        replicas = [replica_entry(r) for r in manifest_replicas]
        per_replica = [synthetic_shots(r) for r in replicas]
        histogram: dict[str, int] = {}
        for shot in range(SHOTS):
            key = "".join(shots[shot] for shots in per_replica)
            histogram[key] = histogram.get(key, 0) + 1
        row = {
            "file": f"batch-{index:03d}/{sub_family}.cq",
            "sub_family": sub_family,
            "sha256": hashlib.sha256(f"{family}-{index}".encode()).hexdigest(),
            "seed": BASE_SEED + index,
            "readout_qubits": readout_qubits(replicas),
            "counts": dict(sorted(histogram.items())),
            "replicas": replicas,
        }
        circuits.append(judge(row))
    return {
        "schema": SCHEMA,
        "family": family,
        "census": cases.census_record(cases.CENSUS, census),
        "emulator": EMULATOR,
        "shots": SHOTS,
        "base_seed": BASE_SEED,
        "limit": None,
        "z_limit": Z_LIMIT,
        "circuits": circuits,
        "summary": summarize(circuits),
    }


def move_shot(record: dict[str, Any], circuit_index: int, position: int, to: str | None = None) -> None:
    """Move one shot of a circuit to a key whose readout bit at `position` reads `to` (flipped when None)."""
    circuit = record["circuits"][circuit_index]
    source = next(k for k in sorted(circuit["counts"]) if k[position] != to)
    to = to if to is not None else "1" if source[position] == "0" else "0"
    target = source[:position] + to + source[position + 1 :]
    circuit["counts"][source] -= 1
    circuit["counts"][target] = circuit["counts"].get(target, 0) + 1
    circuit["counts"] = {k: v for k, v in sorted(circuit["counts"].items()) if v}


def family_mutations(family: str, circuits: int) -> int:
    """Replay a synthetic record of one family and count the mutations its replay rejects."""
    record = synthetic_record(family)
    summary = replay(record)
    if summary["verdict"] != "pass" or summary["circuits"] != circuits:
        raise AssertionError(f"the synthetic family {family} record replays as {summary}")
    rejected = 0

    def reject(label: str, mutate: Callable[[dict[str, Any]], Any]) -> None:
        nonlocal rejected
        mutated = copy.deepcopy(record)
        mutate(mutated)
        try:
            replay(mutated)
        except ValueError:
            rejected += 1
            return
        raise AssertionError(f"family {family}: {label} was accepted")

    def first(prediction: str) -> tuple[int, int, int]:
        """(circuit, readout position of the selector, slot) of the first replica predicting P(selector = 0)."""
        return next(
            (n, c["readout_qubits"].index(r["checks"][0]["qubits"][0]), s)
            for n, c in enumerate(record["circuits"])
            for s, r in enumerate(c["replicas"])
            if r["checks"][0]["prediction"] == prediction
        )

    dark, half = first("0"), first("1/2")
    reject("one selector-0 shot on a P = 0 replica", lambda r: move_shot(r, dark[0], dark[1], "0"))

    def skew(r: dict[str, Any]) -> None:
        for _ in range(200):
            move_shot(r, half[0], half[1], "0")

    reject("a P = 1/2 replica pushed past the z limit", skew)
    reject("a lost shot", lambda r: r["circuits"][0]["counts"].update({next(iter(r["circuits"][0]["counts"])): 0}))
    reject("a broken seed", lambda r: r["circuits"][3].update({"seed": BASE_SEED}))
    reject(
        "a changed prediction",
        lambda r: r["circuits"][dark[0]]["replicas"][dark[2]]["checks"][0].update({"prediction": "1"}),
    )
    reject("a dropped circuit", lambda r: (r["circuits"].pop(), r.update({"summary": summarize(r["circuits"])})))
    reject("a changed census digest", lambda r: r["census"].update({"sha256": "0" * 64}))
    reject("another emulator release", lambda r: r["emulator"].update({"version": "0.9.0"}))
    reject("a dropped emulator field", lambda r: r.pop("emulator"))
    reject("an edited summary", lambda r: r["summary"].update({"verdict": "refuted"}))
    if family == "de":
        parity = next(
            (n, c["readout_qubits"].index(r["checks"][1]["qubits"][1]))
            for n, c in enumerate(record["circuits"])
            for r in c["replicas"]
            if len(r["checks"]) > 1
            and r["checks"][1]["prediction"] in ("0", "1")
            and r["checks"][0]["prediction"] == "1"
        )
        reject("one coherence shot of the wrong parity", lambda r: move_shot(r, parity[0], parity[1]))

        def swap_setting(r: dict[str, Any]) -> None:
            replica = next(rep for c in r["circuits"] for rep in c["replicas"] if rep["params"].get("pauli"))
            replica["params"]["pauli"] = "XXXX"

        reject("a swapped coherence setting", swap_setting)
    limited = copy.deepcopy(record)
    limited["limit"] = len(record["circuits"]) * 8
    replay(limited)
    try:
        replay(limited, exhaustive=True)
    except ValueError:
        rejected += 1
    else:
        raise AssertionError(f"family {family}: a --limit record passed the exhaustive replay")
    # An honest record of a refutation replays and reports the refuted check.
    honest = copy.deepcopy(record)
    move_shot(honest, dark[0], dark[1], "0")
    honest["circuits"][dark[0]] = judge(bare(honest["circuits"][dark[0]]))
    honest["summary"] = summarize(honest["circuits"])
    if replay(honest)["verdict"] != "refuted":
        raise AssertionError("an honest refuted record replays as passing")
    return rejected


def self_test() -> None:
    rejected = family_mutations("a", 848) + family_mutations("de", 149)
    for p, zeros, outcome in (("0", 0, "pass"), ("0", 1, "refuted"), ("1", SHOTS, "pass"), ("1/2", 1024, "pass")):
        if verdict(p, zeros, SHOTS)[0] != outcome:
            raise AssertionError(f"verdict({p}, {zeros}) is not {outcome}")
    edge = round(SHOTS / 2 + Z_LIMIT * math.sqrt(SHOTS / 4))
    if verdict("1/2", edge, SHOTS)[0] != "refuted" or verdict("1/2", edge - 2, SHOTS)[0] != "pass":
        raise AssertionError("the z limit does not separate the P = 1/2 verdicts")
    # Selector-0 keys 000 (3, data 00 even), 010 (1, odd), 011 (2, even): k = 5 of n = 6.
    if count_check("parity_zero_given_zero", list, {"000": 3, "010": 1, "011": 2, "100": 5}) != (5, 6):
        raise AssertionError("the parity count disagrees with its definition")
    print(f"box-kite QX sweep: synthetic records of families a and de replay; {rejected} mutations rejected")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", type=Path, metavar="DIR")
    mode.add_argument("--replay", type=Path, metavar="RECORD")
    mode.add_argument("--emulate", type=Path, nargs="+", metavar="CASE_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--family", nargs="+", choices=FAMILIES, default=list(FAMILIES), help="with --run")
    parser.add_argument("--limit", type=int, help="with --run: the first N replicas of each sub-family")
    parser.add_argument("--bind", action="store_true", help="with --replay: regenerate and compare circuit bytes")
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="with --replay: fail on a refuted check or on a record made with --limit",
    )
    parser.add_argument("--out", type=Path, help="with --emulate: write the emulation record here")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.run:
        failed = False
        for family in args.family:
            summary = run(args.run, family, args.limit)["summary"]
            failed |= summary["verdict"] != "pass"
            print(
                f"box-kite QX sweep {family}: {summary['circuits']} circuits, {summary['replicas']} replicas, "
                f"{summary['checks']} checks, {summary['verdict']}"
            )
        return 1 if failed else 0
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
        record = json.loads(args.replay.read_text(encoding="utf-8"))
        summary = replay(record, bind=args.bind, exhaustive=args.require_pass)
    except ValueError as error:
        raise SystemExit(f"{args.replay}: {error}") from error
    print(
        f"box-kite QX sweep replay: {summary['circuits']} circuits, {summary['replicas']} replicas, "
        f"{summary['checks']} checks, max |z| {summary['max_abs_z']}, {summary['verdict']}"
    )
    return 1 if args.require_pass and summary["verdict"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
