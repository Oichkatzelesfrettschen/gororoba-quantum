"""The library register covers pinned dependencies and scientific alternatives."""

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from hypercomplex_libraries import (
    ROOT,
    check_execution_coverage,
    check_import_coverage,
    check_inventory_denominator,
    execution_declarations,
    inventory,
    main,
    markdown,
    tracked_imports,
)


def test_inventory_covers_locks_and_independent_roles() -> None:
    records = {row["distribution"]: row for row in inventory()["libraries"]}
    for name in ("libqasm", "qxelarator", "hyprat", "octonion", "python-flint", "cryptography", "qutip"):
        if name not in records or not records[name]["role"]:
            raise RuntimeError(f"missing explained library: {name}")
    if records["hypercomplex-algebra"]["independent_algebra_witness"]:
        raise RuntimeError("a wrapper must not count as an independent witness")
    if records["pyadic"]["hardware_execution"]:
        raise RuntimeError("coefficient arithmetic does not submit quantum jobs")


def test_documented_candidates_and_provider_adapters_have_roles() -> None:
    rows = {row["distribution"]: row for row in inventory()["libraries"]}
    for name in (
        "qiskit-addon-aqc-tensor",
        "qiskit-addon-cutting",
        "qiskit-noise-learning",
        "openquantum-sdk-pennylane",
        "numga",
        "padic",
    ):
        if name not in rows or not rows[name]["documentation_mentions"]:
            raise RuntimeError(f"documented candidate lacks a source-bound role: {name}")
    for prose in ("github", "pypi", "probe", "not", "aur"):
        if prose in rows:
            raise RuntimeError(f"a documentation word became a distribution: {prose}")
    for name in (
        "openquantum-sdk-pennylane",
        "openquantum-sdk-cirq",
        "openquantum-sdk-qrisp",
        "openquantum-mcp",
        "qiskit-experiments",
    ):
        if not rows[name]["hardware_execution"]:
            raise RuntimeError(f"a provider acquisition surface needs an execution boundary: {name}")


def test_runtime_manifest_and_dispatch_pin_discovery(tmp_path: Path) -> None:
    dispatcher = tmp_path / "scripts/kaggle_run.py"
    dispatcher.parent.mkdir()
    manifest = tmp_path / "docs/runtime-pins.txt"
    manifest.parent.mkdir()
    manifest.write_text("manifest-only==1.2.3\n")
    dispatcher.write_text(
        'RUNTIME_PINS_FILE = "docs/runtime-pins.txt"\n'
        'GPU_AER_PINS = {"cu13": ("dispatch-only==4.5.6",)}\n'
        'def submit():\n    raise RuntimeError("dispatcher must remain unexecuted")\n'
    )
    declarations, sources = execution_declarations(tmp_path)
    if declarations["manifest-only"] != {"docs/runtime-pins.txt:1": "1.2.3"}:
        raise RuntimeError("the referenced runtime manifest was omitted")
    if declarations["dispatch-only"] != {"scripts/kaggle_run.py:2:GPU_AER_PINS": "4.5.6"}:
        raise RuntimeError("the dispatch literal was omitted")
    record: dict[str, Any] = {
        "libraries": [{"distribution": name, "declared_versions": pins} for name, pins in declarations.items()],
        "sources_sha256": sources,
    }
    check_execution_coverage(record, tmp_path)
    for name in declarations:
        changed = copy.deepcopy(record)
        changed["libraries"] = [row for row in changed["libraries"] if row["distribution"] != name]
        with pytest.raises(ValueError, match="execution pin coverage differs"):
            check_execution_coverage(changed, tmp_path)
    manifest.write_text("manifest-only==1.2.4\nnew-manifest-pin==3.0\n")
    with pytest.raises(ValueError, match="execution pin coverage differs"):
        check_execution_coverage(record, tmp_path)


def test_retained_execution_inventory_covers_authoritative_sources() -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    check_execution_coverage(record, ROOT)
    rows = {row["distribution"]: row for row in record["libraries"]}
    for name in ("qiskit-aer-gpu-cu13", "custatevec-cu13", "cutensornet-cu13", "cutensor-cu13"):
        if rows[name]["independent_algebra_witness"] or not rows[name]["declared_versions"]:
            raise RuntimeError(f"GPU runtime requires provenance and shared-engine boundaries: {name}")
    for name in ("cvxpy", "scs", "clarabel", "osqp"):
        if rows[name]["independent_algebra_witness"] or "infrastructure:" in rows[name]["role"]:
            raise RuntimeError(f"solver needs a qualified scientific role: {name}")


def test_check_rejects_omitted_requirement_library(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    record["libraries"] = [row for row in record["libraries"] if row["distribution"] != "cryptography"]
    record["coverage_counts"]["distributions"] = len(record["libraries"])
    (tmp_path / "libraries.json").write_text(json.dumps(record))
    monkeypatch.setattr(sys, "argv", ["hypercomplex_libraries.py", "--out", str(tmp_path), "--check"])
    with pytest.raises(ValueError, match="inventory declared library coverage differs: cryptography"):
        main()


def test_multiproduct_workflow_admission_differs_from_cvxpy_installation() -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    rows = {row["distribution"]: row for row in record["libraries"]}
    addon = rows["qiskit-addon-mpf"]
    for text in ("multiproduct-formula", "CVXPY", "2026-10-16", "admission", "solver residuals"):
        if text not in addon["role"]:
            raise RuntimeError(f"multiproduct workflow needs explicit scope: {text}")
    if "not installed" in addon["role"]:
        raise RuntimeError("a historical dependency observation became a current installation claim")
    if "docs/notes/qiskit-ecosystem.md:201" not in addon["role_sources"]:
        raise RuntimeError("the dated optional-workflow decision lost its source")
    if rows["cvxpy"]["observed_host_version"] != "1.9.3":
        raise RuntimeError("the retained host CVXPY observation changed")


@pytest.mark.parametrize("alias", [False, True])
def test_inventory_rejects_duplicate_normalized_distribution_names(alias: bool) -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    duplicate = copy.deepcopy(next(row for row in record["libraries"] if row["distribution"] == "numpy-quaternion"))
    if alias:
        duplicate["distribution"] = "NumPy_Quaternion"
    record["libraries"].append(duplicate)
    with pytest.raises(ValueError, match="distribution names repeat after normalization"):
        check_inventory_denominator(record, ROOT)


@pytest.mark.parametrize(
    "field", ["distributions", "execution_pin_distributions", "execution_pin_declarations", "execution_source_files"]
)
@pytest.mark.parametrize("value", [None, True, 347.0, "347", -1, 999, float("inf"), float("nan")])
def test_inventory_rejects_edited_or_noninteger_counts(field: str, value: Any) -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    record["coverage_counts"][field] = value
    with pytest.raises(ValueError, match=f"inventory coverage count differs: {field}"):
        check_inventory_denominator(record, ROOT)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_inventory_rejects_count_field_membership_changes(change: str) -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    if change == "missing":
        record["coverage_counts"].pop("distributions")
    else:
        record["coverage_counts"]["extra"] = 0
    with pytest.raises(ValueError, match="inventory coverage count fields differ"):
        check_inventory_denominator(record, ROOT)


@pytest.mark.parametrize(
    "source",
    [
        "scripts/hypercomplex_libraries.py",
        "docs/state/hypercomplex-libraries/solver-role-grounding.json",
        "docs/notes/iqm/python-stack-versions.json",
    ],
)
def test_check_rejects_missing_declared_source_hash(
    source: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    record["sources_sha256"].pop(source)
    (tmp_path / "libraries.json").write_text(json.dumps(record))
    (tmp_path / "libraries.md").write_text(markdown(record))
    monkeypatch.setattr(sys, "argv", ["hypercomplex_libraries.py", "--out", str(tmp_path), "--check"])
    with pytest.raises(ValueError, match="inventory declared source coverage differs"):
        main()


def test_check_rejects_extra_source_hash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib

    record = json.loads((ROOT / "docs/state/hypercomplex-libraries/libraries.json").read_text())
    record["sources_sha256"]["AGENTS.md"] = hashlib.sha256((ROOT / "AGENTS.md").read_bytes()).hexdigest()
    (tmp_path / "libraries.json").write_text(json.dumps(record))
    (tmp_path / "libraries.md").write_text(markdown(record))
    monkeypatch.setattr(sys, "argv", ["hypercomplex_libraries.py", "--out", str(tmp_path), "--check"])
    with pytest.raises(ValueError, match="inventory declared source coverage differs"):
        main()


@pytest.fixture
def import_snapshot(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    source = tmp_path / "scripts/consumer.py"
    source.parent.mkdir()
    source.write_text("import numpy\nimport unresolved_probe\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "add", "scripts/consumer.py"], cwd=tmp_path, check=True)
    roots, _ = tracked_imports(tmp_path)
    record: dict[str, Any] = {
        "libraries": [{"distribution": "numpy", "imported_by": ["scripts/consumer.py"]}],
        "tracked_import_roots": roots,
        "import_root_distributions": {"numpy": ["numpy"], "unresolved_probe": []},
        "unresolved_import_roots": ["unresolved_probe"],
    }
    check_import_coverage(record, tmp_path)
    return tmp_path, record


@pytest.mark.parametrize("change", ["add", "remove"])
def test_current_import_scan_rejects_tracked_source_changes(
    import_snapshot: tuple[Path, dict[str, Any]], change: str
) -> None:
    root, record = import_snapshot
    source = root / "scripts/consumer.py"
    if change == "add":
        source.write_text(source.read_text() + "import scipy\n")
    else:
        source.write_text(source.read_text().replace("import numpy\n", ""))
    with pytest.raises(ValueError, match="inventory tracked import roots differ"):
        check_import_coverage(record, root)


@pytest.mark.parametrize("field", ["imported_by", "unresolved", "mapping"])
def test_current_import_projection_rejects_stale_or_noncanonical_fields(
    import_snapshot: tuple[Path, dict[str, Any]], field: str
) -> None:
    root, record = import_snapshot
    if field == "imported_by":
        record["libraries"][0]["imported_by"] = []
        message = "inventory current import locations differ"
    elif field == "unresolved":
        record["unresolved_import_roots"] = []
        message = "inventory unresolved import roots differ"
    else:
        record["import_root_distributions"]["numpy"] = ["NumPy"]
        message = "inventory import distribution mapping is not normalized"
    with pytest.raises(ValueError, match=message):
        check_import_coverage(record, root)
