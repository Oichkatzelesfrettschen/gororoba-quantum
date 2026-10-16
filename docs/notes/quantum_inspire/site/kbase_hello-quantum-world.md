> Full piece: [https://www.quantum-inspire.com/kbase/hello-quantum-world/](https://www.quantum-inspire.com/kbase/hello-quantum-world/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 4acd4fa43768e73555dec3f954425853e160f963ac428beb82cb313250dcff3d.

# Hello quantum world

## Let's start

Writing and running your own algorithm on our platform is quite straightforward. As a registered user you can start programming by clicking [MY QI](https://compute.quantum-inspire.com) from our homepage. Anonymous use of Quantum Inspire is not possible.

This will bring you to our editor, where you can write your quantum algorithm. You can run the code on our emulator backend or hardware backends and examine the results.

*Please note*: before running our examples or any code on one of the quantum inspire backends, pelase carefully check the [constraints/requirements for that specific backend](https://www.quantum-inspire.com/kbase/hardware/). For example, Starmon-7 backend would return an error for cQASM `qubit[2] q`, since it currently requires the user to declare all 7 qubits as `qubit[7] q`.

## Examine the code

The algorithm shows how to entangle two qubits using the Hadamard gate and CNOT gate. Under the advanced topics you will find more elaborate code examples.

```cqasm
version 3.0

// create a qubit register of 2 qubits and a bit register of 2 bits
qubit[2] q
bit[2] b

// Create a superposition state for qubit 0
H q[0]

// Entangle both qubits using a CNOT gate
CNOT q[0], q[1]

// measure both qubits into the bit register
b[0,1] = measure q[0,1]
```

The algorithm is written in cQASM. When you are writing more complex algorithms, you need to understand [the detailed sematics and syntax of cQASM](https://qutech-delft.github.io/cQASM-spec/latest/).

The file starts with the specification of the cQASM version on line 1. This line should always be present.

Line 3 is a single line comment. A single-line comment is prefixed by two forward slashes `//` and finishes with the new line. Use comments to document your code, so that someone else can understand what you were trying to do (note that that someone else could also be your future self).

Line 4 defines the size of the qubit register. In this simple example, two qubits are used. Each qubit in the register is identified by its index. The first qubit has index $`0`$ and the second qubit has index $`1`$. Make sure your qubit register does not define more qubits than used by your algorithm. The memory allocated for your algorithm is determined by this number and execution time is optimal when these numbers match.

Line 5 defines the size of the classical bit register that is used to store the outcome of qubit state measurements. Unlike in Quantum Inspire 1.0, the bit register is independent from the qubit register and can have an arbitrary size. This allows you to store for instance the results of intermediate measurements.

In line 8 we perform a Hadamard gate on qubit 0. The Hadamard gate is a single-qubit operation that brings the basis state $`|0\rangle`$ to $`\frac{\vert 00 \rangle + \vert 11 \rangle}{\sqrt{2}}`$.

In line 11 we use a two-qubit operation to entangle both qubits. The CNOT operation flips the second qubit if the first qubit is in $`|1\rangle`$ state and it does nothing on the second qubit if the first qubit is in $`|0\rangle`$ state. Since the first qubit is in a superposition state, it both flips and doesn't flip the second qubit, bringing the full system in the entangled state $`\frac{\vert 0 \rangle + \vert 1 \rangle}{\sqrt{2}}`$ which is one of the [Bell states](https://www.quantum-inspire.com/kbase/bell-states/).

Finally, in line 14, we measure the state of qubits $`0`$ and $`1`$ in bit registers $`0`$ and $`1`$.

## Visualization of the algorithm

The corresponding circuit diagram is shown beneath the editor pane. Standard color coding is used in both the editor and the visualizer.

The circuit is automatically and real-time rendered from the code. The editor also automatically checks your code for obvious errors such as syntax errors, multiple operations on the same qubit at the same time, out-of-range errors etc.

## Running the algorithm

Now it's time to execute this algorithm on Quantum Inspire and examine the results.

When you are a novice in quantum algorithms, results may sometimes surprise you. In this example, the qubits are in an entangled state. You could almost say that, just before the measurement, both qubits are in $`|0\rangle`$ state OR both qubits are in $`|1\rangle`$ state (although this is a simplified explanation of the more complex physical reality).

At the top right you find the `My QI` button which will bring you to the Quantum Inspire editor. If you did not register before or are not authenticated yet, you will be asked to either [register or login using an existing account](https://www.quantum-inspire.com/kbase/managing-your-account/). In this environemnt you can create a new project by clicking on `NEW PROJECT` or open an existing project. In this project you can create a new algorithm by clciking on `+Create Algorithm`. This will generate a new empty code editor for a file named *source.cq*. You can copy and pase the code above in the editor and then click `RUN`. This will show a pop-up where you can select the file you just created (*source.cq*), the backend to execute it on and the number of shots you want to use. let's start with 16 shots to begin with.

Then click `Run` to put the algorithm in the job queue where it will be picked up by the backend for execution.

When you execute the algorithm, it will be scheduled in a queue. The waiting time depends on the length of the queue, your position in the queue and the time needed to run the algorithm. When your algorithm is executed, all shots will be executed directly after one another.

While your algorithm is scheduled to run, you can return to the editor, change the algorithm and execute another run.

## Examining the results

Let's take a look at what our original algorithm produced.

If you click on `Job` you will see some meta-data of the job such as the Job ID (usefull when working with the API), a link to the source code and the status. When the status is *completed* you can click on the result and examine the data. When you open one of the results a histogram will be shown looking like this, although the exact values will probably be different:

0.438

00

0.563

11

1.0

0.8

0.6

0.4

0.2

0.0

When we measure a qubit, the result can be a 0 or a 1. In quantum inspire, the results of qubit measurements are stored in the bit register. What the histogram shows is not the final state of the qubits, but what the contents of the binary register is when the qubits are measured.

The chart shows a histogram over all shots of the state of the bit register *at the end of the algorithm*. In the example histogram above, the bit register was $`00`$ for 44% of the shots, and $`11`$ for 56% of the shots. The rightmost bit is the measurement value of the measured qubit with the lowest index (in this case q\[0\]). The leftmost bit is the measurement value of the measured qubit with the highest index (in this case q\[1\]).

The results show, that whenever the result of the measurement on q\[0\] was $`0`$, the result of the measurement on q\[1\] was also $`0`$. **And**, whenever the result of the measurement on q\[0\] was $`1`$, the result of the measurement on q\[1\] was also $`1`$, exactly what we expected.

We can execute another run of the algorithm, which could give a result like this:

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

Besides the histogram data of the bit register, the results pane also shows date and time of the execution, the execution duration, the number of shots and a unique identifier of the job.

This is all the basic information you need to write and run your own algorithms! Go ahead and enjoy!

Ready for more? Our [Quick guide](https://www.quantum-inspire.com/kbase/quick-guide/) gives you more information on all kinds of extra functionality of the editor, details on how to steer compilation, managing your account and managing your projects. Expert users can go to our list of [Advanced topics](https://www.quantum-inspire.com/kbase/advanced-guide/) to find more info on our SDK, how to create more complex algorithms, optimize quantum circuits etc.

Enjoy !

[Previous](https://www.quantum-inspire.com/kbase/what-is-a-quantum-algorithm/) [Next](https://www.quantum-inspire.com/kbase/quick-guide/)
