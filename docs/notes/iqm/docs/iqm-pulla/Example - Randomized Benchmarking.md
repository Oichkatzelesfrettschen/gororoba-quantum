> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/Example%20-%20Randomized%20Benchmarking.html](https://docs.iqm.tech/4.7/iqm-pulla/Example%20-%20Randomized%20Benchmarking.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c57f63ed447b6c8efad19e08e17f5fd5f3e67932dcaf3d180432ba4c8c4ea5cc.

Note: Randomized Benchmarking is a somewhat heavy experiment, and the version implemented in this notebook will take several minutes to run.

# Import required packages

```
from __future__ import annotations

from itertools import chain
import math

from IPython.core.display import HTML
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import HGate, SGate
from qiskit.quantum_info import Clifford, random_clifford
import qiskit.quantum_info as qi
from qiskit.visualization import plot_histogram

from iqm.pulse.playlist.visualisation.base import inspect_playlist
from iqm.iqm_client.util import print_env_vars
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.pulse_level_utils import qiskit_to_iqm, sweep_job_to_qiskit

# Matplotlib settings
mpl.rcParams['figure.dpi'] = 500
```

# Set up connection to the quantum computer

```
print_env_vars()

provider = IQMProvider()
backend = provider.get_backend()
iqm_client = backend.client
compiler = iqm_client.get_standard_compiler()
```

# Clifford Randomized Benchmarking

NB: Familiarity with quantum channels, gates and Clifford gates is assumed.

## Function to generate Clifford RB circuits

The idea behind Clifford Randomized Benchmarking (CRB) is that under certain (simplified) types of noise, the average survival probability of the initial state of a quantum system under uniformly random sequences of multi-qubit Clifford gates with sequence inversion will decay exponentially in the length of the sequences. From such decay, one can in turn infer the average fidelity of the corresponding Clifford group.

CRB sequences are of the form \$\$\mathcal{S}*m:=\mathcal{C}*{m+1}\circ\mathcal{C}\_m\circ\cdots\circ\mathcal{C}\_1,\$\$ for any \$m\geq1\$, where \$\mathcal{C}*i(\cdot):=C_i(\cdot)C_i^\dagger\$ is a unitary channel with \$C_i\$ being a Clifford gate, and where by definition \$\$\mathcal{C}*{m+1}=(\mathcal{C}\_m\circ\cdots\circ\mathcal{C}*1)^{-1}.\$\$ It is important to notice that \$C*{m+1}\$ is itself a Clifford gate, i.e., one would not implement the sequence \$\mathcal{C}\_m\circ\cdots\circ\mathcal{C}*1\$ in practice, but rather compile the corresponding unitary operator \$C_mC*{m-1}\cdots{C}\_1\$ into a single Clifford gate.

The main assumption is that the real noisy gates can be approximately modeled independently by a quantum channel \$\mathcal{E}\$ (completely positive, trace non-increasing map) as \$\tilde{\mathcal{C}}\_i\approx\mathcal{E}\circ\mathcal{C}\_i\$, or (ultimately equivalently) as \$\tilde{\mathcal{C}}\_i\approx\mathcal{C}\_i\circ\mathcal{E}\$. This implies that the noise is modeled as **Markovian**, **time-stationary** and **gate-independent** — while here we will take these for granted, a lot about RB in more general regimes is known, but it is in general more complicated, and often this simplistic scenario goes a long way as a useful first approximation.

```
def circuit_crb_dd(n_qubits: int, seq_length: int) -> QuantumCircuit:
    """Generates a random circuit with gates uniformly sampled at random from multi-qubit Clifford group, with final measurement.

    Arguments:
        n_qubits: Number of qubits where RB will be done
        seq_length: The RB sequence length
    Returns:
        A circuit with Clifford RB on n_qubits and idling on an ancilla qubit
    """
    # Initialize the full RB + dd_qubit quantum circuit
    qc = QuantumCircuit(n_qubits + 1)

    # Initialize a circuit to compile the inverse of the RB sequence
    qc_inv = QuantumCircuit(n_qubits)

    # Fix the gate
    h_gate = HGate()
    s_gate = SGate()
    circuit = QuantumCircuit(1)
    circuit.append(h_gate, [0])
    circuit.barrier([0])
    circuit.append(s_gate, [0])
    clifford_dd_qubit = circuit.to_instruction()

    for m in range(seq_length):
        # Sample a random Clifford
        clifford = random_clifford(n_qubits).to_instruction()

        # Compose the sampled Clifford in the circuit and add a barrier
        qc.compose(clifford, qubits=list(range(n_qubits)), inplace=True)
        qc_inv.compose(clifford, qubits=list(range(n_qubits)), inplace=True)

        # The base case will be for seq_length=1 !
        if m == 0:
            qc.compose(clifford_dd_qubit, qubits=[n_qubits], inplace=True)
            qc.barrier()  # NB: mind the barriers!
        elif m == seq_length - 1:
            continue
        else:
            qc.barrier(list(range(n_qubits)))

    # Compile and compose the inverse
    qc.barrier()
    compiled_inverse_clifford = Clifford(qc_inv).to_instruction().inverse()
    qc.compose(compiled_inverse_clifford, qubits=list(range(n_qubits)), inplace=True)

    qc.compose(clifford_dd_qubit.inverse(), qubits=[n_qubits], inplace=True)

    # Add measurement
    qc.measure_all()

    return qc
```

## Fix the number of qubits

NB: CRB is not generally intended to work for \$n\>2\$, both because of the scaling of the size of the \$n\$-qubit Clifford group in \$n\$, and because such gates have to eventually be transpiled to a native basis of 1Q and 2Q gates!

```
qubit_indices = [3]
num_qubits = len(qubit_indices)
dd_qubit = [2]
```

## Inspect a circuit sample - pick an arbitrary sequence length

```
sample_length = 4
crb_circuit_sample = circuit_crb_dd(num_qubits, sample_length)
crb_circuit_sample.draw(output='mpl', fold=-1, style='iqp')
```

## Check that the circuit implements an identity modulo a phase

```
sample_operator = crb_circuit_sample.copy()
sample_operator.remove_final_measurements()
op = qi.Operator(sample_operator)
is_id = op.equiv(qi.Pauli('I' * (num_qubits + 1)))
print(f"The unitary of the circuit implements identity: {is_id}")
display(op.draw(output="latex"))
```

## Transpiling the circuit to IQM’s backend

```
# Set an optimization level for Qiskit's optimizer
qiskit_optim_level = 1
```

**Important:** While a high level of optimization in transpile is usually desirable, one must be careful for the optimization not to mess with the Clifford gates, i.e., we want the transformations between barriers in the circuit to implement a Clifford regardless of how it is decomposed. The specific decomposition still matters, however, because the (average) number of 2Q and 1Q gates (i.e., `cz` and `r`, respectively) will dictate how noisily we can implement the Cliffords on average, i.e., the average gate fidelity we will ultimately obtain.

We will not do this check here, but it is now known that a *good* decomposition of Clifford gates in our basis will have on average 8.25 `cz` gates and 1.5 `r` gates (e.g., see [arXiv:1402.4848](https://arxiv.org/abs/1402.4848)).

**NOTE:** When transpiling a circuit with MOVE gates, you might need to set `optimization_level` lower. If `optimization_level` is set too high, the transpiler might add single qubit gates onto the resonator, which is not supported by the IQM Star architectures. If this in undesired, it is best to have the transpiler add the MOVE gates automatically, rather than manually adding them to the circuit.

```
crb_circuit_sample_transp = transpile(
    crb_circuit_sample,  # The circuit to be transpiled
    backend=backend,  # The backend to transpile to
    optimization_level=qiskit_optim_level,
    initial_layout=qubit_indices + dd_qubit,  # The initial mapping of virtual to physical qubits
)
```

We can count the number of native 1Q and 2Q gates by using the circuit attribute `count_ops()`

## Averaging RB sequences over Clifford gates

One important reason why CRB works –and why specifically it uses Clifford gates–, is that the uniformly distributed multi-qubit Clifford group forms a unitary 2-design. This essentially means that any quantity that takes two copies of the pair \$C, C^\dagger\$ and then averaged over all possible \$C\$s, will be exactly the same as if \$C\$ had been *any* uniformly distributed (so-called Haar) random unitary. This matters because there are plenty of results allowing to easily compute such quantities (i.e., second moments) over the whole uniformly distributed unitary group — in fact, such second moment simply takes the form of a depolarizing channel (RB precisely extracts the average gate fidelity through the corresponding polarization parameter).

The CRB sequences are quantities of this type because of the final inverse at the end (i.e. all sequences will have 2 copies of pairs \$C_i,C_i^\dagger\$ for all \$i=1,2,\ldots,m\$). This is the reason why the theory behind RB, under the noise assumptions above, can ensure that the decay in average fidelity, i.e., quantities like \$\$f_0=\langle0\|\mathcal{S}\_m(\|0\rangle!\langle0\|)\|0\rangle\$\$ take the form of a function \$\$f_0=Ap^m+B\$\$ for \$0\leq{A,B,p}\leq1\$.

Furthermore, it ensures that \$p\$ will encode the average gate fidelity of the noisy Clifford gates, whilst \$A,B\$ will encode (and isolate) errors due to state preparation and measurement. This is what is meant by RB being SPAM-robust. In the modeling with assummptions of noisy gates above, this means \$p\sim\int{d}\psi\langle\psi\|\mathcal{E}(\|\psi\rangle!\langle\psi\|)\|\psi\rangle\$ for all possible uniformly distributed pure states \$\|\psi\rangle\$, and \$A\sim\langle0\|\mathcal{E}*\text{spam}(\|0\rangle!\langle0\|)\|0\rangle\$, \$B\sim\langle0\|\mathcal{E}*\text{spam}(\mathbb{I}/2^n)\|0\rangle\$ for a composition of the state preparation and measurement noise.

## Execute on IQM’s backend

We may now fix a number of circuit samples and sequence lengths.

Despite the Clifford group having a (super) exponential amount of terms (e.g., 24 for 1Q, then 11,520 for 2Q), approximating the average over the whole group with finite samples quickly converges to the Haar average.

On the other hand, the sequence lengths can be chosen as exponentially spaced and aiming at long sequences, if possible, serves to better determine the offset constant (often named the *nuisance* parameter, for obvious reasons) in the decay.

```
num_circuit_samples = 25
sequence_lengths = np.geomspace(1, 400, num=8, endpoint=True, dtype=int).tolist()
```

Depending on how many circuits we want to execute, we could either generate all circuit samples for all circuit lengths and send all for execution once, or we may, for example, generate a given amount of circuits, send them to execution while meanwhile continuing to generate circuits and sending them. In either case, one may retrieve the results later.

Here we will generate all circuits for all sequence lengths, and send them to execute as a single batch on the backend.

### Function to generate a number of Clifford RB circuit samples for given sequence lengths

It is generally a good idea to store (at least at this stage) both the abstract and the transpiled circuits, so that we can inspect them later on.

```
def generate_crb_samples(
    num_samples:int,
    seq_lengths: list[int],
    qiskit_optim_level: int = 1,
    ini_layout: list[int] = qubit_indices + dd_qubit,
) -> tuple[dict[int, list[QuantumCircuit]], dict[int, list[QuantumCircuit]]]:
    """Generates a number of crb circuit samples at given sequence lengths.

    Arguments:
        num_samples: the number of crb circuit samples
        seq_lengths: the sequence lengths of the samples
    Returns:
        Mapping of sequence lengths to CRB circuits of that length (raw and transpiled).
    """
    # We will use a dictionary to store all circuits, with keys being sequence lenghts
    all_samples = {}
    all_samples_transpiled = {}

    for m in seq_lengths:
        samples_at_length_m = []
        samples_at_length_m_transpiled = []
        for _ in range(num_samples):
            circuit_samples = circuit_crb_dd(num_qubits, m)
            transpiled_circuit_samples = transpile(
                circuit_samples, backend=backend, optimization_level=qiskit_optim_level, initial_layout=ini_layout
            )
            samples_at_length_m.append(circuit_samples)
            samples_at_length_m_transpiled.append(transpiled_circuit_samples)

        all_samples[m] = samples_at_length_m
        all_samples_transpiled[m] = samples_at_length_m_transpiled

    return all_samples, all_samples_transpiled
```

```
all_samples, all_samples_transpiled = generate_crb_samples(num_circuit_samples, sequence_lengths)
```

We can inspect the circuits just as a sanity check

```
# Pick one of the sequence lengths
m_ex = sequence_lengths[2]

# Pick one of the samples
sample_ex = 5

# Display circuits
display(all_samples[m_ex][sample_ex].draw(output='mpl', style='iqp', fold=0))
display(all_samples_transpiled[m_ex][sample_ex].draw(output='mpl', style='iqp', fold=0))
```

**Task**: Count the average number of 1Q and 2Q gates in the circuits for each sequence length.

**Task**: Since the Clifford group is a 2-design, its so-called *frame potential* (see e.g., [arXiv:1610.04903](https://arxiv.org/abs/1610.04903)) has to satisfy \$\displaystyle{\sum\_{k,,k^\prime=1}^K}\left\|\mathrm{tr}\left(C\_{k^\prime}^{\dagger}C_k\right)\right\|^4/K^2 = 2\$. Verify this condition for the 1Q Clifford group. **warning** for the 2Q Clifford group: there are in total \$n=11,520^2 = 132,710,400\$ values in the sum! It suffices to compute the values in a triangular part of the matrix \$U\_{k^\prime}^{\dagger}U_k\$ — so you can definitely verify this property, however there will still be \$n(n-1)/2\$ such terms for your computer to sum up!

### Submit circuits to execute

We can now send the transpiled circuits to be run on the hardware.

NB: It is generally preferable to use `backend.run` instead of `execute` command, since the latter performs a transpilation pass “under the hood”.

```
compiler.show_stages()
```

```
from iqm.station_control.interface.executor_interface import JobTracker
from exa.common.data.setting_node import SettingNode
from iqm.station_control.interface.models import MoveGateFrameTrackingMode, RunDefinition

shots = 5000

def set_settings(settings: SettingNode, shots: int) -> None:
    """Set the compilation and execution settings."""
    # provide DDStrategy in settings: [(5, "YXYX", "center")]
    settings.stages.dynamical_decoupling.apply_dd_strategy.dd_is_disabled = False
    settings.stages.dynamical_decoupling.apply_dd_strategy.DDStrategy_gate_sequences_ratio = [5]
    settings.stages.dynamical_decoupling.apply_dd_strategy.DDDStrategy_gate_sequences_gate_pattern_xy = [
        [
            (math.pi, math.pi / 2),
            (math.pi, 0),
            (math.pi, math.pi / 2),
            (math.pi, 0),
         ],
        ]
    settings.stages.dynamical_decoupling.apply_dd_strategy.DDStrategy_gate_sequences_align = ["center"]
    settings.stages.dynamical_decoupling.apply_dd_strategy.DDStrategy_target_qubits = ["QB3"]

    settings.stages.timebox_stage.prepend_heralding.add_heralding = False
    settings.stages.circuit_resolution.resolve_circuits.scheduling_strategy = "ASAP"
    settings.stages.timebox_stage.prepend_reset.active_reset_cycles = None
    settings.stages.circuit_stage.subscribe_and_probe.convert_terminal_measurements = True
    settings.stages.schedule_stage.apply_move_gate_phase_corrections.move_gate_frame_tracking_mode = MoveGateFrameTrackingMode.FULL
    settings.stages.circuit_stage.subscribe_and_probe.probe_all = False
    settings.stages.circuit_stage.validate_circuits.move_gate_validation = True

    settings.controllers.options.playlist_repeats = shots
    settings.controllers.options.averaging_bins = shots


def submit_all(transp_circuits: dict[int, list[QuantumCircuit]]) -> tuple[dict[int, JobTracker], RunDefinition]:
    """Submit all jobs."""

    all_jobs = {}
    print("Submitting all circuits for execution")
    for m, qiskit_circuits in transp_circuits.items():
        # one job per m
        iqm_circuits, compiler = qiskit_to_iqm(backend, qiskit_circuits)
        settings = compiler.get_settings(circuits=iqm_circuits)
        set_settings(settings, shots=shots)
        run_definition, context = compiler.compile(circuits=iqm_circuits, settings=settings)
        all_jobs[m] = iqm_client.submit_playlist(run_definition, context=context)

    print("All jobs submitted OK")
    return all_jobs, run_definition


def retrieve_all(all_jobs: dict[int, JobTracker]) -> dict[int, list[dict[str, int]]]:
    """Retrieve all jobs."""

    retrieved_counts = {}
    for m, job in all_jobs.items():
        print(f"Retrieving results for sequence length {m} out of {list(all_jobs)}")
        job.wait_for_completion()
        qiskit_result = sweep_job_to_qiskit(job, shots=shots)
        retrieved_counts[m] = qiskit_result.get_counts()

    print("All results retrieved OK")
    return retrieved_counts
```

```
submitted_jobs, run_definition = submit_all(all_samples_transpiled)
HTML(inspect_playlist(run_definition.sweep_definition.playlist, range(1)))
```

```
all_counts = retrieve_all(submitted_jobs)
```

We can now inspect the results for a given sequence length (we will use the one defined above). The counts at the ground state relate to the survival probability (or state fidelity) of such state under our random Clifford circuits.

```
plot_histogram(all_counts[m_ex], title=f"RB Counts at sequence length {m_ex}", bar_labels=False)
```

**Task**: Compare the histograms between the outcomes for the narrowest and the deepest circuits

NB: You can wrap `plot_histogram()` with `display(*)` to show both results in one cell

## Analyze the results: what is the average gate fidelity of our gates?

### Estimate the survival probabilities of every circuit at all sequence lengths

```
def survival_probabilities(all_counts: dict[int, list[dict[str, int]]]) -> dict[int, list[float]]:
    all_survival = {m: [] for m in all_counts}
    for m, counts_samples in all_counts.items():
        survival_m = []
        for counts_sample in counts_samples:
            total_counts = sum(counts_sample.values())
            survival_m.append(counts_sample['00'] / total_counts if '00' in counts_sample.keys() else 0)
        all_survival[m] = survival_m
    return all_survival
```

```
all_survival_probabilities = survival_probabilities(all_counts)
```

### Plot the data

```
def plot_survival_probabilities(all_survival_probabilities: dict[int, list[float]]):
    color = (0.247, 0.635, 0.965)
    fig, ax = plt.subplots()
    sequence_lengths = list(all_survival_probabilities.keys())

    flat_fidelity_data = list(chain.from_iterable(all_survival_probabilities.values()))
    scatter_x = [[m] * len(all_survival_probabilities[m]) for m in sequence_lengths]
    flat_scatter_x = list(chain.from_iterable(scatter_x))

    ax.scatter(flat_scatter_x, flat_fidelity_data, s=4, color=color, alpha=0.15)

    ax.errorbar(
        all_survival_probabilities.keys(),
        [np.mean(x) for x in all_survival_probabilities.values()],
        [np.std(x) / np.sqrt(len(x)) for x in all_survival_probabilities.values()],
        color=color,
        fmt="o",
        markersize=4,
        capsize=4,
        label='Mean probability',
    )

    ax.set_xscale("log")
    plt.xlabel('Clifford RB sequence length (log)')
    plt.ylabel(r'Survival probability of $|00\rangle$')
    plt.title(r"Clifford RB survival probabilities of $|00\rangle$", fontsize=9)

    plt.legend()
    plt.grid()

    # plt.show()
    return fig, ax
```

```
survival_probs_plot = plot_survival_probabilities(all_survival_probabilities)
```
