"""Compare the request bytes our submitter sends with the bytes iqm-client would send for one retained case body.

Our submitter (iqm_jobs.post_job) hashes json.dumps(body, sort_keys=True) into submission.json as body_sha256 and
sends json.dumps(body) through iqm_platform.Client. iqm-client builds a RunRequest model and sends its
model_dump_json() as UTF-8 bytes under Content-Type "application/json; charset=UTF-8" (_IQMServerClient._serialize_model
and _prepare_request_kwargs). The tool records our wire bytes through a recording transport, builds the RunRequest
for the same case row, and reports the digest of every form, whether the circuits agree as data, and which request
fields only one side names. Nothing leaves the process: the transport answers a fixed reply and iqm-client is used only
to build and serialize the model.

Usage:
    "$PYTHON" scripts/iqm_transport_capture.py CASE_DIR [--job kernel] [--qc garnet] [--out FILE]
    "$PYTHON" scripts/iqm_transport_capture.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import iqm_jobs  # noqa: E402
import iqm_platform  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def our_wire(body: dict[str, Any], path: str) -> tuple[bytes, dict[str, str]]:
    """The bytes and headers iqm_platform.Client.post puts on the wire for body, from a recording transport."""
    seen: list[tuple[str, str, bytes | None, dict[str, str]]] = []

    def transport(
        method: str, url: str, data: bytes | None, headers: dict[str, str]
    ) -> tuple[int, dict[str, str], bytes]:
        seen.append((method, url, data, headers))
        return 201, {}, b'{"id": "recorded"}'

    client = iqm_platform.Client("recorded-not-a-token", transport)
    client.post(path, body)
    _, _, data, headers = seen[0]
    if data is None:
        raise RuntimeError("the recording transport saw no body")
    return data, {k: v for k, v in headers.items() if k.lower() != "authorization"}


def iqm_client_wire(body: dict[str, Any]) -> bytes:
    """The body bytes iqm-client sends for the same circuits, shots and options."""
    from iqm.iqm_client.iqm_client import RunRequest
    from iqm.iqm_server_client.iqm_server_client import _IQMServerClient
    from iqm.pulse import Circuit, CircuitOperation

    circuits = [
        Circuit(
            name=c["name"],
            instructions=tuple(
                CircuitOperation(name=i["name"], locus=tuple(i["locus"]), args=i["args"]) for i in c["instructions"]
            ),
        )
        for c in body["circuits"]
    ]
    request = RunRequest(
        circuits=circuits,
        shots=body["shots"],
        heralding_mode=body["heralding_mode"],
        active_reset_cycles=body.get("active_reset_cycles"),
        calibration_set_id=body.get("calibration_set_id"),
    )
    return _IQMServerClient._serialize_model(request).encode("utf-8")


def circuit_view(circuit: dict[str, Any]) -> list[Any]:
    return [(i["name"], list(i["locus"]), i["args"]) for i in circuit["instructions"]]


def capture(case_dir: Path, job: str, qc: str) -> dict[str, Any]:
    cases = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    row = next(r for r in cases["jobs"] if r["job"] == job)
    body = iqm_jobs.body_of(case_dir, row, qc)
    ours, headers = our_wire(body, f"{iqm_platform.API}/jobs/{qc}/circuit")
    theirs = iqm_client_wire(body)
    recorded = sha256(json.dumps(body, sort_keys=True).encode())
    ours_data, theirs_data = json.loads(ours), json.loads(theirs)
    only_theirs = {k: theirs_data[k] for k in sorted(set(theirs_data) - set(ours_data))}
    return {
        "case": cases["case"],
        "job": job,
        "qc": qc,
        "circuits": len(body["circuits"]),
        "digests": {
            "recorded_body_sha256_sorted_keys": recorded,
            "our_wire_sha256": sha256(ours),
            "iqm_client_wire_sha256": sha256(theirs),
        },
        "bytes": {"our_wire": len(ours), "iqm_client_wire": len(theirs)},
        "our_wire_equals_recorded_form": sha256(ours) == recorded,
        "iqm_client_equals_our_wire": theirs == ours,
        "circuits_agree_as_data": [circuit_view(c) for c in ours_data["circuits"]]
        == [circuit_view(c) for c in theirs_data["circuits"]],
        "scalar_fields_ours": {k: v for k, v in ours_data.items() if k != "circuits"},
        "scalar_fields_iqm_client": {k: v for k, v in theirs_data.items() if k != "circuits"},
        "fields_only_in_iqm_client": only_theirs,
        "our_headers": headers,
    }


def self_test() -> int:
    """A one-circuit case: the recorded digest is not the wire digest, and the circuits agree as data."""
    circuit = {
        "name": "c0",
        "instructions": [
            {"name": "prx", "locus": ["QB1"], "args": {"angle": 1.5707963268, "phase": 0.0}},
            {"name": "measure", "locus": ["QB1"], "args": {"key": "m"}},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        case_dir = Path(tmp)
        (case_dir / "circuits").mkdir()
        (case_dir / "circuits/c0.json").write_text(json.dumps(circuit), encoding="utf-8")
        row = {
            "job": "kernel",
            "circuits": [{"file": "circuits/c0.json"}],
            "shots": 10,
            "options": {"heralding_mode": "zeros", "active_reset_cycles": 1, "calibration_set_id": None},
        }
        (case_dir / "cases.json").write_text(json.dumps({"case": "self-test", "jobs": [row]}), encoding="utf-8")
        report = capture(case_dir, "kernel", "garnet")
    problems = []
    if report["our_wire_equals_recorded_form"]:
        problems.append("the self-test body has sorted keys; it cannot show the key-order difference")
    if not report["circuits_agree_as_data"]:
        problems.append("circuits differ as data")
    if report["iqm_client_equals_our_wire"]:
        problems.append("the two encoders produced the same bytes")
    if problems:
        print("self-test failed: " + "; ".join(problems))
        return 1
    print("self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("case", type=Path, nargs="?")
    parser.add_argument("--job", default="kernel")
    parser.add_argument("--qc", default="garnet")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.case is None:
        parser.error("CASE_DIR is required")
    report = capture(args.case, args.job, args.qc)
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
