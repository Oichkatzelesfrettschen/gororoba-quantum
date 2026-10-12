"""Check N21 probe provenance with real native-Qiskit computations."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch


def _run_probe(probe_path: Path, source_root: Path, output_path: Path, *, mutate: bool = False) -> None:
    import qiskit

    specification = importlib.util.spec_from_file_location("n21_probe_fixture", probe_path)
    if specification is None or specification.loader is None:
        raise RuntimeError("Cannot load temporary probe")
    probe = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(probe)
    real_transpile = qiskit.transpile
    source_changed = False

    def transpile(*arguments: Any, **keywords: Any) -> Any:
        nonlocal source_changed
        if mutate and not source_changed:
            with probe_path.open("a", encoding="utf-8") as destination:
                destination.write("\n# Temporary regression mutation during native transpilation.\n")
            source_changed = True
        return real_transpile(*arguments, **keywords)

    arguments = [str(probe_path), "--source-root", str(source_root), "--output", str(output_path)]
    with (
        patch.object(sys, "argv", arguments),
        patch.object(qiskit, "transpile", transpile),
        redirect_stdout(io.StringIO()),
    ):
        probe.main()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[3])
    arguments = parser.parse_args()
    source_root = arguments.source_root.resolve(strict=True)
    bundle = Path(__file__).resolve().parent
    historical_bytes = (bundle / "result.json").read_bytes()
    historical = json.loads(historical_bytes)
    archive = (bundle / "historical_probe.py.gz").read_bytes()
    if hashlib.sha256(gzip.decompress(archive)).hexdigest() != historical["probe_sha256"]:
        raise RuntimeError("Archived probe differs from the historical result's recorded source digest")
    if archive[4:8] != bytes(4):
        raise RuntimeError("Historical probe gzip timestamp must be zero")
    source_bytes = (bundle / "probe.py").read_bytes()

    with tempfile.TemporaryDirectory(prefix="n21-probe-provenance-") as temporary_directory:
        temporary = Path(temporary_directory)
        probe_path = temporary / "probe.py"
        probe_path.write_bytes(source_bytes)
        output_path = temporary / "unchanged.json"
        _run_probe(probe_path, source_root, output_path)
        successful_bytes = output_path.read_bytes()
        successful = json.loads(successful_bytes)
        if successful["probe_sha256"] != hashlib.sha256(source_bytes).hexdigest():
            raise RuntimeError("Unchanged probe output carries the wrong executed-source digest")
        if successful["results"] != historical["results"]:
            raise RuntimeError("Native probe results differ from the retained multiplier checks")

        try:
            _run_probe(probe_path, source_root, output_path)
        except FileExistsError:
            pass
        else:
            raise RuntimeError("Probe accepted an existing output path")
        if output_path.read_bytes() != successful_bytes:
            raise RuntimeError("Probe changed the existing output")

        changed_output = temporary / "changed-source.json"
        try:
            _run_probe(probe_path, source_root, changed_output, mutate=True)
        except RuntimeError as error:
            if str(error) != "probe source changes during the probe":
                raise RuntimeError("Mutation failed outside the probe-source guard") from error
        else:
            raise RuntimeError("Probe accepted a source mutation during native computation")
        if probe_path.read_bytes() == source_bytes:
            raise RuntimeError("Source mutation fixture did not edit the executed probe")
        if changed_output.exists():
            raise RuntimeError("Changed-source probe created an output")
        if output_path.read_bytes() != successful_bytes:
            raise RuntimeError("Source mutation changed the existing output")

    if (bundle / "result.json").read_bytes() != historical_bytes:
        raise RuntimeError("Historical result bytes changed during regression")
    print("N21 probe: native results, source mutation rejection, exclusive output, and historical source archive pass")


if __name__ == "__main__":
    main()
