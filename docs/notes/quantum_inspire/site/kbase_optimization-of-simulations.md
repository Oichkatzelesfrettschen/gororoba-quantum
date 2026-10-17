> Full piece: [https://www.quantum-inspire.com/kbase/optimization-of-simulations/](https://www.quantum-inspire.com/kbase/optimization-of-simulations/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 2f1cb6c60652e48f7ef22892cedf5e39ec2528a4c0f96f617b8cde9a338af976.

# Optimization of simulations

## Introduction

When you run an algorithm on a emulator, it is usually unnecessary to end it with a [measurement instruction](https://www.quantum-inspire.com/kbase/cqasm-qubit-initialization-and-measurement/#qubit-measurement). This section explains when it is better to omit the measurement (which drastically improves execution time) and when it is needed to include a measurement statement at the end of the algorithm.

There are three different modes in which simulations can run; each mode implements a different way of obtaining the data that generates the histogram.

The different modes are explained in detail below.

### Deterministic algorithms using a single shot (N=1)

If the algorithm is deterministic (see next section, it can be executed with simulation optimization.

When this mode is running with a single shot (number of shots is 1), the histogram data will contain the probability amplitude values of the final state in the computational z-basis. The histogram will be determined directly from the final state probability amplitudes. In this case the raw data file will only contain one entry, which is the same as the histogram data.

### Deterministic algorithms with multiple shots (N\>1)

When executing with simulation optimization and more than one shot, the histogram will be determined using a Monte Carlo simulation, based on the probability amplitudes of the final state. More information on the exact steps is given in the page on [simulation optimization](https://www.quantum-inspire.com/kbase/optimization-of-simulations/).

### Non-deterministic algorithms

When running a non-deterministic algorithm on the emulator, or when running an algorithm on actual hardware, the result is obtained by executing the algorithm multiple times (the number of shots) and reading out the binary measurement register. The histogram reflects the observed frequency of distinct measurement register values. Note that the binary register is always initialized to zeroes, so when a qubit is not measured at all, the corresponding bit in the binary register (and thus in the histogram) will be zero, but that value has no relationship with the actual qubit state.

## Optimizing algorithms on emulator back-ends through the web interface

### Deterministic algorithms

In a simulation we can determine the full quantum state of the system, therefore in most cases it is not necessary to perform a measurement, or even to run the algorithm multiple times, to determine all possible outcomes.

The [Hello quantum world example](https://www.quantum-inspire.com/kbase/hello-quantum-world/) is an example of such an algorithm. When you run it repeatedly, the final quantum state will always be the same. We will refer to such an algorithm as a *deterministic algorithm*. Most algorithms fall into this category.

In this example, assuming no measurement is performed, the final quantum state of the system is:

$`\vert\Phi^{+}\rangle =\frac{\vert 00 \rangle + \vert 11 \rangle}{\sqrt{2}} = \frac{1}{\sqrt{2}} \vert 00 \rangle + \frac{1}{\sqrt{2}} \vert 11 \rangle`$

In this case, the probability amplitudes for the $`\vert 00 \rangle`$ state and $`\vert 11 \rangle`$ state are both $`\frac{1}{\sqrt{2}}`$ and the probability of measuring one of these states is 50% (which is the result of squaring its probability amplitude). The probability of each state is exactly what we show in the histogram, so one shot is enough to determine *exactly* the probability of each state:

0.500

00

0.500

11

1.0

0.8

0.6

0.4

0.2

0.0

The **web interface** of Quantum Inspire uses a simple rule to determine whether an algorithm is deterministic or not. This rule does not cover all situations, but catches a large number of situations where the algorithm is deterministic and just one execution of the algorithm is sufficient. When the following two conditions are true, the algorithm is certainly deterministic:

- The algorithm contains no `measurement` instruction (`measure`, `measure_all`, `measure_z`, `measure_y`, `measure_x`, `measure_parity`)
- The algorithm contains no `error_model` instruction

The web interface will determine if optimization is possible based on this rule and will only do a single simulation if the algorithm is classified as deterministic.

### Simulation optimization without randomization

When an algorithm is deterministic, Quantum Inspire will always determine the full state of the system with a single simulation (independent of the number of shots that is given as an input). The user will be offered two ways of generating the probability distribution histogram for the possible outcome states, using the field `number of shots` (N) on the pop-up window that appears after the `RUN` button is pressed from the editor view:

1.  N=1: The histogram will be determined directly from the final state probability amplitudes. This method is called **simulation optimization without randomization**.
2.  N\>1: The histogram will be determined using a Monte Carlo simulation. This method is called **simulation optimization with randomization**.

### Simulation optimization with randomization

When the user selects a number of shots N\>1 the Monte Carlo simulation will do the following:

1.  For each possible outcome state, the probability will be determined (total probability =1)
2.  A bin is created for each outcome state, initialized with zero
3.  Each bin will be mapped to a number range between 0 and 1, based on the probability value for each bin. As an example: for the Bell state in the Hello quantum world example the bin 00 will be mapped to the range $`0 < x \leq 0.5`$ and the bin 11 will be mapped to $`0.5 < x \leq 1`$
4.  A random number between 0 and 1 is generated (excluding zero but including 1).
5.  The bin corresponding to the random number is increased by one
6.  Steps 3 and 4 are repeated N times
7.  The final state distribution is determined by normalizing the contents of the bins.

The result will be just as if you had executed the algorithm N times. Note that in this case, the distribution will get closer and closer to the result of the optimization without randomization with the uncertainty depending on the number of 'shots' (virtual shots). Such a simulation can be valuable for testing algorithms on a simulation back-end before running it on a hardware back-end.

### Non-deterministic algorithms

It is important to realize the following: if we had added a measure_all statement at the end of the hello quantum world algorithm, the final state would have been different. Below we will show some examples explaining why the inclusion of a `measure` instruction or an `error model` may lead to non-deterministic behavior. In these cases, simulation optimization is not possible and the user should execute multiple shots of the algorithm to produce a probability distribution for the possible outcomes. The user should **enforce** this by adding a `measure` instruction at the end of the algorithm for one or more qubits.

After the measurement, the final state of the system will be either:

$`\left [ \frac{\vert 0 \rangle}{\sqrt{2}} \right ] \left [ \frac{\vert 0 \rangle}{\sqrt{2}} \right ]`$

or

$`\left [ \frac{\vert 1 \rangle}{\sqrt{2}} \right ] \left [ \frac{\vert 1 \rangle}{\sqrt{2}} \right ]`$

In this case, the final state is not deterministic and we will have to execute multiple shots in order to produce a probability distribution for the possible outcomes.

### Algorithms with an error model

When we [include an error model](https://www.quantum-inspire.com/kbase/cqasm-error-models/) in our algorithm, random errors will be introduced when it is executed and the final state may differ for each execution.

In this case, the final state is not deterministic and we will have to execute multiple shots in order to produce a probability distribution for the possible outcomes.

### Algorithms with binary-controlled gates

Measurement instructions, together with binary-controlled gates, can be used to alter the flow of the algorithm. In this case, the final state is not deterministic and we will have to execute multiple shots in order to produce a probability distribution for the possible outcomes.

Note that binary-controlled instructions by itself, without previous measurements on the qubits, will not lead to a different state, because the corresponding binary register entries will be zero. Therefore, Quantum Inspire checks for measurement instructions, not for binary-controlled gates.

### Algorithms with measurements

Even a single measurement can lead to non-deterministic behavior. As an example, try out the following code in Quantum Inspire:

```cqasm
version 1.0
qubits 1
measure_x q[0]
```

When you execute 1 shot of this algorithm and try this a few times in succession, you will notice that the outcome will be different every time. This is because the qubit is initialized in the ground state in the z-basis, but we measure in the x-basis in this example! So, even a single measurement may result in a non-deterministic algorithm.

### Edge cases

The rules that are used by Quantum Inspire to determine whether an algorithm is deterministic may sometimes cause an algorithm to be identified as non-deterministic when it is not. An example is the following code, where the measurements in line 4 have no impact on the final state of the system. In this case Quantum Inspire will prevent optimization of the simulation.

```cqasm
version 1.0
qubits 2
prep_z q[0:1]
{measure_z q[0] | measure_x q[1]}
{x q[0] | c-x b[0],q[1]}
```

In cases like this, the algorithm can often be re-written in such a way that the measurement instructions are not needed.

## Optimizing algorithms on emulator back-ends through the SDK

When you use the SDK, things are slightly different, depending on how you use the SDK.

### ProjectQ

When you use the ProjectQ in the Quantum Inspire SDK, the **SDK determines automatically** if the algorithm is deterministic or not based on the following rules:

- ProjectQ does not know the `error_model` instruction. So, this instruction is not relevant.
- If the SDK finds a gate after a measurement instruction, the algorithm is classified as non-deterministic and the user should add a measurement instruction at the end in order to get meaningful results.
- If the algorithm re-uses a de-allocated simulation qubit the algorithm is classified as non-deterministic and the user should add a measurement instruction at the end in order to get meaningful results. The concept of re-using ancilla qubits is specific to projectQ. The reader is referred to projectQ documentation to get more details about this. Note: In this Quantum Inspire forces a re-initialization by inserting a measure `q[x]` followed by a `c-X b[x],q[x]` command.

### Qiskit

When you use the Qiskit in the Quantum Inspire SDK, the **SDK determines automatically** if the algorithm is deterministic or not based on the following rules:

- Qiskit does not know the `error_model` instruction. So, this instruction is not relevant.
- If the SDK finds a gate after a measurement instruction, the algorithm is classified as non-deterministic and the user should add a measurement instruction at the end in order to get meaningful results.

### Direct use of API with cQASM

It is also possible to use the API through the QuantumInspireAPI object directly, see <https://github.com/QuTech-Delft/quantuminspire>. This is for advanced users that really know what they are doing. In this case the user has even more control over the optimization process through the *full_state_projection* argument in the `execute_qasm` command. Full state projection is the keyword used internally in Quantum Inspire to do optimization using a single determination of the full final state. By default, this argument is set to False. If you set this flag to True, Quantum Inspire will only do a single determination of the full state and sample from that state. This means the user has to determine whether an algorithm is deterministic or not! If you are not sure, set this argument to False. This will execute the number of shots as specified by the user.
