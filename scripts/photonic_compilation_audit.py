"""Compare requested intensities, returned numerical meshes and measured one-click frequencies.

Service circuits pass a bounded protobuf wire decoder, rather than Perceval's
expression deserializer. A closer preceding setting is a discriminating
observation, not proof that the hardware retained its preceding configuration.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import zlib
from pathlib import Path
from typing import Any

import numpy as np
import qd_belenos_mesh as mesh
import qd_platform as qd
from photonic_repeat_readout import ROOT, analyze

from parallel import ordered_map


def _elements(blob: str) -> list[Any]:
    if len(blob) > qd.RESULT_LIMIT:
        raise ValueError("the compiled mesh exceeds the result bound")
    if blob.startswith(":PCVL:zip:"):
        decoder = zlib.decompressobj()
        data = decoder.decompress(base64.b64decode(blob[len(":PCVL:zip:") :], validate=True), qd.RESULT_LIMIT + 1)
        if len(data) > qd.RESULT_LIMIT or not decoder.eof or decoder.unused_data:
            raise ValueError("the compressed mesh exceeds its bound or carries additional streams")
        blob = data.decode("utf-8")
    elements = mesh.decode(blob)
    for kind, mode, value in elements:
        if kind == "bs":
            if not 0 <= mode < 23 or not np.isfinite(value).all():
                raise ValueError("the returned coupler lies outside the 24-mode finite numeric domain")
        elif not 0 <= mode < 24 or not isinstance(value, int | float) or not np.isfinite(value):
            raise ValueError("the returned phase lies outside the 24-mode finite numeric domain")
    return elements


def compiled_probabilities(blob: str, input_state: str) -> list[float]:
    match = re.fullmatch(r":PCVL:BasicState:\|([01](?:,[01])*)>", input_state)
    occupation = [int(value) for value in match[1].split(",")] if match else []
    if len(occupation) != 24 or sum(occupation) != 1:
        raise ValueError("the mesh comparison requires a 24-mode one-photon computed input")
    elements = _elements(blob)
    unitary = mesh.unitary(elements, [value for kind, _, value in elements if kind == "ps"])
    probabilities = np.abs(unitary[:, occupation.index(1)]) ** 2
    if not np.isfinite(probabilities).all() or abs(float(sum(probabilities)) - 1) > 1e-9:
        raise ValueError("the returned optical mesh fails probability normalization")
    return probabilities.tolist()


def _row(arguments: tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]) -> dict[str, Any]:
    row, entry, preceding = arguments
    fields = entry["result_fields"]
    compiled = compiled_probabilities(fields["computed_circuit"], fields["computed_input"])
    measured, requested = np.asarray(row["mode_probabilities"]), np.asarray(row["expected_mode_probabilities"])
    previous_distance = None
    if preceding is not None:
        previous_fields = preceding["result_fields"]
        previous = compiled_probabilities(previous_fields["computed_circuit"], previous_fields["computed_input"])
        previous_distance = float(np.abs(measured - previous).sum() / 2)
    return {
        "name": row["name"],
        "job_id": row["job_id"],
        "observation_index": row["observation_index"],
        "compiled_mode_probabilities": compiled,
        "compiled_vs_requested_tvd": float(np.abs(np.asarray(compiled) - requested).sum() / 2),
        "measured_vs_compiled_tvd": float(np.abs(measured - compiled).sum() / 2),
        "measured_vs_preceding_compiled_tvd": previous_distance,
        "experiment_optical_mesh_matches_circuit": _elements(fields["computed_circuit"])
        == _elements(fields["computed_experiment"]),
    }


def audit(path: Path) -> dict[str, Any]:
    from bdsc_certificate import close

    retained = json.loads(path.read_text())
    names = [row["run"] for row in retained["acquisitions"]]
    if any(Path(name).name != name or name in {".", ".."} for name in names):
        raise ValueError("an acquisition must name one retained run directory")
    directories = [ROOT / "results/quandela/runs" / name for name in names]
    fresh = analyze(directories)
    close(retained, fresh, "bound photonic repeat readout")
    if any(row["backends"] != ["qpu:belenos"] for row in retained["acquisitions"]):
        raise ValueError("the 24-mode compilation audit is qualified for Belenos records")
    results = {directory.name: json.loads((directory / "results.json").read_text()) for directory in directories}
    arguments = []
    for row in retained["observations"]:
        entries = results[row["run"]]["iterations"]
        index = row["observation_index"]
        arguments.append((row, entries[index], entries[index - 1] if index else None))
    rows = ordered_map(_row, arguments, min_items=1)
    return {
        "schema": "photonic-compilation-measurement-audit-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "readout": path.resolve().relative_to(ROOT).as_posix(),
        "readout_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": rows,
        "max_compiled_vs_requested_tvd": max(row["compiled_vs_requested_tvd"] for row in rows),
        "max_measured_vs_compiled_tvd": max(row["measured_vs_compiled_tvd"] for row in rows),
        "boundary": (
            "returned numerical meshes are metadata; their agreement with a request does not prove applied controls"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readout", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    record = audit(arguments.readout)
    if arguments.check:
        from bdsc_certificate import close

        close(json.loads(arguments.check.read_text()), record, "photonic compilation audit")
        print("replayed returned meshes and measured conditional distributions")
    elif arguments.out:
        qd.write_json(arguments.out, record, exclusive=True)
        print(f"retained {len(record['rows'])} requested/compiled/measured comparisons")
    else:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
