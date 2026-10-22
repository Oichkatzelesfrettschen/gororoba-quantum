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
