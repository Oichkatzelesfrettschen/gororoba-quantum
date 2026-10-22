"""The library register covers pinned dependencies and scientific alternatives."""

from hypercomplex_libraries import inventory


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
