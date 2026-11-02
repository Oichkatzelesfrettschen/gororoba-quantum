"""Perceval linear-optics behavior the Quandela scripts rely on, checked against two-photon interference answers."""

from __future__ import annotations

import numpy as np
import perceval as pcvl
from perceval.serialization import deserialize, serialize
from perceval.utils.conversion import probs_to_sample_count

ONE_ONE = pcvl.BasicState([1, 1])


def balanced() -> pcvl.Circuit:
    return pcvl.Circuit(2) // pcvl.BS.H()


def test_hong_ou_mandel_dip_on_the_slos_backend() -> None:
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(np.asarray(balanced().compute_unitary()))))
    backend.set_input_state(ONE_ONE)
    distribution = backend.prob_distribution()
    if abs(float(distribution.get(ONE_ONE, 0.0))) > 1e-12:
        raise AssertionError("indistinguishable photons must never exit one per mode")
    if not np.isclose(sum(float(value) for value in distribution.values()), 1.0):
        raise AssertionError(distribution)


def test_noise_model_distinguishability_restores_coincidences() -> None:
    processor = pcvl.Processor("SLOS", balanced(), noise=pcvl.NoiseModel(indistinguishability=0.0))
    processor.with_input(ONE_ONE)
    processor.min_detected_photons_filter(2)
    results = processor.probs()["results"]
    if not np.isclose(float(results.get(ONE_ONE, 0.0)), 0.5, atol=1e-9):
        raise AssertionError(f"distinguishable photons exit one per mode half the time: {results}")


def test_serialization_round_trip_and_sample_conversion() -> None:
    circuit = balanced() // (1, pcvl.PS(0.25))
    restored = deserialize(serialize(circuit))
    if not np.allclose(np.asarray(restored.compute_unitary()), np.asarray(circuit.compute_unitary())):
        raise AssertionError("serialize/deserialize changed the circuit unitary")
    distribution = pcvl.BSDistribution({pcvl.BasicState([2, 0]): 0.5, pcvl.BasicState([0, 2]): 0.5})
    counts = probs_to_sample_count(distribution, count=1000)
    # The conversion samples: 1000 draws at p = 1/2 put each count within 100 (over six standard deviations) of 500.
    if (
        sum(counts.values()) != 1000
        or set(counts) - set(distribution)
        or any(abs(counts[s] - 500) > 100 for s in counts)
    ):
        raise AssertionError(f"counts stray from an even two-state distribution: {counts}")
