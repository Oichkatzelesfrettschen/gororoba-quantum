"""Native cross-checks of our Belenos mesh and postselected-CZ models against Perceval 1.3.1.

Four checks, each an equality or a recorded divergence:

1. unitary: the numeric mesh of qd_belenos_mesh (decode, run_architecture, mesh_phases, unitary) against
   Circuit.compute_unitary() of the served computed_circuit, per retained entry, with the component counts of the
   chip (couplers, phase shifters, Mach-Zehnder cells);
2. optimizer: perceval.utils.algorithms.CircuitOptimizer started from the served phases (first_guess, one trial,
   so no random start runs) over the served architecture with symbolic phases, and Perceval's matrix fidelity of
   our unitary against its own;
3. decomposition: Circuit.decomposition (triangle, BS(theta, phi_tr), PS) of the served 24-mode unitary beside the
   same call on a deterministic dense control, the 24-mode Fourier matrix, each with the circuit's component count
   and largest entry error, and the allow_error retry; the call returns None when it finds no decomposition;
4. cz: the success probability of Catalog "postprocessed cz" with NoiseModel(indistinguishability=M) for each
   rail input against 1/9 (inputs 00, 01, 11) and (5 - 4M)/9 (input 10), the law of
   ascella_cz_tomography_reference_case.rail_rate_ratio, and the success probability of Catalog "heralded cz".

CircuitOptimizer.optimize without first_guess, Matrix.random_unitary and Perceval's own random starts draw from an
unseeded generator, so this module never calls them; a random start needs a value of a retained QRNG draw
(AGENTS.md, Seeds) passed through the optimizer's seed argument.

Usage: "$PYTHON" scripts/qd_perceval_crosscheck.py (--write OUT RUN... | --check OUT RUN... | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import qd_belenos_mesh as mesh_lib  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "qd-perceval-crosscheck-v1"
OVERLAPS = (1.0, 0.8, 0.5, 0.0)
RAIL_INPUTS = {"00": [1, 0, 1, 0], "01": [1, 0, 0, 1], "10": [0, 1, 1, 0], "11": [0, 1, 0, 1]}
DIGITS = 9


class CrosscheckError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CrosscheckError(message)


def served_entries(run: Path) -> list[dict[str, Any]]:
    inner = mesh_lib.raw_result(run)
    return list(inner.get("results_list") or [inner])


def our_success(rail_input: str, overlap: float) -> float:
    """The success law of the postselected CZ in ascella_cz_tomography_reference_case.rail_rate_ratio."""
    return (5.0 - 4.0 * overlap) / 9.0 if rail_input == "10" else 1.0 / 9.0


def cz_success(item: str, rail_input: str, overlap: float) -> float:
    import perceval as pcvl
    from perceval.components import catalog

    experiment = catalog[item].build_experiment()
    processor = pcvl.Processor("SLOS", experiment, noise=pcvl.NoiseModel(indistinguishability=overlap))
    processor.with_input(pcvl.BasicState(RAIL_INPUTS[rail_input]))
    return float(processor.probs()["global_perf"])


def cz_table() -> dict[str, Any]:
    rows = []
    for overlap in OVERLAPS:
        perceval = {i: cz_success("postprocessed cz", i, overlap) for i in RAIL_INPUTS}
        ours = {i: our_success(i, overlap) for i in RAIL_INPUTS}
        ratio = perceval["10"] * perceval["01"] / (perceval["00"] * perceval["11"])
        rows.append(
            {
                "overlap": overlap,
                "perceval": perceval,
                "ours": ours,
                "max_abs_difference": max(abs(perceval[i] - ours[i]) for i in RAIL_INPUTS),
                "rate_ratio_perceval": ratio,
                "rate_ratio_law": 5.0 - 4.0 * overlap,
            }
        )
    heralded = {i: cz_success("heralded cz", i, 1.0) for i in RAIL_INPUTS}
    return {"postprocessed": rows, "heralded_at_overlap_1": heralded, "heralded_law": 2.0 / 27.0}


def served_matrix(entry: dict[str, Any]) -> Any:
    import numpy as np
    from perceval.serialization import deserialize

    return np.array(deserialize(entry["computed_circuit"]).compute_unitary())


def served_unitary(entry: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    from perceval.serialization import deserialize

    circuit = deserialize(entry["computed_circuit"])
    reference = served_matrix(entry)
    elements = mesh_lib.decode(entry["computed_circuit"])
    arch = mesh_lib.run_architecture(elements)
    ours = mesh_lib.unitary(arch, mesh_lib.mesh_phases(arch, elements))
    couplers = sum(1 for kind, _, _ in elements if kind == "bs")
    return {
        "max_abs_difference": float(np.abs(ours - reference).max()),
        "unitarity_error_perceval": float(np.abs(reference @ reference.conj().T - np.eye(len(reference))).max()),
        "couplers": couplers,
        "phase_shifters": len(elements) - couplers,
        "mzi_cells": len(mesh_lib.mzis(arch)),
        "perceval_components": int(circuit.ncomponents()),
    }


def symbolic_template(circuit: Any) -> tuple[Any, list[float]]:
    """The served circuit with every phase shifter symbolic, and the served phase values in component order."""
    from perceval.components import PS, Circuit
    from perceval.utils import P

    template = Circuit(circuit.m)
    phases: list[float] = []
    for modes, component in circuit._components:
        if isinstance(component, PS):
            template.add(modes[0], PS(P(f"phi{len(phases)}")))
            phases.append(float(component.param("phi")))
        else:
            template.add(modes, component)
    return template, phases


def optimizer_check(entry: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    from perceval.serialization import deserialize
    from perceval.utils import Matrix
    from perceval.utils.algorithms.circuit_optimizer import CircuitOptimizer
    from perceval.utils.algorithms.norm import fidelity

    circuit = deserialize(entry["computed_circuit"])
    target = Matrix(np.array(circuit.compute_unitary()))
    template, phases = symbolic_template(circuit)
    result, achieved = CircuitOptimizer(threshold=1e-9, ntrials=1).optimize(target, template, first_guess=phases)
    return {
        "variable_phases": len(phases),
        "optimizer_fidelity": float(achieved),
        "optimized_vs_target_fidelity": float(fidelity(target, Matrix(np.array(result.compute_unitary())))),
    }


def fourier(size: int) -> Any:
    import numpy as np

    index = np.arange(size)
    return np.exp(2j * math.pi * np.outer(index, index) / size) / math.sqrt(size)


def decompose(unitary: Any, **options: Any) -> dict[str, Any]:
    import numpy as np
    from perceval.components import BS, PS, Circuit
    from perceval.utils import InterferometerShape, Matrix, P

    found = Circuit.decomposition(
        Matrix(np.array(unitary)),
        BS(theta=P("theta"), phi_tr=P("phi")),
        phase_shifter_fn=PS,
        shape=InterferometerShape.TRIANGLE,
        max_try=2,
        **options,
    )
    if found is None:
        return {"status": "none", "options": options}
    error = float(np.abs(np.array(found.compute_unitary()) - unitary).max())
    return {"status": "circuit", "options": options, "components": int(found.ncomponents()), "max_abs_error": error}


def stable(result: dict[str, Any]) -> dict[str, Any]:
    """The reproducible part of a decomposition result: allow_error retries draw from an unseeded generator, so
    their component count and error vary between runs and only the error class is kept."""
    if result["status"] == "none":
        return result
    error = result["max_abs_error"]
    kept = {"status": result["status"], "options": result["options"], "error_class": error_class(error)}
    if not result["options"]:
        kept["components"] = result["components"]
    return kept


def error_class(error: float) -> str:
    return "below_1e-6" if error < 1e-6 else "below_1e-2" if error < 1e-2 else "at_least_1e-2"


def decomposition_table(entry: dict[str, Any]) -> dict[str, Any]:
    served = served_matrix(entry)
    size = len(served)
    return {
        "served": [stable(decompose(served)), stable(decompose(served, allow_error=True))],
        "fourier_control": [stable(decompose(fourier(size)))],
        "size": size,
    }


def round_tree(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, DIGITS)
    if isinstance(value, dict):
        return {k: round_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [round_tree(v) for v in value]
    return value


def run_item(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    kind, entry = item
    if kind == "unitary":
        return served_unitary(entry)
    if kind == "optimizer":
        return optimizer_check(entry)
    return decomposition_table(entry)


def record(runs: list[Path]) -> dict[str, Any]:
    import perceval as pcvl

    out = []
    for run in runs:
        entries = served_entries(run)
        items = [("unitary", e) for e in entries] + [("optimizer", entries[0]), ("decomposition", entries[0])]
        results = parallel.ordered_map(run_item, items, min_items=2)
        out.append(
            {
                "run": run.name,
                "unitary": results[: len(entries)],
                "optimizer": results[len(entries)],
                "decomposition": results[len(entries) + 1],
            }
        )
    return round_tree({"schema": SCHEMA, "perceval": pcvl.__version__, "runs": out, "cz": cz_table()})


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def self_test() -> int:
    table = cz_table()
    require(all(row["max_abs_difference"] < 1e-12 for row in table["postprocessed"]), "postselected CZ law")
    require(abs(table["heralded_at_overlap_1"]["10"] - 2.0 / 27.0) < 1e-12, "heralded CZ law")
    result = decompose(fourier(4))
    require(result["status"] == "circuit" and result["max_abs_error"] < 1e-6, f"Fourier control decomposes: {result}")
    print("qd_perceval_crosscheck self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--check", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    mode = args.write or args.check
    if not mode or len(mode) < 2:
        parser.error("--write or --check takes OUT and at least one RUN")
    out, runs = Path(mode[0]), [Path(r) for r in mode[1:]]
    text = dump(record(runs))
    if args.write:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
        return 0
    if out.read_text(encoding="utf-8") != text:
        print(f"{out} differs from the recomputed record", file=sys.stderr)
        return 1
    print(f"{out} matches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
