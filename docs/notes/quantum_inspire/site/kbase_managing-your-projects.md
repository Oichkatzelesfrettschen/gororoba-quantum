> Full piece: [https://www.quantum-inspire.com/kbase/managing-your-projects/](https://www.quantum-inspire.com/kbase/managing-your-projects/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 102520c025e85f50d60f4560ed46ca3b24842cc9f704c0bb60330cba00c57b84.

# Managing your projects and algorithms

The algorithm which we wrote in the [Hello World example](https://www.quantum-inspire.com/kbase/hello-quantum-world/) generates a [Bell state](https://www.quantum-inspire.com/kbase/bell-states/). More specifically, it generates the so-called $`\vert\Phi^{+}\rangle`$ state which is equal to

$`\vert\Phi^{+}\rangle =\frac{\vert 00 \rangle + \vert 11 \rangle}{\sqrt{2}}`$

We can change this algorithm to generate another Bell state, the $`\vert\Phi^{-}\rangle`$ state, as follows:

```cqasm
version 3.0

// create a qubit register of 2 qubits and a bit register of 2 bits
qubit[2] q
bit[2] b

// Create a superposition state for qubit 0
H q[0]

// Entangle both qubits using a CNOT gate
CNOT q[0], q[1]

//Flip the second qubit
X q[1]

// measure both qubits into the bit register
b[0,1] = measure q[0,1]
```

When you click on `Save` a new commit will be made and you wil asked to provide a description. You can browse old versions (commits) by clicking on the algorithm menu (the three dots).

You can also choose to Rename your agorithm or Delete your algorithm (and its results!) or to just [compile the algorithm](https://www.quantum-inspire.com/kbase/executing-your-algorithm/) without actually running it.

![](https://www.datocms-assets.com/119587/1742827537-save-commit-snapshot.jpg)

You can find all your projects in the `My QI` home menu. You can find this button in the top right corner. You can also sort your projects by name or date of creation. You can also rename or delete a project.

❗Note that deleting a project will also delete all its algorithms and results.

![](https://www.datocms-assets.com/119587/1742828485-projects-snapshot.jpg)

[Previous](https://www.quantum-inspire.com/kbase/creating-a-new-project/) [Next](https://www.quantum-inspire.com/kbase/working-with-the-editor/)
