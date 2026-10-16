> Full piece: [https://www.quantum-inspire.com/kbase/executing-your-algorithm/](https://www.quantum-inspire.com/kbase/executing-your-algorithm/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 69a3229842923cbf9ec4b5dde90a3e4a5ca7d78f9929375f41d62a2159567144.

# Compiling and executing your algorithm

## Initiating a run

Running your algorithm on one of the available backends is initiated by clicking on the `RUN` button. A popup window will appear that shows you:

- A selection for the file that needs to be executes (e.g. source file or a previously compiled file)
- The backend that shall be used for this experiment
- The name of the current experiment (can be changed by the user)
- The [number of shots](https://www.quantum-inspire.com/kbase/number-of-shots) of this experiment (can be changed by the user)

When you run a quantum algorithm on a selected backend, Quantum Inspire will always (implicitly) compile the circuit according to the [compilation strategy](https://www.quantum-inspire.com/kbase/compilation#compilation-strategy) defined for that backend. This means that the circuit could be mapped, decomposed, optimized etc before the final instructions are generated required by the backend to execute the circuit. The results of each *compilation stage* are not shown to the user. If you wan to examine the results of each compile stage, you should explicitely compile the file, without running it, see the next paragraph.

## Explicit compilation of the algorithm

## Running a pre-compiled version of the algorithm

## Executing algorithms on a hardware backend

When you run a quantum algorithm on a hardware backend the list of quantum operations is limited by the set of operations that is supported by the backend and the topology of the chip. The list of allowed operations for the current backends can be [found here](https://www.quantum-inspire.com/kbase/hardware-backends/).

For hardware backends, the number of qubits in your algorithm must always be set equal to the number of qubits on the chip, although you do not need to perform operations on all qubits.

All qubits will be initialized in the ground state or \|0\> state in the z-basis.

When you do not put any `measure` statements at the end of your algorithm, by default all qubits will be measured in the z-direction. When you do close your algorithm with a measurement on one or more qubits, only those qubits will be measured and the result for non-measured qubits will be set to the default value of zero.

In most cases you will have to execute multiple shots in order to get some statistics on your measurement and to reduce the effects of decoherence, leakage, and control imperfections. On a hardware backend, when you execute N shots of your algorithm, all shots will be executed in succession. For each shot, the final measurements will be stored in the binary register and written to the raw data file, see [displaying and downloading your results](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/). The histogram will show the probability distribution of each state of the binary register.

## Running hybrid quantum-classical algorithms

Running hybrid algorithms is not possible uing the graphical user interface and the editor. This should be done via the [QI Tool](https://www.quantum-inspire.com/kbase/software-development-kit/).

[Previous](https://www.quantum-inspire.com/kbase/working-with-the-editor/) [Next](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/)
