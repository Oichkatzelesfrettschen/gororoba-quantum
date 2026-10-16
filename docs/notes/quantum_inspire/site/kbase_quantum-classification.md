> Full piece: [https://www.quantum-inspire.com/kbase/quantum-classification/](https://www.quantum-inspire.com/kbase/quantum-classification/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 c8c3cd80342d0fe9242d727f5ce80b68bc7dd7d188a293d273b248bc4d3231aa.

# Code example: Quantum classification

The future is now. Quantum Machine Learning in the Cloud!

## Backends

*This example is written for all Inspire backends, the [emulator backend](https://www.quantum-inspire.com/kbase/emulator-backends), [Spin-2 backend](https://www.quantum-inspire.com/kbase/quantum-classification/kbase/spin-2-operational-specifics/) and [Starmon-7 backend](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics).* However, please ensure to adapt the code as per the topology of the backend you intend to use.

## What does it do?

Classification is a form of machine learning in which labels are assigned to data, often with respect to other data. For instance, we can classify between animals having $`2`$ or $`4`$ legs or a different number. Often we classify new data based on already classified (learned) data. We classify this new data point by representing all data points by features or characteristics and compute the distance between the features of the new data point and the features of the learned data points. The new data point is assigned the label to which it has the shortest distance.

This is an example of $`k`$-nearest neighbor classification with $`k=N`$, which classically has a complexity of $`\mathcal{O}(NM)`$, with $`N`$ the number of data points and $`M`$ the number of features. A quantum version of this classifier was proposed by Schuld et al. , see ref.1, and has a constant complexity $`\mathcal{O}(1)`$.

## What is it used for?

Classification has wide-spread use in everyday life and we often classify objects without fully realizing we do it. Classically, naively we would have to compute the distance between the new data point and all other data points separately, after which we combine the results. This approach can be approved upon, but we are still left with a complexity of $`\mathcal{O}(NM)`$.

With a quantum-based approach, we do the same computations, but now only requiring one single-qubit operation and two measurements. Hence, the quantum-based approach is in theory better than the classical one. A caveat is however that the result is probabilistic, hence, multiple measurement rounds must be needed. Furthermore, a specific quantum state is assumed to begin with. Without something like a quantum RAM or a quantum process that produces the input state efficiently, we are left with the same complexity as the classical approach.

## How does classification work?

Let our data points be given by $`{(x^i, y^i)}_{i=0}^{N-1}`$, with $`>x^i`$ the data point and $`y^i`$ the corresponding label and let $`(x^*, y^*)`$ be the unlabeled new data point. Furthermore, there are only two labels $`y^i=\pm 1`$. The new label is then given by evaluating

``` math
\space\space\space\space\ (1) \space\space\space\space\begin{gathered}
   y^* = {\rm sgn}\left(\sum_{i=0}^{N-1} y^i \left[1-\frac{1}{4N}{\vert{x^*}-x^i\vert}^2\right]\right)
\end{gathered}
```

If both classes have the same number of data points, we can simplify the above function to

``` math
\space\space\space\space\ (2) \space\space\space\space\begin{gathered}
   y^* = {\rm sgn}\left(\sum_{i=0}^{N-1} y^i {\vert{x^*} + x^i\vert}^2\right)
\end{gathered}
```

## Quantum implementation

### Preparation

If we normalize our data set, we can encode every data point into a quantum state

``` math
\space\space\space\space\ (3) \space\space\space\space\begin{gathered}
   x^i = (x^i_0,...,x^i_{M-1})^T \Rightarrow \vert x^i \rangle = \sum_{j=0}^{M-1} x^i_j \vert j \rangle
\end{gathered}
```

where \vert j \rangle is the j-th computational basis state. Suppose now that we start with the following quantum state

The first register $`\vert i \rangle`$ is the $`i`$-th computational basis state to keep track of the $`>i`$-th training point. The second register is an ancilla qubit entangled with the training set and the new test point. The third register is a combination of the new test point and the training set. The fourth register $`\vert y^i \rangle`$ encodes the labels of the training set. In the case of only two classes we need only one qubit to encode the labels and we identify $`y^i=1`$ with $`\vert y^i \rangle = \vert 1 \rangle`$ and $`y^i=-1`$ with $`\vert y^i \rangle = \vert 0 \rangle`$. *NB this is in contrast with the convention in quantum mechanics, where the state $`\it{ \vert 0 \rangle }`$ corresponds with 1, and $`\it{ \vert 1 \rangle }`$ corresponds with -1.*

### The algorithm

Given this initial state, the quantum algorithm consists of only three operations. First, we apply a Hadamard on the second register. This gives

``` math
\space\space\space\space\ (5) \space\space\space\space\begin{gathered}
   \frac{1}{2\sqrt{N}} \sum_{i=0}^{N-1} \vert i \rangle (\vert 0 \rangle (\vert x^* \rangle + \vert x^i \rangle) + \vert 1 \rangle (\vert x^* \rangle - \vert x^i \rangle )) \vert y^i \rangle
\end{gathered}
```

We then measure the second register and conditionally continue if we measured the 0-state. This gives

``` math
\space\space\space\space\ (6) \space\space\space\space\begin{gathered}
   \frac{1}{2\sqrt{Np_{0}}} \sum_{i=0}^{N-1} \vert i \rangle \vert 0 \rangle(\vert x^* \rangle + \vert x^i \rangle) \vert y^i \rangle = \\
   \frac{1}{2\sqrt{Np_{0}}} \sum_{i=0}^{N-1} \vert i \rangle \vert 0 \rangle (\sum_{j=0}^{M-1} x^*_j \vert j \rangle + \sum_{k=0}^{M-1} x^i_k \vert k \rangle) \vert y^i \rangle = \\
   \frac{1}{2\sqrt{Np_{0}}} \sum_{i=0}^{N-1} \sum_{j=0}^{M-1} \vert i \rangle \vert 0 \rangle ( x^*_j + x^i_j) \vert j \rangle \vert y^i \rangle
\end{gathered}
```

with p\_{0} the probability of obtaining 0 after measuring the second register and x^i_j the j-th feature of the i-th data point.

Now measuring the last register which encodes the label gives the probability of each class. For example

``` math
\space\space\space\space\ (7) \space\space\space\space\begin{gathered}
   P(y^* = \alpha) = \frac{1}{4Np_{0}}\sum_{i \vert y^i=\alpha} \vert x^* + x^i \vert ^2
\end{gathered}
```

where in our case \alpha can be -1 or 1. It can be easily verified that this classifier will yield the same result as its classical counterpart formula 2. The difference is that formula 7 gives only the chance of a certain classification. The measurement should therefore be done numerous times to get an accurate result, the more the better. Also, when a test point lays close to the border of another class, the chance of a wrong classification becomes bigger.

Note that the two measurement rounds can be combined by classically post-processing the results.

## Example code

Let us consider a simple implementation of the above quantum distance-based classifier. As we have no quantum RAM, we will explicitly prepare the quantum state. Furthermore, we will consider only two data points, each with two features.

For normalized and standardized data, we can assume without loss of generality that

``` math
\begin{matrix}
\begin{aligned}
   &\vert x^0 \rangle = \cos(\theta/2)\vert 0 \rangle - \sin(\theta/2)\vert 1 \rangle \\
   &\vert x^1 \rangle = \cos(\phi/2)\vert 0 \rangle - \sin(\phi/2)\vert 1 \rangle \\
   &\vert x^* \rangle = \cos(\omega/2)\vert 0 \rangle - \sin(\omega/2)\vert 1 \rangle
\end{aligned}
&&&&&
\begin{aligned}
   & y^0 = -1 \\
   & y^1 = 1 \\
   &\space
\end{aligned}
\end{matrix}
```

where in this example we use

``` math
\begin{matrix}
\begin{aligned}
   &\space\space\space x_0 = (1,0)\\
   &\space\space\space x_1=(-0.9929,0.1191)\\
   &\space\space\space x^* = (0.9939, 0.1103)\\
\end{aligned}
&&
\text{resulting in}
&&
\begin{aligned}
   &\theta = 0 \\
   &\phi = −6.0445 \\
   &\omega = −0.2210 \\
\end{aligned}
\end{matrix}
```

The code is then given by

```cqasm
version 3.0

qubit[4] q
bit[4] b

init q[0:3]
H q[0:1]

/* Encode new data point */
// encode the new data point, this implements a cRy(omega)
CNOT q[1], q[2]
Ry(0.1105) q[2]             // (Ry q[2], -omega/2)
CNOT q[1], q[2]
Ry(-0.1105) q[2]           // (Ry q[2], omega/2)
X q[1]

/* Encode first training point */
// encode the first data point, this implements a ccRy(theta)

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

CNOT q[0], q[2]
Ry(0) q[2]                 // (Ry q[2], theta/4)
CNOT q[0], q[2]
Ry(0) q[2]                 // (Ry q[2], -theta/4)

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

CNOT q[0], q[2]
Ry(0) q[2]                 // (Ry q[2], -theta/4)
CNOT q[0], q[2]
Ry(0) q[2]                 // (Ry q[2], theta/4)
X q[0]

/* .Encode second training point */
// encode the second data point, this implements a ccRy(phi)

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

CNOT q[0], q[2]
Ry(-1.511125) q[2]         // (Ry q[2], phi/4)
CNOT q[0], q[2]
Ry(1.511125) q[2]          // (Ry q[2], -phi/4)

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

CNOT q[0], q[2]
Ry(1.511125) q[2]          // (Ry q[2], -phi/4)
CNOT q[0], q[2]
Ry(-1.511125) q[2]         // (Ry q[2], phi/4)

/* Labels */
// encode the labels
CNOT q[0], q[3]

/* Algorithm */
// The actual algorithm
H q[1]

b[1, 3] = measure q[1,3]
```

0.498

0000

0.002

0010

0.007

1000

0.493

1010

1.0

0.8

0.6

0.4

0.2

0.0

Note that we must discard the measurement results where the measurement of the second qubit gives $`1`$, so we should only look at results 1000 and 0000. Hence, we see that $`P(y^*=-1) > P(y^*=1)`$, as we would expect.

## Using the spin-2 quantum chip

Following N. Neumann in [\[3\]](https://arxiv.org/abs/2004.10426) we can implement the classifier in the [spin-2 quantum chip](https://www.quantum-inspire.com/kbase/spin-2-operational-specifics/). This is a non-trivial reduction to a two-qubit system, working only for the case of only two features and only two training data points.

The following variables are proposed

``` math
t = \frac{  cos^2 ( \frac{\omega}{4}) }{  cos^2 (\frac{\omega - \phi}{4}) } \\
\space\\
\text{and}\\
\space\\
\omega ' = \text{arctan} \Bigg( \frac{1-\sqrt{t}}{1+\sqrt{t}} \Bigg)
```

in combination with this algorithm

![](https://www.datocms-assets.com/119587/1591036465-classification2.png)

By measuring the lower (second) qubit and continuing only if the result is 0, we end up with the final state

``` math
c * \space \Big( cos(\omega'/2) \vert 00 \rangle + \big( 1 + sin(\omega'/2) \big) \vert 01 \rangle \Big)
```

where c is some normalizing constant.

Finally measuring the upper (first) qubit will give the class for the test data point, with the same probability as the original 4-qubit script.

Looking at our example we find

``` math
\begin{matrix}
\begin{aligned}
   & t &= \\
   & \omega'&=\\
\end{aligned}
&
\begin{aligned}
   & 75.8202\\
   -&2.68422\\
\end{aligned}
\end{matrix}
```

resulting in the following cqasm code

```cqasm
version 3.0

qubit[2] q

H q[0]
Ry(1.34211) q[1]                        // (Ry q[1], -theta/2
CNOT q[0], q[1]
Ry(-1.34211) q[1]                       // (Ry q[1], theta/2
H q[0]
```

0.974

00

0.000

01

0.013

10

0.013

11

1.0

0.8

0.6

0.4

0.2

0.0

The above result is obtained with a [single shot optimized run](https://www.quantum-inspire.com/kbase/optimization-of-simulations/) in the emulator. If we discard the results where the first qubit gives 1, and only keep states 00 and 10, we see the same probability of a correct classification of 98.7% as for the 4 qubit version.

0.519

00

0.169

01

0.151

10

0.161

11

1.0

0.8

0.6

0.4

0.2

0.0

The above result is obtained by running the algorithm on the [spin-2](https://www.quantum-inspire.com/kbase/spin-2-operational-specifics/) quantum hardware chip with 1024 shots. We see the result is less accurate, but is still accurate enough to give the right classification.

## Want to know more?

For more information see the article by Schuld et al., the notebooks on this algorithm on our GitHub or this article \[2\], where the practicalities of the state preparation are given.

\[1\] Implementing a distance-based classifier with a quantum interference circuit, M. Schuld, M. Fingerhuth, and F. Petruccione, EPL (Europhysics Letters), Volume 119, Number 6, 2017

\[2\] R. Wezeman, N. Neumann, and F. Phillipson. “Distance-based classifier on the Quantum Inspire”. In: Digitale Welt4.1 (Jan. 2020), pp. 85–91

[3](https://arxiv.org/abs/2004.10426) N. Neumann "Classification using a two-qubit quantum chip"

[Previous](https://www.quantum-inspire.com/kbase/code-example-the-maximum-independent-set/) [Next](https://www.quantum-inspire.com/kbase/hardware-backends/)
