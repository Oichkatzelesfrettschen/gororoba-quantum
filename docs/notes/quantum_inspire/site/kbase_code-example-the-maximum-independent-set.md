> Full piece: [https://www.quantum-inspire.com/kbase/code-example-the-maximum-independent-set/](https://www.quantum-inspire.com/kbase/code-example-the-maximum-independent-set/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 83221667a9621c07f75223fb0c392aa5ef9f01d8d3099ee0297057d590e62992.

# Code example: the Maximum Independent Set

This example is written for the Rydberg emulator backend - Ry Emulator - and can run on a maximum of nine qubits.

## Problem Description

The Maximum independent set problem is a combinatorial optimization problem that is hard to solve with classical computers \[1\]. The problem is to find an independent set of vertices on a given graph with a maximum number of elements. Here, an independent set means a set of vertices that are not directly connected with an edge. In the figure below, there are a variety of independent and dependent sets on a unit disk graph which will become relevant later.

![Image taken from Ref. \[1\].](https://www.datocms-assets.com/119587/1749501029-picture1.png)

Image taken from Ref. \[1\].

The following figure shows a real-world application of the Maximum Independent Set problem: a store placement problem. An independent set can be used to place stores so that any node on the graph is at most 1 hop away from a store.

![Image taken from Ref. \[1\].](https://www.datocms-assets.com/119587/1749501030-picture2.png)

Image taken from Ref. \[1\].

## Applications

Maximum independent set and similar problems have a variety of different real world and academic applications. Some of the real-world problems include store placement, antenna placement for wireless networks, and ad-hoc network routing. There are also academically interesting applications such as the binary satisfiability problem, quadratic unconstrained binary optimization (QUBO), maximum cut and graph coloring are only some examples. A detailed explanation of the maximum independent set problem can be found at \[1\].

![Image taken from Ref. \[1\].](https://www.datocms-assets.com/119587/1749501029-picture3.png)

Image taken from Ref. \[1\].

## Binary Satisfiability Problem

One of the applications of Maximum Independent Set problem is solving the binary satisfiability problem \[2\]. This problem aims to decide whether a given binary logical statement can be satisfiable (i.e. it evaluates True for any pick of {True, False} values for its variables) or not. One may map a binary satisfiability problem to an MIS. This is done by expressing the statement in so-called conjunctive normal form. In the figure below, the binary satisfiability problem is mapped to a Unit Disk Graph. Finding the number of nodes on the maximum independent set answers whether the logical statement given in canonical form is satisfiable or not.

![Image taken from Ref. \[1\].](https://www.datocms-assets.com/119587/1749501029-picture4.png)

Image taken from Ref. \[1\].

## Maximum Independent Set on the neutral atom Rydberg emulator backend

In 2022, Ebadi et al. proposed solving the Maximum Independent set problem in a native way using neutral atom platforms exploiting the Rydberg blockade mechanism \[2\]. The key idea is that on a neutral atom quantum computer, the atoms are placed in a 2D lattice, and the Rydberg blockade that they may experience with each other is equivalent to Unit Disk Graphs (UDG). A Unit disk graph is a graph with edges between two nodes only if the distances between the nodes are of unit length. To illustrate further, one might create a UDG by drawing unit disks around every node in a graph and drawing an edge between each node and the nodes that are inside the unit disk of that node. The main idea is that if the neighboring atoms within the blockade range can block each other, then only one of the atoms within the unit disk graph can be in the Rydberg state. Since the only way two nodes can be connected is if they are within unit range, we have a mechanism to make sure only atoms that are not connected can be in Rydberg state. Exploiting this, one can ensure the readout of a measurement will be an MIS. The algorithm is a hybrid algorithm which means there is a classical and a quantum part to the process. The classical part is a closed loop optimization that scans and iterates over the parameter space of the quantum process. The quantum process we use is a Variational Quantum Adiabatic Algorithm (VQAA). The figure below is a depiction of the MIS solver on a neutral atom platform as proposed by Ebadi et al. \[2\]. A unit disk graph is depicted in A & B. C,D & E to show how the hybrid algorithm works.

## VQAA

![Image taken from Ref. \[2\].](https://www.datocms-assets.com/119587/1749501030-picture5.png)

Image taken from Ref. \[2\].

The Variational Quantum Adiabatic Algorithm is a method that is used to prepare quantum many body states introduced by Farhi et al. \[3\]. To put the atoms in the Rydberg blockade, we sweep the detuning from a negative to positive value adiabatically (i.e. very slowly) at a constant Rabi frequency. The closed loop optimization scans the Rydberg gate parameters to find an optimal solution which corresponds to the independent set with largest number of nodes \[2\]. An example code with VQAA running for solving MIS along with an interactive demo is available via this link: <https://gitlab.tue.nl/20235021/ry-emulator-examples>

## Circuit

The quantum circuit is described by a cQASM file. In this part, we discuss the cQASM file and its syntax for the circuit. First, we specify the version of the cQASM language as 3.0. After that, we define a quantum register. The syntax for defining the register is the following:

```
qubit[4] q
```

Here, we define the register q with 4 qubits. Then we initialize the positions of the qubits in the register. As mentioned before, the positions of the qubits are important for our calculation as it determines which atoms will be in the blockade range during the quantum process. The position of an atom is specified by:

```
INIT(0,1) q[0]
```

This line of code assigns the 0th qubit in register q to position $`x=0`$ and $`y=1`$ in the rectangular lattice shown below. All together the code looks like:

![](https://www.datocms-assets.com/119587/1749501030-picture6.png)

```
version 3.0
qubit[4] q
asm(Rydberg)```
INIT(0, 0) q[0] 
INIT(0, 1) q[1] 
INIT(1, 2) q[2] 
INIT(1, 3) q[3] '''
```

Note that we used the asm(Rydberg)" directive for the INIT" commands. This directive indicates the following raw string (i.e. the code text that is between triple quotations) is Rydberg platform specific. Currently, there are a total of two directives that need to be used as such: INIT and RYD. Both directives and how to work with them are explained in the [Code example: Getting started with the neutral atom platform page](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform).

We move on to add gates for each qubit. We use an $`X`$ gate for each qubit which will flip each qubit from $`0`$ to $`1`$.

```
X q[0] 
X q[1] 
X q[2] 
X q[3] 
```

With this addition, our circuit now looks as follows:

![](https://www.datocms-assets.com/119587/1749501030-picture8.png)

Here, we show two versions of the same circuit. On the left, we see the circuit with gate names and on the right, we see the same circuit with pulses drawn for the gates. The next step is to apply the Rydberg pulse. A time-dependent Rydberg pulse command can be specified using the following lines:

```
asm(Rydberg)``` 
RYD(0.066, -0.733, 0.069) 
RYD(0.240, -0.466, 0.069) 
RYD(0.455, -0.199, 0.069) 
RYD(0.629, 0.068, 0.069) 
RYD(0.696, 0.335, 0.069) 
RYD(0.629, 0.602, 0.069) 
RYD(0.455, 0.869, 0.069) 
RYD(0.240, 1.135, 0.069) 
RYD(0.066, 1.402, 0.069) 
RYD(0.000, 1.669, 0.069) ''' 
```

with the Rydberg pulses, our circuit looks as follows:

![](https://www.datocms-assets.com/119587/1749501030-picture9.png)

Note that all the consecutive discrete pulse steps are merged into one pulse and represented as such.

```
X q[0] 
X q[1] 
X q[2] 
X q[3]
```

![](https://www.datocms-assets.com/119587/1749501030-picture9.png)

And we are done, the circuit doesn't need measurement gates as measurement is implied at the end of every circuit for each qubit.

## Results and Interpretation

After running the circuit we get the measurement results. In the figure below, we see the number of occurrences of each result. For the MIS problem, it is more instructive to look at the number of $`1`$'s in the measured qubits as that corresponds to the number of nodes in the independent set. In the figure below, we see the number of occurrences of measurement results with a specific number of $`1`$'s. Looking at the graph, we interpret that the number of nodes in the independent sets vary between $`0`$ and $`4`$. Note that due to the Rydberg blockade, ideally, in this configuration nodes of 3 and 4 shouldn't be among the results. However, current quantum computers are noisy and prone to errors, and the Rydberg emulator accounts for noise and decoherence. The interpretation requires a weighted average of the number of 1's. The number of shots in this example was $`100`$ and the average approximately gives a value of $`1.18`$. The closer the value of the average converges to an integer, the more reliable the iteration loop is expected to be. In this instructive example, we used a 10 step pulse approximation for the Rydberg laser and only performed 100 shots, which gives rise to a larger error.

![](https://www.datocms-assets.com/119587/1749501029-picture10.png)

![](https://www.datocms-assets.com/119587/1749501029-picture11.png)

\[1\] J. Wurtz, P. L. S. Lopes, C. Gorgulla, N. Gemelke, A. Keesling, and S. Wang, “Industry applications of neutral-atom quantum computing solving indepen- dent set problems,” 2024.

\[2\] S. Ebadi, A. Keesling, M. Cain, T. T. Wang, H. Levine, D. Bluvstein, G. Se- meghini, A. Omran, J.-G. Liu, R. Samajdar, X.-Z. Luo, B. Nash, X. Gao, B. Barak, E. Farhi, S. Sachdev, N. Gemelke, L. Zhou, S. Choi, H. Pichler, S.- T. Wang, M. Greiner, V. Vuletić, and M. D. Lukin, “Quantum optimization of maximum independent set using rydberg atom arrays,” Science, vol. 376, no. 6598, pp. 1209–1215, 2022.

\[3\] E. Farhi, J. Goldstone, S. Gutmann, and M. Sipser, “Quantum computation by adiabatic evolution,” 2000.

[Previous](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/) [Next](https://www.quantum-inspire.com/kbase/quantum-classification/)
