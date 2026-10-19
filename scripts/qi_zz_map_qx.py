"""Build compact QX preflight twins of the proposed Tuna-17 ZZ map, entirely offline.

Only inactive wait-only wires are removed. Every active gate, explicit wait,
barrier and measurement survives an order-preserving register relabeling.
The ideal checks concern native gates and wiring, not physical idle ZZ.

Usage: python scripts/qi_zz_map_qx.py (--write DIR | --check DIR | --self-test)
       python scripts/qi_zz_map_qx.py --analyze RUNS_ROOT --plan PLAN --out NEWFILE
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS, _check_submission_manifest  # noqa: E402
from qi_zz_map import CATALOGUE, digest, json_text, require  # noqa: E402
from qi_zz_map import DEFAULT_OUT as TUNA_CASES  # noqa: E402

from parallel import ordered_map  # noqa: E402

DEFAULT_OUT = ROOT / "results/quantum_inspire/cases/zz_map_qx"
PLAN_SCHEMA = "qi-zz-map-qx-plan-v1"
CASE_SCHEMA = "qi-zz-map-qx-cases-v1"
SHOTS = 1024
Y_TESTS = 576
FAMILY_ALPHA = 0.01
WIRE = re.compile(r"(X90|mX90|Y90|mY90|wait\([0-9]+\)) q\[([0-9]+)\]")
GLOBAL_WAIT = re.compile(r"wait\([0-9]+\) q")
POLICY = {
    "deterministic_outcomes": "zero mismatches in every prepared neighbor, calibration bit and X probe",
    "y_marginals": "abs(P1-0.5) <= sqrt(log(2*m/alpha)/(2*n)) for every Y probe",
    "y_tests": Y_TESTS,
    "family_alpha": FAMILY_ALPHA,
    "scope": "ideal marginal gate/wiring conformance; no physical ZZ, hardware timing or joint independence claim",
}


def compact(source: str, active: list[int]) -> str:
    """Delete only inactive per-wire waits; relabel every remaining wire monotonically."""
    require(active == sorted(set(active)) and 2 <= len(active) <= 8, "invalid active register")
    require(all(0 <= q < 17 for q in active), "active wire outside Tuna register")
    mapping = {qubit: index for index, qubit in enumerate(active)}
    lines = []
    declarations = set()
    for line in source.splitlines():
        if line in ("qubit[17] q", "bit[17] b"):
            declarations.add(line)
            lines.append(line.replace("[17]", f"[{len(active)}]"))
        elif match := WIRE.fullmatch(line):
            gate, qubit = match[1], int(match[2])
            if qubit in mapping:
                lines.append(f"{gate} q[{mapping[qubit]}]")
            else:
                require(gate.startswith("wait("), "would discard an active operation on an omitted wire")
        else:
            require(
                line in ("", "version 3.0", "init q", "barrier q", "b = measure q")
                or line.startswith("//")
                or GLOBAL_WAIT.fullmatch(line) is not None,
                f"unrecognized source instruction: {line}",
            )
            lines.append(line)
    require(declarations == {"qubit[17] q", "bit[17] b"}, "source register declaration mismatch")
    return "\n".join(lines) + "\n"


def transform(task: tuple[str, dict[str, Any]]) -> tuple[dict[str, Any], str]:
    source_root, source_row = task
    row = copy.deepcopy(source_row)
    relative = f"{row['batch_directory']}/{row['file']}"
    source = (Path(source_root) / relative).read_bytes()
    require(digest(source) == row["sha256"], "Tuna circuit differs from its plan")
    active = sorted({q for pair in row["pairs"] for q in pair["edge"]})
    mapping = {q: index for index, q in enumerate(active)}
    code = compact(source.decode("utf-8"), active)
    for pair in row["pairs"]:
        pair["tuna_edge"] = pair["edge"]
        pair["edge"] = [mapping[q] for q in pair["edge"]]
        for role in ("probe", "neighbor"):
            if role in pair:
                pair[role] = mapping[pair[role]]
    row.update(
        sha256=digest(code),
        nqubits=len(active),
        tuna_to_qx={str(q): mapping[q] for q in active},
        source_tuna_circuit={"path": relative, "sha256": digest(source)},
    )
    return row, code


def build(source_plan: Path = TUNA_CASES / "plan.json") -> dict[str, str]:
    source_plan = source_plan.resolve()
    source = json.loads(source_plan.read_bytes())
    require(source["schema"] == "qi-zz-map-plan-v1", "unrecognized Tuna plan")
    require(source["status"] == "proposed_not_submitted", "source is not the unsubmitted proposal")
    require(source["cost"]["total_jobs"] == 416 and len(source["batches"]) == 139, "Tuna budget changed")
    require(HARDWARE_BATCH_CIRCUITS == 3, "hardware batch policy changed")
    catalogue = json.loads(CATALOGUE.read_bytes())
    backend = next(b for b in catalogue["backend_types"] if b["identifier"] == "QXsinglenodesimulator")
    require(backend["nqubits"] >= 8 and backend["max_number_of_shots"] >= SHOTS, "QX capacity changed")
    require(backend["max_jobs_per_batch_job"] >= 3, "QX batch limit changed")
    require(
        {"X90", "mX90", "Y90", "mY90", "init", "wait", "barrier", "measure"} <= set(backend["gateset"]),
        "QX lacks a required native instruction",
    )
    for batch in source["batches"]:
        require(
            digest((source_plan.parent / batch["directory"] / "cases.json").read_bytes()) == batch["cases_sha256"],
            "Tuna batch manifest differs from its plan",
        )
    identities = {
        "source_tuna_plan_sha256": digest(source_plan.read_bytes()),
        "catalogue_sha256": digest(CATALOGUE.read_bytes()),
        "qx_builder_sha256": digest(Path(__file__).read_bytes()),
    }
    rendered = ordered_map(transform, [(str(source_plan.parent), row) for row in source["circuits"]])
    files: dict[str, str] = {}
    rows = [row for row, _ in rendered]
    for row, code in rendered:
        files[f"{row['batch_directory']}/{row['file']}"] = code
    batches = []
    for batch in source["batches"]:
        directory = batch["directory"]
        batch_rows = [
            {k: v for k, v in row.items() if k != "batch_directory"}
            for row in rows
            if row["batch_directory"] == directory
        ]
        require(0 < len(batch_rows) <= HARDWARE_BATCH_CIRCUITS, "QX batch exceeds the matched hardware cap")
        cases = {
            "schema": CASE_SCHEMA,
            "status": "proposed_not_submitted",
            "backend": backend["identifier"],
            "backend_type_id": backend["id"],
            "nqubits": max(row["nqubits"] for row in batch_rows),
            "register_width_convention": "nqubits is the batch maximum; each circuit records its exact nqubits",
            "shots": SHOTS,
            "source_digests": identities,
            "circuits": batch_rows,
        }
        text = json_text(cases)
        files[f"{directory}/cases.json"] = text
        batches.append({"directory": directory, "circuits": len(batch_rows), "cases_sha256": digest(text)})
    require(sum(len(row["pairs"]) for row in rows if row.get("quadrature") == "y") == Y_TESTS, "Y-test family changed")
    files["plan.json"] = json_text(
        {
            "schema": PLAN_SCHEMA,
            "status": "proposed_not_submitted",
            "backend": backend["identifier"],
            "backend_type_id": backend["id"],
            "source_tuna_plan": str(source_plan.relative_to(ROOT)),
            "source_digests": identities,
            "shots": SHOTS,
            "bit_order": "qubit_0_rightmost",
            "cost": {"total_jobs": 416, "batches": 139, "shots_per_job": SHOTS, "total_job_shots": 416 * SHOTS},
            "sanity_policy": POLICY,
            "circuits": rows,
            "batches": batches,
        }
    )
    return files


def check_counts(row: dict[str, Any], counts: Counter[str], shots: int) -> list[str]:
    """Fixed ideal marginals, with a Hoeffding/union bound over all 576 Y probes."""
    require(sum(counts.values()) == shots and shots > 0, "incorrect raw denominator")
    require(
        all(
            len(s) == row["nqubits"] and not set(s) - {"0", "1"} and type(n) is int and n > 0 for s, n in counts.items()
        ),
        "malformed raw outcomes",
    )
    failures = []
    bound = math.sqrt(math.log(2 * Y_TESTS / FAMILY_ALPHA) / (2 * shots))
    for pair in row["pairs"]:
        if row["kind"] == "readout":
            deterministic = dict(zip(pair["edge"], pair["prepared"], strict=True))
        else:
            deterministic = {pair["neighbor"]: pair["neighbor_state"]}
            if row["quadrature"] == "x":
                deterministic[pair["probe"]] = 0
            else:
                ones = sum(n for s, n in counts.items() if s[-1 - pair["probe"]] == "1")
                if abs(ones / shots - 0.5) > bound:
                    failures.append(f"Y probe q{pair['probe']} differs from 1/2 beyond the familywise bound")
        for qubit, target in deterministic.items():
            if any(int(shot[-1 - qubit]) != target for shot in counts):
                failures.append(f"deterministic q{qubit} differs from {target}")
    return failures


def read_batch(task: dict[str, Any]) -> dict[str, Any]:
    directory = Path(task["runs_root"]) / task["batch"]["directory"]
    hashes = {}

    def read(name: str) -> bytes:
        payload = (directory / name).read_bytes()
        hashes[f"{task['batch']['directory']}/{name}"] = digest(payload)
        return payload

    cases_bytes = read("cases.json")
    require(digest(cases_bytes) == task["batch"]["cases_sha256"], "QX manifest differs from reviewed plan")
    cases = json.loads(cases_bytes)
    receipt = json.loads(read("submission.json"))
    require(receipt.get("schema") == "qi-submission-v2", "future QX preflight requires a digest-bound v2 receipt")
    _check_submission_manifest(directory, receipt, require_enqueued=True)
    require(
        cases["backend"] == "QXsinglenodesimulator" and cases["backend_type_id"] == task["backend_type_id"],
        "wrong backend",
    )
    require(cases["shots"] == SHOTS, "QX denominator differs from preflight")
    rows = task["rows"]
    expected = [{k: v for k, v in row.items() if k != "batch_directory"} for row in rows]
    require(cases["circuits"] == expected, "QX circuit roles differ from plan")
    collected = json.loads(read("results.json"))
    jobs = {row["file"]: row["job"] for row in receipt["jobs"]}
    results = {row["file"]: row for row in collected["jobs"]}
    require(
        len(jobs) == len(receipt["jobs"]) == len(results) == len(collected["jobs"]) == len(rows),
        "duplicate or missing job",
    )
    require(set(jobs) == set(results) == {row["file"] for row in rows}, "QX acquisition file set mismatch")
    checked = []
    for row in rows:
        name = row["file"]
        require(digest(read(name)) == row["sha256"], "QX circuit hash mismatch")
        retained = results[name]
        job = retained["job"]
        require(job["id"] == jobs[name] and job["batch_job_id"] == receipt["batch_job"], "job identity mismatch")
        require(job["status"] == "completed" and job["number_of_shots"] == SHOTS, "QX job incomplete")
        require(job.get("raw_data_enabled") is True, "QX raw output was not retained")
        raw = json.loads(read(f"raw/{name}.json"))
        require(
            isinstance(raw, list) and len(raw) == SHOTS and all(isinstance(s, str) for s in raw),
            "QX raw shots malformed",
        )
        counts = Counter(raw)
        require(len(retained["results"]) == 1, "QX job needs exactly one result")
        result = retained["results"][0]
        require(
            result["job_id"] == job["id"]
            and result["shots_requested"] == result["shots_done"] == SHOTS
            and result["results"] == dict(counts),
            "QX result metadata or histogram mismatch",
        )
        checked.append({"file": name, "job": job["id"], "failures": check_counts(row, counts, SHOTS)})
    return {"circuits": checked, "input_sha256": hashes}


def analyze(plan_path: Path, runs_root: Path) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    require(plan["schema"] == PLAN_SCHEMA and plan["sanity_policy"] == POLICY, "unrecognized QX plan or criteria")
    require(plan["cost"]["total_jobs"] == 416 and len(plan["batches"]) == 139, "incomplete preflight design")
    tasks = [
        {
            "runs_root": str(runs_root),
            "batch": batch,
            "backend_type_id": plan["backend_type_id"],
            "rows": [row for row in plan["circuits"] if row["batch_directory"] == batch["directory"]],
        }
        for batch in plan["batches"]
    ]
    results = ordered_map(read_batch, tasks)
    checked = [row for result in results for row in result["circuits"]]
    require(len(checked) == 416 and len({row["job"] for row in checked}) == 416, "missing or reused QX acquisition")
    return {
        "schema": "qi-zz-map-qx-preflight-analysis-v1",
        "plan_sha256": digest(plan_bytes),
        "sanity_policy": POLICY,
        "passes": all(not row["failures"] for row in checked),
        "circuits": checked,
        "input_sha256": {k: v for result in results for k, v in result["input_sha256"].items()},
        "scope": "QX ideal native-gate/wiring sanity only; no physical ZZ or hardware timing validation",
    }


def self_test() -> None:
    source = (
        "version 3.0\nqubit[17] q\nbit[17] b\ninit q\nbarrier q\n"
        "X90 q[2]\nwait(1) q[3]\nmY90 q[14]\nwait(25) q\nbarrier q\nb = measure q\n"
    )
    expected = (
        source.replace("[17]", "[2]")
        .replace("X90 q[2]", "X90 q[0]")
        .replace("mY90 q[14]", "mY90 q[1]")
        .replace("wait(1) q[3]\n", "")
    )
    require(compact(source, [2, 14]) == expected, "sparse active-wire compaction changed an instruction")
    for broken in (source.replace("wait(1) q[3]", "X90 q[3]"), source.replace("X90 q[2]", "CZ q[2], q[14]")):
        try:
            compact(broken, [2, 14])
        except ValueError:
            pass
        else:
            raise AssertionError("compaction silently discarded or accepted an unsupported operation")
    row = {
        "kind": "conditional_ramsey",
        "quadrature": "y",
        "nqubits": 2,
        "pairs": [{"edge": [0, 1], "probe": 0, "neighbor": 1, "neighbor_state": 1}],
    }
    require(not check_counts(row, Counter({"10": 512, "11": 512}), SHOTS), "ideal Y fixture rejected")
    require(bool(check_counts(row, Counter({"10": SHOTS}), SHOTS)), "biased Y fixture accepted")
    require(bool(check_counts(row, Counter({"00": 512, "01": 512}), SHOTS)), "neighbor bit-order failure accepted")
    row["quadrature"] = "x"
    require(not check_counts(row, Counter({"10": SHOTS}), SHOTS), "ideal X fixture rejected")
    require(bool(check_counts(row, Counter({"10": SHOTS - 1, "11": 1}), SHOTS)), "deterministic X error accepted")
    calibration = {"kind": "readout", "nqubits": 2, "pairs": [{"edge": [0, 1], "prepared": [1, 0]}]}
    require(not check_counts(calibration, Counter({"01": SHOTS}), SHOTS), "canonical calibration indexing failed")
    with tempfile.TemporaryDirectory() as scratch:
        directory = Path(scratch) / "batch-000"
        (directory / "raw").mkdir(parents=True)
        name = "fixture.cq"
        (directory / name).write_text(expected, encoding="utf-8")
        retained_row = {**row, "file": name, "sha256": digest(expected)}
        cases = {"backend": "QXsinglenodesimulator", "backend_type_id": 1, "shots": SHOTS, "circuits": [retained_row]}
        cases_bytes = json_text(cases)
        (directory / "cases.json").write_text(cases_bytes, encoding="utf-8")
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "batch_job": "synthetic-batch",
            "backend": cases["backend"],
            "backend_type_id": 1,
            "shots": SHOTS,
            "cases_sha256": digest(cases_bytes),
            "jobs": [{"file": name, "job": "synthetic-job", "sha256": digest(expected)}],
        }
        (directory / "submission.json").write_text(json_text(receipt), encoding="utf-8")
        collected = {
            "jobs": [
                {
                    "file": name,
                    "job": {
                        "id": "synthetic-job",
                        "batch_job_id": "synthetic-batch",
                        "number_of_shots": SHOTS,
                        "status": "completed",
                        "raw_data_enabled": True,
                    },
                    "results": [
                        {
                            "job_id": "synthetic-job",
                            "shots_requested": SHOTS,
                            "shots_done": SHOTS,
                            "results": {"10": SHOTS},
                        }
                    ],
                }
            ]
        }
        (directory / "results.json").write_text(json_text(collected), encoding="utf-8")
        raw_path = directory / "raw" / f"{name}.json"
        raw_path.write_text(json_text(["10"] * SHOTS), encoding="utf-8")
        task = {
            "runs_root": scratch,
            "backend_type_id": 1,
            "batch": {"directory": "batch-000", "cases_sha256": digest(cases_bytes)},
            "rows": [{**retained_row, "batch_directory": "batch-000"}],
        }
        require(not read_batch(task)["circuits"][0]["failures"], "valid retained-input fixture rejected")
        raw_path.write_text(json_text(["11"] * SHOTS), encoding="utf-8")
        try:
            read_batch(task)
        except ValueError:
            pass
        else:
            raise AssertionError("altered raw shots were accepted against the retained histogram")
    print(
        "QX ZZ preflight: sparse-wire preservation, unsafe omissions, "
        "native vocabulary and fixed sanity regressions pass"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--analyze", type=Path, metavar="RUNS_ROOT")
    parser.add_argument("--source-plan", type=Path, default=TUNA_CASES / "plan.json")
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUT / "plan.json")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.analyze:
        if args.out is None:
            parser.error("--analyze requires --out NEWFILE")
        text = json_text(analyze(args.plan, args.analyze))
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(text)
        return 0
    files = build(args.source_plan)
    directory = args.write or args.check
    existing = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if args.check:
        require(existing == set(files), "QX proposal file set differs from regeneration")
        require(
            all((directory / name).read_text(encoding="utf-8") == text for name, text in files.items()),
            "QX proposal content differs",
        )
    else:
        require(not existing - set(files), "refusing to overwrite retained acquisitions or unrelated files")
        for name, text in files.items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    print(f"QX ZZ preflight: {len(files)} files, 416 compact circuits, 139 batches, 425984 proposed shots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
