> Full piece: [https://www.quantum-inspire.com/kbase/number-of-shots/](https://www.quantum-inspire.com/kbase/number-of-shots/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 7e4fac431260e014a7c9be1ec46755b33d12bb23b0b819e2dd51840236f34275.

# Number of shots

Each quantum algorithm that is executed is repeated a number of times (the number of shots).

Measurement in quantum mechanics are non-deterministic. If the system consists of a single qubit in the state $`a \left\lvert 0 \right\rangle + b \left\lvert 1 \right\rangle`$\> then a measurement in the $`z`$-basis results in a value 0 with probability $`|a|^2`$ and a value 1 with probability $`|b|^2`$. It is therefore not possible to gain full information about a quantum system with a single measurement. Also physical systems have noise so our measurement result might be corrupted.

For example if we have the following quantum algorithm

```cqasm
version 3.0

qubit[1] q
bit[1] b

H q[0]
b[0]=measure q[0]
```

and the algorithm is executed perfectly, the state of the system after the Hadamard gate would be

$`\frac{1}{\sqrt{2}} \left( \left\lvert 0 \right\rangle + \left\lvert 1 \right\rangle \right)`$

The outcome of a single measurement is either 0 or 1. When we perform the quantum algorithm with 20 shots, then a typical measurement outcome would be:

```
data=0,1,1,0,1,1,0,1,0,1,0,0,1,0,0,1,1,0,1,1
```
