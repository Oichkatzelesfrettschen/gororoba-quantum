"""Construct unassigned logical readout-context circuit alternatives.

The circuit list is a source catalogue, not an execution schedule. The caller
must establish an approved allocation, native layout, ordering, cost and timing.
The circuits do not submit, compile or authenticate provider data.
"""

from qiskit import QuantumCircuit


def actor_alternatives(
    width: int, reporter_bits: tuple[int, int], actor_bits: tuple[int, ...]
) -> dict[tuple[str, int], QuantumCircuit]:
    """Build unassigned preparation alternatives, without asserting equal timing."""
    if (
        type(width) is not int
        or width < 2
        or type(reporter_bits) is not tuple
        or len(reporter_bits) != 2
        or any(type(bit) is not int or not 0 <= bit < width for bit in reporter_bits)
        or len(set(reporter_bits)) != 2
        or type(actor_bits) is not tuple
        or not actor_bits
        or any(type(bit) is not int or not 0 <= bit < width for bit in actor_bits)
        or len(set(actor_bits)) != len(actor_bits)
        or bool(set(actor_bits) & set(reporter_bits))
    ):
        raise ValueError("actor and reporter bits must be distinct members of the measured register")
    circuits: dict[tuple[str, int], QuantumCircuit] = {}
    for arm in ("idle", "active"):
        for input_bits in range(4):
            circuit = QuantumCircuit(width, width, name=f"actor-{arm}-input-{input_bits:02b}")
            for position, bit in enumerate(reporter_bits):
                if (input_bits >> position) & 1:
                    circuit.x(bit)
            if arm == "active":
                circuit.x(actor_bits)
            circuit.barrier()
            circuit.measure(range(width), range(width))
            circuits[(arm, input_bits)] = circuit
    return circuits


def padded_actor_alternatives(
    width: int, reporter_bits: tuple[int, int], actor_bits: tuple[int, ...], x_duration_ticks: tuple[int, ...]
) -> dict[tuple[str, int], QuantumCircuit]:
    """Pad logical arms using caller-supplied X durations; compiled timing remains a separate gate."""
    alternatives_by_arm = actor_alternatives(width, reporter_bits, actor_bits)
    if (
        type(x_duration_ticks) is not tuple
        or len(x_duration_ticks) != width
        or any(type(ticks) is not int or ticks <= 0 for ticks in x_duration_ticks)
    ):
        raise ValueError("one positive integer X duration is required per measured logical qubit")
    preparation_ticks = max(x_duration_ticks[bit] for bit in (*reporter_bits, *actor_bits))
    padded: dict[tuple[str, int], QuantumCircuit] = {}
    for arm, input_bits in alternatives_by_arm:
        selected = {bit for position, bit in enumerate(reporter_bits) if (input_bits >> position) & 1}
        if arm == "active":
            selected.update(actor_bits)
        circuit = QuantumCircuit(width, width, name=f"actor-{arm}-input-{input_bits:02b}-padded")
        for bit in range(width):
            if bit in selected:
                circuit.x(bit)
            delay_ticks = preparation_ticks - (x_duration_ticks[bit] if bit in selected else 0)
            if delay_ticks:
                circuit.delay(delay_ticks, bit, unit="dt")
        circuit.barrier()
        circuit.measure(range(width), range(width))
        padded[(arm, input_bits)] = circuit
    return padded


def alternatives(width: int, target_bits: tuple[int, int]) -> dict[tuple[str, int], QuantumCircuit]:
    """Prepare all two-bit inputs under fixed-register sparse and dense contexts."""
    if (
        type(width) is not int
        or width < 2
        or type(target_bits) is not tuple
        or len(target_bits) != 2
        or any(type(bit) is not int or not 0 <= bit < width for bit in target_bits)
        or target_bits[0] == target_bits[1]
    ):
        raise ValueError("two distinct target qubits must belong to the measured register")
    circuits: dict[tuple[str, int], QuantumCircuit] = {}
    for context in ("sparse", "dense"):
        for input_bits in range(4):
            circuit = QuantumCircuit(width, width, name=f"{context}-input-{input_bits:02b}")
            for position, qubit in enumerate(target_bits):
                if (input_bits >> position) & 1:
                    circuit.x(qubit)
            if context == "dense":
                for qubit in range(width):
                    if qubit not in target_bits:
                        circuit.x(qubit)
            circuit.barrier()
            circuit.measure(range(width), range(width))
            circuits[(context, input_bits)] = circuit
    return circuits
