"""Derive every Quantum Inspire DeMarrais circuit's ideal outcome from its CZ graph and X positions alone.

Each circuit is H on every qubit, a layer of CZ gates, X on the oracle hubs, the same CZ layer, H on every qubit
and a measurement. CZ X_j CZ = X_j Z_N(j) for the CZ neighbourhood N(j), and H maps Z to X, so the output is the
basis state whose bit q is the parity of the X'd hubs adjacent to q in the CZ graph. The replay parses each .cq,
predicts that string from the edge list and hub set, requires it to equal the exact statevector outcome and the
manifest's `ideal_shot_string` (qubit 0 rightmost), and records the circuit's Cayley-Dickson label beside the
gate content, which holds no parameter the label sets.

``--out FILE`` writes the record; ``--check FILE`` recomputes it and requires the retained bytes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[3]
CASES = ROOT / "results/quantum_inspire/cases"
FAMILIES = ("demarrais_tuna17_8192d", "demarrais_qx_1024d")
GATE = re.compile(r"^(H|X|CZ)\s+q\[(\d+)\](?:,\s*q\[(\d+)\])?$")


def parse(path: Path) -> tuple[int, list[tuple[str, tuple[int, ...]]]]:
    text = path.read_text(encoding="utf-8")
    width = int(re.search(r"qubit\[(\d+)\]", text).group(1))  # type: ignore[union-attr]
    gates: list[tuple[str, tuple[int, ...]]] = []
    for line in text.splitlines():
        match = GATE.match(line.strip())
        if match:
            name, a, b = match.groups()
            gates.append((name, (int(a),) if b is None else (int(a), int(b))))
        elif line.strip() and not line.startswith(("version", "//", "qubit", "bit", "barrier", "b = measure")):
            raise ValueError(f"{path}: unparsed line {line!r}")
    return width, gates


def predict(width: int, gates: list[tuple[str, tuple[int, ...]]]) -> tuple[str, list[list[int]], list[int]]:
    """The CZ-neighbour parity of the X'd hubs as a bit string with qubit 0 rightmost, the manifests' order."""
    names = [name for name, _ in gates]
    if names[:width] != ["H"] * width or names[-width:] != ["H"] * width:
        raise ValueError("the circuit does not open and close with H on every qubit")
    middle = gates[width:-width]
    hubs = sorted(qubits[0] for name, qubits in middle if name == "X")
    cz = [(min(qubits), max(qubits)) for name, qubits in middle if name == "CZ"]
    if len(middle) != len(hubs) + len(cz) or len(cz) % 2:
        raise ValueError("the middle of the circuit is not two CZ layers around the X hubs")
    before, after = sorted(cz[: len(cz) // 2]), sorted(cz[len(cz) // 2 :])
    if hubs:
        split = [name for name, _ in middle].index("X")
        if split != len(cz) // 2 or any(name != "X" for name, _ in middle[split : split + len(hubs)]):
            raise ValueError("the X hubs do not sit between the two CZ layers")
    if before != after:
        raise ValueError("the two CZ layers differ")
    bits = [sum(1 for j in hubs if (min(q, j), max(q, j)) in set(before)) % 2 for q in range(width)]
    return "".join(map(str, reversed(bits))), [list(edge) for edge in before], hubs


def statevector_outcome(width: int, gates: list[tuple[str, tuple[int, ...]]]) -> str:
    circuit = QuantumCircuit(width)
    for name, qubits in gates:
        getattr(circuit, name.lower())(*qubits)
    law = Statevector(circuit).probabilities_dict()
    outcomes = [key for key, value in law.items() if value > 1e-9]
    if len(outcomes) != 1:
        raise ValueError(f"the circuit has {len(outcomes)} outcomes, not one")
    return outcomes[0]


def record() -> dict[str, Any]:
    rows = []
    for family in FAMILIES:
        for manifest in sorted((CASES / family).glob("batch-*/cases.json")):
            cases = json.loads(manifest.read_text(encoding="utf-8"))
            for row in cases["circuits"]:
                width, gates = parse(manifest.parent / row["file"])
                predicted, edges, hubs = predict(width, gates)
                exact = statevector_outcome(width, gates)
                if predicted != exact or predicted != row["ideal_shot_string"]:
                    raise ValueError(
                        f"{row['file']}: parity {predicted}, statevector {exact}, manifest {row['ideal_shot_string']}"
                    )
                rows.append(
                    {
                        "family": family,
                        "batch": manifest.parent.name,
                        "file": row["file"],
                        "label": row["kind"],
                        "cayley_dickson_target_dim": cases.get("cayley_dickson_target_dim"),
                        "cz_edges": len(edges),
                        "x_hubs": hubs,
                        "ideal_shot": predicted,
                    }
                )
    return {
        "schema": "demarrais-pauli-propagation-v1",
        "rule": "bit q = parity of the X'd hubs adjacent to q in the circuit's CZ graph",
        "circuits": rows,
    }


def render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    text = render(record())
    if arguments.out:
        arguments.out.write_text(text, encoding="utf-8")
        return 0
    if arguments.check.read_text(encoding="utf-8") != text:
        print(f"{arguments.check}: the recomputed record differs", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
