> Full piece: [https://www.quantum-inspire.com/kbase/working-with-the-editor/](https://www.quantum-inspire.com/kbase/working-with-the-editor/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 946c6c3d7144f95211c86cb1d4017da122faa875591e0c9cc69102c86833f3c3.

# Working with the editor

By going to 'My QI', you enter the *editor* for a specific project by clicking on the project title. When a new project is created, you enter the editor automatically as well.

A typical cQASM program could look like this:

```cqasm
version 3.0

qubit[2] q

// Create a superposition state for qubit 0
H q[0]

// Entangle both qubits using a CNOT gate
CNOT q[0], q[1]
```

Some details of this program were [explained earlier](https://www.quantum-inspire.com/kbase/hello-quantum-world/).

You can type your cQASM program directly in the editor. The editor checks your code for obvious problems such as syntax errors, multiple operations on the same qubit at the same time, out-of-range errors, etc. Syntax highlighting is used to easily discriminate between instructions, operands, comments etc.

Note that syntax errors are signaled in the editor by a clear warning, but this does not prevent the code from being saved.

Although the editor may catch the most obvious syntax errors, your code could still contain other problems which result in execution errors.

Our new editor environment has lots of new features.You can drag windows around. Check out the source code, compiled code, job status and job results. Try it out for yourself to find out all features.

## Visualization of the algorithm

The circuit diagram corresponding to the cQASM code is shown in a separate section of your window. The circuit is automatically rendered from the code in real time. Both the code display and the circuit visualization use differing colors to distinguish initialization and measurement operations from qubit operations and comments.

You can visualize your algorithm in he horizaontal direction, vertical direction or you can toggle off the viusualization completely using the visualization options at the bottom right.

You can download the visualization of the algorithm as a SVG or PNG vector file in either direction and using a light or a dark theme.

Try it out yourself, by cicking the download button in the picture below.

If your algorithm contains many lines of code, the rendering of the circuit could take some time. For very long algorithms our [Software Development Kit (SDK)](https://www.quantum-inspire.com/kbase/software-development-kit/) may be more appropriate.

In the editor you can type your own code or copy and paste existing algorithms.

[Previous](https://www.quantum-inspire.com/kbase/managing-your-projects/) [Next](https://www.quantum-inspire.com/kbase/executing-your-algorithm/)
