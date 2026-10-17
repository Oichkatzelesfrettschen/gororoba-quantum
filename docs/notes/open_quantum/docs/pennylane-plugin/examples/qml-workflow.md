> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/](https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 333f02a1d4a506f4803c5a88ed3bda7aac6ad0761c71a313ff333359088e798f.

# Quantum Machine Learning Workflow

This tutorial demonstrates a quantum machine learning (QML) classification workflow using a variational quantum classifier on Open Quantum.

## Overview

We build a simple binary classifier that:

1.  Encodes classical data into quantum states using angle embedding.
2.  Processes the quantum state through a parameterized variational circuit.
3.  Measures an expectation value as the classifier output.
4.  Trains the circuit parameters using gradient descent.

## Setup

[](#__codelineno-0-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-0-2)`import`` ``numpy`` ``as`` ``np`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`dev`` ``=`` ``qml``.``device``(`\
[](#__codelineno-0-5)`    ``"openquantum.device"``,`\
[](#__codelineno-0-6)`    ``wires``=``2``,`\
[](#__codelineno-0-7)`    ``shots``=``4096``,`\
[](#__codelineno-0-8)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-0-9)`)`\

## Generate Toy Data

Create a simple 2D dataset with two classes:

[](#__codelineno-1-1)`np``.``random``.``seed``(``42``)`\
[](#__codelineno-1-2)`n_samples`` ``=`` ``20`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`# Class 0: points near (0.3, 0.3)`\
[](#__codelineno-1-5)`X_class0`` ``=`` ``np``.``random``.``normal``(``loc``=``0.3``,`` ``scale``=``0.15``,`` ``size``=``(``n_samples`` ``//`` ``2``,`` ``2``))`\
[](#__codelineno-1-6)`y_class0`` ``=`` ``np``.``zeros``(``n_samples`` ``//`` ``2``)`\
[](#__codelineno-1-7)\
[](#__codelineno-1-8)`# Class 1: points near (0.7, 0.7)`\
[](#__codelineno-1-9)`X_class1`` ``=`` ``np``.``random``.``normal``(``loc``=``0.7``,`` ``scale``=``0.15``,`` ``size``=``(``n_samples`` ``//`` ``2``,`` ``2``))`\
[](#__codelineno-1-10)`y_class1`` ``=`` ``np``.``ones``(``n_samples`` ``//`` ``2``)`\
[](#__codelineno-1-11)\
[](#__codelineno-1-12)`X`` ``=`` ``np``.``vstack``([``X_class0``,`` ``X_class1``])`\
[](#__codelineno-1-13)`y`` ``=`` ``np``.``hstack``([``y_class0``,`` ``y_class1``])`\
[](#__codelineno-1-14)\
[](#__codelineno-1-15)`# Scale features to [0, pi] for angle embedding`\
[](#__codelineno-1-16)`X_scaled`` ``=`` ``X`` ``*`` ``np``.``pi`\

## Define the Quantum Classifier

### Feature Encoding

Use angle embedding to encode classical features as rotation angles:

[](#__codelineno-2-1)`def`` ``feature_map``(``x``):`\
[](#__codelineno-2-2)`    ``"""Encode a 2D feature vector into qubit rotations."""`\
[](#__codelineno-2-3)`    ``qml``.``RX``(``x``[``0``],`` ``wires``=``0``)`\
[](#__codelineno-2-4)`    ``qml``.``RX``(``x``[``1``],`` ``wires``=``1``)`\

### Variational Circuit

Define a parameterized ansatz for classification:

[](#__codelineno-3-1)`def`` ``variational_layer``(``params``):`\
[](#__codelineno-3-2)`    ``"""A single variational layer with rotations and entanglement."""`\
[](#__codelineno-3-3)`    ``qml``.``RY``(``params``[``0``],`` ``wires``=``0``)`\
[](#__codelineno-3-4)`    ``qml``.``RY``(``params``[``1``],`` ``wires``=``1``)`\
[](#__codelineno-3-5)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-3-6)`    ``qml``.``RY``(``params``[``2``],`` ``wires``=``0``)`\
[](#__codelineno-3-7)`    ``qml``.``RY``(``params``[``3``],`` ``wires``=``1``)`\

### Full QNode

[](#__codelineno-4-1)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-4-2)`def`` ``classifier``(``x``,`` ``params``):`\
[](#__codelineno-4-3)`    ``# Encode features`\
[](#__codelineno-4-4)`    ``feature_map``(``x``)`\
[](#__codelineno-4-5)`    ``# Apply variational layers`\
[](#__codelineno-4-6)`    ``variational_layer``(``params``[:``4``])`\
[](#__codelineno-4-7)`    ``variational_layer``(``params``[``4``:``8``])`\
[](#__codelineno-4-8)`    ``# Measure`\
[](#__codelineno-4-9)`    ``return`` ``qml``.``expval``(``qml``.``PauliZ``(``0``))`\

The output is a value in \[-1, 1\]. We map this to a class prediction: values \> 0 correspond to class 0, values \<= 0 to class 1.

## Define the Cost Function

[](#__codelineno-5-1)`def`` ``cost``(``params``,`` ``X``,`` ``y``):`\
[](#__codelineno-5-2)`    ``"""Binary cross-entropy-like cost from expectation values."""`\
[](#__codelineno-5-3)`    ``total_cost`` ``=`` ``0.0`\
[](#__codelineno-5-4)`    ``for`` ``x_i``,`` ``y_i`` ``in`` ``zip``(``X``,`` ``y``):`\
[](#__codelineno-5-5)`        ``prediction`` ``=`` ``classifier``(``x_i``,`` ``params``)`\
[](#__codelineno-5-6)`        ``# Map label {0, 1} to target {1, -1}`\
[](#__codelineno-5-7)`        ``target`` ``=`` ``1.0`` ``-`` ``2.0`` ``*`` ``y_i`\
[](#__codelineno-5-8)`        ``total_cost`` ``+=`` ``(``prediction`` ``-`` ``target``)`` ``**`` ``2`\
[](#__codelineno-5-9)`    ``return`` ``total_cost`` ``/`` ``len``(``y``)`\
[](#__codelineno-5-10)\
[](#__codelineno-5-11)\
[](#__codelineno-5-12)`def`` ``accuracy``(``params``,`` ``X``,`` ``y``):`\
[](#__codelineno-5-13)`    ``"""Compute classification accuracy."""`\
[](#__codelineno-5-14)`    ``correct`` ``=`` ``0`\
[](#__codelineno-5-15)`    ``for`` ``x_i``,`` ``y_i`` ``in`` ``zip``(``X``,`` ``y``):`\
[](#__codelineno-5-16)`        ``prediction`` ``=`` ``classifier``(``x_i``,`` ``params``)`\
[](#__codelineno-5-17)`        ``predicted_class`` ``=`` ``0`` ``if`` ``prediction`` ``>`` ``0`` ``else`` ``1`\
[](#__codelineno-5-18)`        ``if`` ``predicted_class`` ``==`` ``y_i``:`\
[](#__codelineno-5-19)`            ``correct`` ``+=`` ``1`\
[](#__codelineno-5-20)`    ``return`` ``correct`` ``/`` ``len``(``y``)`\

## Training Loop

[](#__codelineno-6-1)`# Initialize parameters`\
[](#__codelineno-6-2)`np``.``random``.``seed``(``0``)`\
[](#__codelineno-6-3)`params`` ``=`` ``np``.``random``.``uniform``(``-``np``.``pi``,`` ``np``.``pi``,`` ``size``=``8``)`\
[](#__codelineno-6-4)\
[](#__codelineno-6-5)`# Optimizer`\
[](#__codelineno-6-6)`opt`` ``=`` ``qml``.``AdamOptimizer``(``stepsize``=``0.1``)`\
[](#__codelineno-6-7)\
[](#__codelineno-6-8)`# Training`\
[](#__codelineno-6-9)`n_epochs`` ``=`` ``20`\
[](#__codelineno-6-10)`for`` ``epoch`` ``in`` ``range``(``n_epochs``):`\
[](#__codelineno-6-11)`    ``params``,`` ``loss`` ``=`` ``opt``.``step_and_cost``(``lambda`` ``p``:`` ``cost``(``p``,`` ``X_scaled``,`` ``y``),`` ``params``)`\
[](#__codelineno-6-12)\
[](#__codelineno-6-13)`    ``if`` ``epoch`` ``%`` ``5`` ``==`` ``0``:`\
[](#__codelineno-6-14)`        ``acc`` ``=`` ``accuracy``(``params``,`` ``X_scaled``,`` ``y``)`\
[](#__codelineno-6-15)`        ``print``(``f``"Epoch ``{``epoch``:``3d``}``: Loss = ``{``loss``:``.4f``}``, Accuracy = ``{``acc``:``.2%``}``"``)`\
[](#__codelineno-6-16)\
[](#__codelineno-6-17)`# Final accuracy`\
[](#__codelineno-6-18)`final_acc`` ``=`` ``accuracy``(``params``,`` ``X_scaled``,`` ``y``)`\
[](#__codelineno-6-19)`print``(``f``"``\n``Final accuracy: ``{``final_acc``:``.2%``}``"``)`\

Expected output:

[](#__codelineno-7-1)`Epoch   0: Loss = 1.2341, Accuracy = 50.00%`\
[](#__codelineno-7-2)`Epoch   5: Loss = 0.5213, Accuracy = 75.00%`\
[](#__codelineno-7-3)`Epoch  10: Loss = 0.2187, Accuracy = 90.00%`\
[](#__codelineno-7-4)`Epoch  15: Loss = 0.1023, Accuracy = 95.00%`\
[](#__codelineno-7-5)\
[](#__codelineno-7-6)`Final accuracy: 95.00%`\

Note

Results will vary between runs due to shot noise and the stochastic nature of the data. Accuracy on this simple dataset should converge to 85-100% within 20 epochs.

## Gradients on Hardware

The plugin computes gradients using the **parameter-shift rule**, which is compatible with shot-based hardware execution. For each trainable parameter, the parameter-shift rule evaluates the circuit at two shifted parameter values:

\\ \frac{\partial f}{\partial \theta_i} = \frac{f(\theta_i + \pi/2) - f(\theta_i - \pi/2)}{2} \\

This means each gradient step requires \\2P\\ circuit evaluations, where \\P\\ is the number of parameters. For our 8-parameter circuit, each optimization step executes 16 circuits on the backend.

Warning

QML training on hardware can be expensive. Each optimization step executes \\2P\\ circuits, and each circuit costs credits based on the shot count. Start with fewer shots and shorter training runs during development, then increase for final validation. See [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/).

## Considerations for Hardware QML

- **Shot noise affects gradients.** Use at least 4096 shots for stable gradient estimates.
- **Start with fewer shots.** Use lower shot counts during development to reduce costs, then increase for final training or evaluation.
- **Keep circuits shallow.** Deeper circuits accumulate more hardware noise and take longer to execute.
- **Use fewer parameters when possible.** Each parameter requires two extra circuit evaluations for gradient computation.

## Next Steps

- [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) -- Choose and configure backends.
- [VQE Example](https://docs.openquantum.com/pennylane-plugin/examples/vqe/) -- Another variational algorithm example.
- [Troubleshooting](https://docs.openquantum.com/pennylane-plugin/troubleshooting/) -- Common issues and solutions.
