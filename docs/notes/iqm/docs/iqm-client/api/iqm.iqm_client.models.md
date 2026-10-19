> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 73624170d96281ee5b1874a23f21b4b598bc1947c0b0983494a9f20f4fa23e54.

# models

Full path: iqm.iqm_client.models

Data models used by IQMClient.

We currently support the following native operations for circuit execution, represented by `iqm.pulse.CircuitOperation`:

| name | \# of qubits | args | description |
|----|----|----|----|
| measure | \>= 1 | `key: str`, `feedback_key: str` | Measurement in the Z basis. |
| prx | 1 | `angle: float`, `phase: float` | Phased x-rotation gate. |
| cc_prx | 1 | `angle: float`, `phase: float`, `feedback_qubit: str`, `feedback_key: str` | Classically controlled PRX gate. |
| reset | \>= 1 |  | Reset the qubit(s) to \\\|0\rangle\\. |
| cz | 2 |  | Controlled-Z gate. |
| move | 2 |  | Move a qubit state between a qubit and a computational resonator, as long as at least one of the components is in the \\\|0\rangle\\ state. |
| barrier | \>= 1 |  | Execution barrier. |
| delay | \>= 1 | `duration: float` | Force a delay between circuit operations. |

## Measure

[`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "(in iqm.pulse v15.0.0)")

Measurement in the computational (Z) basis. The measurement results are the output of the circuit. Takes two string arguments: `key`, denoting the measurement key the returned results are labeled with, and `feedback_key`, which is only needed if the measurement result is used for classical control within the circuit. All the measurement keys and feedback keys used in a circuit must be unique (but the two groups of keys are independent namespaces). Each qubit may be measured multiple times, i.e. mid-circuit measurements are allowed.

Example

``` python
CircuitOperation(name='measure', locus=('alice', 'bob', 'charlie'), args={'key': 'm1'})
```

## PRX

[`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "(in iqm.pulse v15.0.0)")

Phased x-rotation gate, i.e. an x-rotation conjugated by a z-rotation. Takes two arguments, the rotation angle `angle` and the phase angle `phase`, both measured in units of radians. The gate is represented in the standard computational basis by the matrix

\\\text{PRX}(\theta, \phi) = \exp(-i (X \cos (\phi) + Y \sin (\phi)) \\ \theta/2) = \text{RZ}(\phi) \\ \text{RX}(\theta) \\ \text{RZ}^\dagger(\phi),\\

where \\\theta\\ = `angle`, \\\phi\\ = `phase`, and \\X\\ and \\Y\\ are Pauli matrices.

Example

``` python
CircuitOperation(name='prx', locus=('bob',), args={'angle': 1.4 * pi, 'phase': 0.5 * pi})
```

## CC_PRX

[`iqm.pulse.gates.conditional`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.html#module-iqm.pulse.gates.conditional "(in iqm.pulse v15.0.0)")

Classically controlled PRX gate. Takes four arguments. `angle` and `phase` are exactly as in PRX. `feedback_key` is a string that identifies the `measure` instruction whose result controls the gate (the one that shares the feedback key). `feedback_qubit` is the name of the physical qubit within the `measure` instruction that produces the feedback. If the measurement result is 1, the PRX gate is applied. If it is 0, an identity gate of similar time duration gate is applied instead. The measurement instruction must precede the classically controlled gate instruction in the quantum circuit.

## Reset

[`iqm.pulse.gates.reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "(in iqm.pulse v15.0.0)")

Resets the qubit(s) non-unitarily to the \\\|0\rangle\\ state.

Example

``` python
CircuitOperation(name='reset', locus=('alice', 'bob'), args={})
```

Note

Currently inherits its calibration from `cc_prx` and is only available when `cc_prx` is.

## CZ

[`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "(in iqm.pulse v15.0.0)")

Controlled-Z gate. Represented in the standard computational basis by the matrix

\\\text{CZ} = \text{diag}(1, 1, 1, -1).\\

It is symmetric wrt. the qubits it’s acting on, and takes no arguments.

Example

``` python
CircuitOperation(name='cz', locus=('alice', 'bob'), args={})
```

## MOVE

[`iqm.pulse.gates.move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html#module-iqm.pulse.gates.move "(in iqm.pulse v15.0.0)")

The MOVE operation is a unitary population exchange operation between a qubit and a resonator. Its effect is only defined in the invariant subspace \\S = \text{span}\\\|00\rangle, \|01\rangle, \|10\rangle\\\\, where it swaps the populations of the states \\\|01\rangle\\ and \\\|10\rangle\\. Its effect on the orthogonal subspace is undefined.

MOVE has the following presentation in the subspace \\S\\:

\\\text{MOVE}\_S = \|00\rangle \langle 00\| + a \|10\rangle \langle 01\| + a^{-1} \|01\rangle \langle 10\|,\\

where \\a\\ is an undefined complex phase that is canceled when the MOVE gate is applied a second time.

To ensure that the state of the qubit and resonator has no overlap with \\\|11\rangle\\, it is recommended that no single qubit gates are applied to the qubit in between a pair of MOVE operations.

Example

``` python
CircuitOperation(name='move', locus=('alice', 'resonator'), args={})
```

Note

MOVE is only available in quantum computers with the IQM Star architecture.

## Barrier

[`iqm.pulse.gates.barrier`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.html#module-iqm.pulse.gates.barrier "(in iqm.pulse v15.0.0)")

Affects the physical execution order of the instructions elsewhere in the circuit that act on qubits spanned by the barrier. It ensures that any such instructions that succeed the barrier are only executed after all such instructions that precede the barrier have been completed. Hence it can be used to guarantee a specific causal order for the other instructions. It takes no arguments, and has no other effect.

Example

``` python
CircuitOperation(name='barrier', locus=('alice', 'bob'), args={})
```

Note

One-qubit barriers will not have any effect on circuit’s compilation and execution. Higher layers that sit on top of IQM Client can make actual use of one-qubit barriers (e.g. during circuit optimization), therefore having them is allowed.

## Delay

[`iqm.pulse.gates.delay`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.html#module-iqm.pulse.gates.delay "(in iqm.pulse v15.0.0)")

Forces a delay between the preceding and following circuit operations. It can be applied to any number of qubits. Takes one argument, `duration`, which is the minimum duration of the delay in seconds. It will be rounded up to the nearest possible duration the hardware can handle.

Example

``` python
CircuitOperation(name='delay', locus=('alice', 'bob'), args={'duration': 80e-9})
```

Note

We can only guarantee that the delay is *at least* of the requested duration, due to both hardware and practical constraints, but could be much more depending on the other operations in the circuit. To see why, consider e.g. the circuit

``` python
(
    CircuitOperation(name='cz', locus=('alice', 'bob'), args={}),
    CircuitOperation(name='delay', locus=('alice',), args={'duration': 1e-9}),
    CircuitOperation(name='delay', locus=('bob',), args={'duration': 100e-9}),
    CircuitOperation(name='cz', locus=('alice', 'bob'), args={}),
)
```

In this case the actual delay between the two CZ gates will be 100 ns rounded up to hardware granularity, even though only 1 ns was requested for alice.

Module Attributes

|  |  |
|----|----|
| [`STANDARD_DD_STRATEGY`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.STANDARD_DD_STRATEGY.html#iqm.iqm_client.models.STANDARD_DD_STRATEGY "iqm.iqm_client.models.STANDARD_DD_STRATEGY") | The default DD strategy uses the following gate sequences: |

Functions

|  |  |
|----|----|
| [`validate_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.validate_circuit.html#iqm.iqm_client.models.validate_circuit "iqm.iqm_client.models.validate_circuit")(circuit) | Validates a submitted quantum circuit. |

Classes

|  |  |
|----|----|
| [`CircuitCompilationOptions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") | Various discrete options for quantum circuit compilation to pulse schedule. |
| [`CircuitJobParameters`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitJobParameters.html#iqm.iqm_client.models.CircuitJobParameters "iqm.iqm_client.models.CircuitJobParameters") | Parameters for a circuit execution job (see `CircuitJobDefinition` for definitions). |

Inheritance

![Inheritance diagram of iqm.iqm_client.models](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-5b7d01b9a1bc4c2ee64b69403731dc12a8513268.png)
