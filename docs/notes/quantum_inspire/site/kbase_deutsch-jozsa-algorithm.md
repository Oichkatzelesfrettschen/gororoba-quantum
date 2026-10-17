> Full piece: [https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/](https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 6e319106b755e0b101724c443c5df7309c92afed7ef25bf78242139fe170ecdf.

# Code example: Deutsch-Jozsa algorithm

## Backends

\*In this example, the [QX Emulator](https://www.quantum-inspire.com/kbase/emulator-backends/) is used as backend. The [Spin-2](https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/kbase/spin-2-operational-specifics/) and [Starmon-7](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/) can also be used as backend. In order to use Starmon-7 as backend, please refer to the Starmon-7 \[toplogy\] (<https://www.quantum-inspire.com/backends/starmon-7/>) and make sure that to use a pair of Starmon-7's qubits that are coupled. This is not the case for qubit 0 and qubit 1, so the script should be adjusted. Qubit 0 and Qubit 2 are coupled in Starmon-7, so the algorithm will work on the Starmon backend if we change all references to qubit 0 to qubit 2.

## What does it do?

In the Deutsch–Jozsa algorithm we use an oracle to determine if a binary function $`f(x) : \{0,1\}^n \rightarrow \{0,1\}`$ is constant or balanced.

The function is constant if $`f(x)=0`$ or $`f(x)=1`$ for all values of $`x`$. A function is balanced if $`f(x)=0`$ for half of the possible input values $`x`$ and $`f(x)=1`$ for the other half.

## What is it used for?

The Deutsch-Josza algorithm is a simple example of a quantum algorithm that can be used to speed up a search. As will be explained below, it can determine whether or not a function has a certain property (being balanced). The algorithm achieves this by requiring that the function (more precisely, a derivation of the function) need only be called once with a quantum algorithm instead of twice with a classical algorithm. When the function is very 'expensive', e.g., in terms of computational resources, it can be very beneficial if you have to compute this function only once instead of twice.

Although the speed-up of this specific algorithm is only a factor of 2, other quantum algorithms, using the same quantum mechanical effects, can achieve a polynomial or even an exponential speed-up compared to classical algorithms.

## How does it work?

In this example we consider a binary function $`f(x) : \{0,1\} \rightarrow \{0,1\}`$. There are four possibilities for the function $`f(x)`$, which we call the Oracle function. These are:

1.  $`f_1(x)=0`$
2.  $`f_2(x)=1`$
3.  $`f_3(x)=x`$
4.  $`f_4(x)=1-x`$

The algorithm to determine whether our function $`f(x)`$ is constant or balanced requires only a single query of $`f(x)`$. By changing the Oracle, the 4 different functions can be tested.

In this example a very simple Oracle is implemented for the four different functions, but a much more complex Oracle could also be used.

## Examination of the code

The following code shows the implementation of the algorithm, which uses two qubits. Note that we do not include a measure statement at the end of the algorithm. In this case no measurement statement is required (see [optimization of simulations](https://www.quantum-inspire.com/kbase/optimization-of-simulations/)), but one could be added without causing any problems because this algorithm requires just one shot for its execution.

```cqasm
version 3.0
qubit [2] q
bit[2] b

// In the Deutsch–Jozsa algorithm we use an oracle to determine if a binary function f(x) is constant or balanced.
// Constant f(x)=fc1=0 OR f(x)=fc2=1
// Balanced f(x)=fb3=x OR f(x)=fb4=NOT(x)
// The algorithm requires only a single query of f(x).
// By changing the Oracle, the 4 different functions can be tested.

// Initialize qubits in |+> and |-> state

X q[1]
H q[0,1]}
 
//oracle_fc1
// do nothing or I q[0:1]
 
//oracle_fc2
// X q[1]
 
//.oracle_fb3
// CNOT q[0],q[1]
 
//.oracle_fb4
// CNOT q[0],q[1]
// X q[1]
 
.measurement
H q[0]
b[0] = measure q[0]
```

## Examination of the results

Let us run the code above, using Oracle $`f_c1`$. You can do this by copying the code above to the editor, [executing the algorithm](https://www.quantum-inspire.com/kbase/executing-your-algorithm/) (1 shot is sufficient) and [examining the results](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/). You should get the following result:

1.000

00

1.0

0.8

0.6

0.4

0.2

0.0

We can now run the same code again, but this time we implement the 2nd Oracle, by uncommenting line 20. If we now examine the histogram we get exactly the same result as for the first oracle.

Likewise, we can run the algorithm for Oracle 3 or Oracle 4 by commenting out line 20 and uncommenting one of the other Oracle implementations; in these cases, we will get a different result:

1.000

01

1.0

0.8

0.6

0.4

0.2

0.0

As shown, **with a single function call** we can determine from the outcome whether a function is constant (binary register is 00) or balanced (binary register is 01).

## Want to know more?

To learn more about the Deutsch-Jozsa algorithm, watch [this informative video on QuTube](https://www.qutube.nl/quantum-algorithms/deutsch-jozsa-algorithm).

For more information see [Deutsch–Jozsa algorithm on Wikipedia](https://en.wikipedia.org/wiki/Deutsch%E2%80%93Jozsa_algorithm).

[Previous](https://www.quantum-inspire.com/kbase/libket/) [Next](https://www.quantum-inspire.com/kbase/full-adder/)
