"""Exercise portable measured HTML with explicitly synthetic temporary fixtures."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import check_extract_measured_ripple as extraction_checks
import extract_measured_ripple as extractor
import render_measured_ripple as renderer


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def seal(value: dict[str, Any]) -> None:
    value.pop("payload_sha256", None)
    value["payload_sha256"] = renderer.digest(renderer.canonical(value))


def move_count(value: dict[str, Any], name: str) -> None:
    counts = value["members"][name]["counts"]
    occupied = next(index for index, count in enumerate(counts) if count > 0)
    counts[occupied] -= 1
    counts[(occupied + 1) % len(counts)] += 1


def snapshot(directory: Path) -> dict[str, tuple[Any, ...]]:
    """Compare names, bytes, identities, link counts, and mtimes, including root."""
    result = {}
    for path in (directory, *sorted(directory.rglob("*"))):
        status = path.lstat()
        identity = (status.st_dev, status.st_ino, status.st_nlink, status.st_mtime_ns)
        if path.is_symlink():
            contents: Any = ("symlink", os.readlink(path))
        elif path.is_file():
            contents = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        else:
            contents = ("directory",)
        result[str(path.relative_to(directory))] = (*contents, *identity)
    return result


def invoke(script: Path, inputs: list[Path], output: Path, check: bool) -> subprocess.CompletedProcess[str]:
    optimization = [f"-{'O' * sys.flags.optimize}"] if sys.flags.optimize else []
    return subprocess.run(
        [
            sys.executable,
            *optimization,
            "-B",
            "-W",
            "error",
            str(script),
            *[argument for path in inputs for argument in ("--evidence", str(path))],
            "--out",
            str(output),
            *(["--check"] if check else []),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> None:
    outcomes: dict[str, Any] = {"evidence_kind": "synthetic_fixture", "shape_rejections": [], "path_rejections": 0}
    with TemporaryDirectory(prefix="measured-ripple-renderer-contract-") as temporary:
        root = Path(temporary)
        payloads = []
        for family in ("ripple", "rank-sector"):
            run = extraction_checks.fixture(root / "synthetic-raw" / family, family)
            payload = json.loads(extractor.canonical(extractor.extract_run(run, fixture_mode=True)))
            require(payload["evidence_kind"] == "synthetic_fixture", "fixture lost evidence label")
            renderer.validate(payload)
            payloads.append(payload)
        inputs = []
        for payload in payloads:
            path = root / ("synthetic-" + payload["family"] + ".json")
            path.write_bytes(renderer.canonical(payload))
            inputs.append(path)
        source = root / "scripts/render_measured_ripple.py"
        source.parent.mkdir()
        source.write_bytes(Path(renderer.__file__).read_bytes())
        template = root / "gororoba_quantum/visualizations/measured_cayley_dickson_ripples.html"
        template.parent.mkdir(parents=True)
        template.write_bytes(renderer.TEMPLATE.read_bytes())
        output = root / "synthetic-measured-ripples.html"
        result = invoke(source, inputs, output, False)
        require(result.returncode == 0, result.stderr)
        require(output.read_text() == renderer.render(payloads), "rendering differs across CLI and function")
        html = output.read_text()
        require("SYNTHETIC FIXTURE" in html and "QPU measurement evidence absent" in html, "fixture labeling absent")
        require(renderer.MARKER not in html, "unreplaced template data marker")
        require('src="http' not in html and 'href="http' not in html, "external content in portable view")
        before = snapshot(root)
        result = invoke(source, inputs, output, True)
        require(result.returncode == 0 and before == snapshot(root), "successful --check changed fixture tree")
        outcomes["successful_check"] = "byte/name/identity/mtime preserving"
        for label, destination in (
            ("missing_output", root / "absent.html"),
            ("missing_parent", root / "absent" / "output.html"),
        ):
            before = snapshot(root)
            result = invoke(source, inputs, destination, True)
            require(result.returncode != 0 and before == snapshot(root), label + " --check wrote fixture tree")
        altered = root / "altered.html"
        altered.write_text("existing fixture content\n")
        for check in (False, True):
            before = snapshot(root)
            result = invoke(source, inputs, altered, check)
            require(result.returncode != 0 and before == snapshot(root), "existing output changed")
        for protected in (*inputs, template):
            symlink = root / (protected.name + ".alias")
            symlink.symlink_to(protected)
            hardlink = root / (protected.name + ".hardlink")
            os.link(protected, hardlink)
            alias_directory = root / (protected.name + ".directory")
            alias_directory.symlink_to(protected.parent, target_is_directory=True)
            nested = root / "canonical-child"
            nested.mkdir(exist_ok=True)
            aliases = (
                protected,
                symlink,
                hardlink,
                alias_directory / protected.name,
                protected.parent / "." / protected.name,
            )
            for destination in aliases:
                for check in (False, True):
                    before = snapshot(root)
                    result = invoke(source, inputs, destination, check)
                    require(result.returncode != 0 and "aliases" in result.stderr, "path alias was admitted")
                    require(before == snapshot(root), "rejected path alias changed fixture tree")
                    outcomes["path_rejections"] += 1
        dangling = root / "dangling-output"
        dangling.symlink_to(root / "missing-target")
        for destination in (dangling, root):
            for check in (False, True):
                before = snapshot(root)
                result = invoke(source, inputs, destination, check)
                require(result.returncode != 0 and before == snapshot(root), "invalid output changed fixture tree")
                outcomes["path_rejections"] += 1
        first = next(iter(payloads[0]["members"]))
        rank_first = next(iter(payloads[1]["members"]))
        mutations: list[tuple[str, int, Callable[[dict[str, Any]], Any]]] = [
            ("schema", 0, lambda value: value.update(schema="unknown")),
            ("evidence_kind", 0, lambda value: value.update(evidence_kind="simulation")),
            ("family", 0, lambda value: value.update(family="unknown")),
            ("count_sum", 0, lambda value: value["members"][first]["counts"].__setitem__(0, 100000)),
            ("boolean_shots", 0, lambda value: value["members"][first].update(shots=True)),
            ("probability_width", 0, lambda value: value["members"][first].update(probabilities=[1])),
            ("probability_value", 0, lambda value: value["members"][first]["probabilities"].__setitem__(0, -0.1)),
            (
                "probability_count",
                0,
                lambda value: move_count(value, first),
            ),
            ("residual", 0, lambda value: value["members"][first]["hardware_minus_ideal"].__setitem__(0, 4)),
            ("shot_block", 0, lambda value: value["members"][first]["shot_order_blocks"][0].update(start_shot=1)),
            ("missing_block", 0, lambda value: value["members"][first].update(shot_order_blocks=[])),
            ("duplicate_pub", 0, lambda value: value["pubs"].append(copy.deepcopy(value["pubs"][0]))),
            ("pub_shots", 0, lambda value: value["pubs"][0].update(shots=33)),
            ("pub_qubits", 0, lambda value: value["pubs"][0].update(active_physical_qubits=[9999])),
            ("raw_hash", 0, lambda value: value["pubs"][0].update(raw_sha256="invalid")),
            ("covariance_shape", 0, lambda value: value["pubs"][0]["event_zero"].update(covariance=[])),
            ("covariance_value", 0, lambda value: value["pubs"][0]["event_zero"]["covariance"][0].__setitem__(0, 1)),
            (
                "duplicate_joint_member",
                0,
                lambda value: value["pubs"][0]["event_zero"]["members"].append(
                    value["pubs"][0]["event_zero"]["members"][0]
                ),
            ),
            ("source_path", 0, lambda value: value["source_files"].update({"../outside": "0" * 64})),
            ("source_hash", 0, lambda value: value["source_files"].update({"record.json": "invalid"})),
            ("throughput_total", 0, lambda value: value["throughput"].update(unique_active_qubit_shots=0)),
            (
                "throughput_rate",
                0,
                lambda value: value["throughput"]["rates_per_charged_second"].update(unique_active_qubit_shots=0),
            ),
            ("unavailable_charge", 0, lambda value: value["throughput"].update(retained_collector_charge_seconds=None)),
            ("rank_normalization", 1, lambda value: value["members"][rank_first]["metadata"].update(alpha_exact="3")),
            (
                "rank_zero_denominator",
                1,
                lambda value: value["members"][rank_first]["metadata"].update(parameter_exact="1/0"),
            ),
            ("endpoint_interval", 0, lambda value: value["endpoint_analysis"]["observables"][0].update(lo=1000)),
        ]
        for label, index, mutate in mutations:
            changed = copy.deepcopy(payloads[index])
            mutate(changed)
            seal(changed)
            try:
                renderer.validate(changed)
            except ValueError:
                outcomes["shape_rejections"].append(label)
            else:
                raise RuntimeError("accepted malformed payload: " + label)
        altered_payload = copy.deepcopy(payloads[0])
        altered_payload["experiment_digest"] = "0" * 64
        try:
            renderer.validate(altered_payload)
        except ValueError as error:
            require("hash differs" in str(error), "hash mutation failed for another reason")
        else:
            raise RuntimeError("accepted changed payload hash")
        for label, values in (("duplicate families", [payloads[0], payloads[0]]), ("empty input", [])):
            try:
                renderer.render(values)
            except ValueError:
                outcomes["shape_rejections"].append(label)
            else:
                raise RuntimeError("accepted " + label)
        mixed = copy.deepcopy(payloads[1])
        mixed["evidence_kind"] = "collected_hardware"
        seal(mixed)
        try:
            renderer.render([payloads[0], mixed])
        except ValueError:
            outcomes["shape_rejections"].append("mixed evidence kinds")
        else:
            raise RuntimeError("mixed synthetic and hardware evidence")
        injected = copy.deepcopy(payloads[0])
        injected["interpretation"].append("</script><script>window.untrusted = true;</script>")
        seal(injected)
        escaped = renderer.render([injected])
        require(
            "</script><script>window.untrusted" not in escaped and "\\u003c/script\\u003e" in escaped,
            "script-closing injection escaped embedding",
        )
        duplicate_json = root / "synthetic-duplicate-key.json"
        duplicate_json.write_text('{"schema":"one","schema":"two"}')
        before = snapshot(root)
        result = invoke(source, [duplicate_json], root / "duplicate.html", False)
        require(
            result.returncode != 0 and "duplicate JSON key" in result.stderr and before == snapshot(root),
            "duplicate key admission wrote fixture tree",
        )
        withheld = copy.deepcopy(payloads[0])
        withheld["endpoint_analysis"] = {"withheld": "synthetic calibration mismatch"}
        seal(withheld)
        require("synthetic calibration mismatch" in renderer.render([withheld]), "withholding reason lost")
        for value in payloads:
            renderer.render([value])
        rounded = copy.deepcopy(payloads[0])
        model_member = next(item for item in rounded["members"].values() if len(item["counts"]) == 32)
        rounded_model = [round(count / 4096, 6) for count in [25] * 31 + [3321]]
        model_member["preparation_model"]["probabilities"] = rounded_model
        model_member["hardware_minus_preparation_model"] = [
            measured - model for measured, model in zip(model_member["probabilities"], rounded_model, strict=True)
        ]
        seal(rounded)
        renderer.validate(rounded)
        require(
            model_member["preparation_model"]["probabilities"] == rounded_model, "renderer renormalized retained model"
        )
        outcomes["six_decimal_model_mass"] = sum(rounded_model)
        model_member["preparation_model"]["probabilities"][0] += 0.0001
        model_member["hardware_minus_preparation_model"][0] -= 0.0001
        seal(rounded)
        try:
            renderer.validate(rounded)
        except ValueError:
            outcomes["shape_rejections"].append("model_serialization_envelope")
        else:
            raise RuntimeError("accepted model mass beyond six-decimal serialization envelope")
        outcomes["families"] = {
            value["family"]: {"members": len(value["members"]), "pubs": len(value["pubs"])} for value in payloads
        }
    print(json.dumps(outcomes, sort_keys=True))


if __name__ == "__main__":
    main()
