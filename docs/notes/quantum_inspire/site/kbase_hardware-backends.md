> Full piece: [https://www.quantum-inspire.com/kbase/hardware-backends/](https://www.quantum-inspire.com/kbase/hardware-backends/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 97e86469e9c740b22e08812a5397997a02be66ca691568c2f92b10d16e94d52d.

# Overview of hardware backends

## Introduction

Quantum Inspire has multiple quantum hardware chips or quantum processors. Running algorithms on quantum chips is in some ways different from using emulators. In emulators you usually have more options to do things which you cannot (yet) do with actual hardware. In this section we describe some *general* restrictions of quantum chips and some background information that helps you understand how to get the most out of the chips and how to interpret the results. Some more backend-specific information and/or restrictions are given here:

- **Tuna-5 and Tuna-9**: [operational specifics](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)
- **Starmon-7** : [operational specifics](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/)
- **Spin-2+** : [operational specifics](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/)

A general description of the backends can be found here:

- **Tuna-5/-9 and Starmon-7**: [5/7/9-qubit transmon processors](https://www.quantum-inspire.com/backends/transmons/)
- **Spin-2+**: [2-qubit semiconductor electron spin processor](https://www.quantum-inspire.com/backends/spin-2-plus/)

## Algorithm execution

When you run a quantum algorithm on a hardware backend you will finalize the algorithm with a measurement on one or more qubits in order to get the results of the measurement in the [binary register](https://www.quantum-inspire.com/kbase/binary-register/). In most cases you will need to execute multiple shots in order to get some statistics on your measurement and to reduce the effects of decoherence, leakage and control imperfections. On a hardware backend, when you execute multiple shots of your algorithm, all of them will be executed back to back. For each shot, the final measurement results will be stored in the binary register and written to the raw data file; see [displaying and downloading your results](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/). The histogram will show the normalized frequency of each state of the binary register.

## Qubit initialization and measurement

On our hardware backends *all* qubits will always be initialized in the ground state at the beginning of each shot and all qubits will always be measured at the end of each shot, even when the user does not supply a `prep` statement at the begin or a `measure` statement at the end of the algorithm. The `measure` statement at the end of an algorithm merely determines which measurement results are returned to the user. The following situations must be considered:

1.  The `measure_all` statement is included at the end of the algorithm

In this case all measured output states are returned.

2.  No `measure` (or `measure_all`, `measure_x` etc) statement is included at the end of an algorithm

In this case the system will return **all** measured states to the user (because it does not make sense to return no results to the user). This is therefore equivalent to a `measure_all` statement.

3.  A `measure`, `measure_x`, `measure_y` or `measure_z` is included but not for all qubits (e.g., only for qubit 0)

In this case [binning is done which means that only the measurement probabilities for the measured qubit are returned](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/#binnning), irrespective of the results of the non-measured qubit (for which the output probability is then set to zero).

Note: algorithms for hardware backends **must** always include a `qubit [2] register_name` command (for Spin-2+) or `qubit [7] register_name` command (for Starmon-7) in the cQASM file.

## Number of operations

The number of quantum operations that return a **meaningful** result is mainly determined by the coherence times (T1 and T2\*) of the qubits which determines to a large extend the operational fidelities. The actual gate count is also determined by the decomposition of the gates. As an example, a SWAP gate on Spin-2 will be decomposed into 3 CZ gates and some single-qubit gates. Furthermore, the individual backends will limit the number of operations that can be executed. If you try to execute too many operations in one shot, the system will return an error and your job will not be executed.

## Number of shots

Our hardware backends allow you to do a **large number of shots** to determine the output probabilities of the individual states. The maximum number of shots is limited by the memory capabilities of the data acquisition hardware that is used.

[Previous](https://www.quantum-inspire.com/kbase/quantum-classification/) [Next](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)
