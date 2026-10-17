> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/](https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
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

``` python
import pennylane as qml
import numpy as np

dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=4096,
    backend="rigetti:cepheus-1-108q",
)
```

## Generate Toy Data

Create a simple 2D dataset with two classes:

``` python
np.random.seed(42)
n_samples = 20

# Class 0: points near (0.3, 0.3)
X_class0 = np.random.normal(loc=0.3, scale=0.15, size=(n_samples // 2, 2))
y_class0 = np.zeros(n_samples // 2)

# Class 1: points near (0.7, 0.7)
X_class1 = np.random.normal(loc=0.7, scale=0.15, size=(n_samples // 2, 2))
y_class1 = np.ones(n_samples // 2)

X = np.vstack([X_class0, X_class1])
y = np.hstack([y_class0, y_class1])

# Scale features to [0, pi] for angle embedding
X_scaled = X * np.pi
```

## Define the Quantum Classifier

### Feature Encoding

Use angle embedding to encode classical features as rotation angles:

``` python
def feature_map(x):
    """Encode a 2D feature vector into qubit rotations."""
    qml.RX(x[0], wires=0)
    qml.RX(x[1], wires=1)
```

### Variational Circuit

Define a parameterized ansatz for classification:

``` python
def variational_layer(params):
    """A single variational layer with rotations and entanglement."""
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)
```

### Full QNode

``` python
@qml.qnode(dev)
def classifier(x, params):
    # Encode features
    feature_map(x)
    # Apply variational layers
    variational_layer(params[:4])
    variational_layer(params[4:8])
    # Measure
    return qml.expval(qml.PauliZ(0))
```

The output is a value in \[-1, 1\]. We map this to a class prediction: values \> 0 correspond to class 0, values \<= 0 to class 1.

## Define the Cost Function

``` python
def cost(params, X, y):
    """Binary cross-entropy-like cost from expectation values."""
    total_cost = 0.0
    for x_i, y_i in zip(X, y):
        prediction = classifier(x_i, params)
        # Map label {0, 1} to target {1, -1}
        target = 1.0 - 2.0 * y_i
        total_cost += (prediction - target) ** 2
    return total_cost / len(y)


def accuracy(params, X, y):
    """Compute classification accuracy."""
    correct = 0
    for x_i, y_i in zip(X, y):
        prediction = classifier(x_i, params)
        predicted_class = 0 if prediction > 0 else 1
        if predicted_class == y_i:
            correct += 1
    return correct / len(y)
```

## Training Loop

``` python
# Initialize parameters
np.random.seed(0)
params = np.random.uniform(-np.pi, np.pi, size=8)

# Optimizer
opt = qml.AdamOptimizer(stepsize=0.1)

# Training
n_epochs = 20
for epoch in range(n_epochs):
    params, loss = opt.step_and_cost(lambda p: cost(p, X_scaled, y), params)

    if epoch % 5 == 0:
        acc = accuracy(params, X_scaled, y)
        print(f"Epoch {epoch:3d}: Loss = {loss:.4f}, Accuracy = {acc:.2%}")

# Final accuracy
final_acc = accuracy(params, X_scaled, y)
print(f"\nFinal accuracy: {final_acc:.2%}")
```

Expected output:

```
Epoch   0: Loss = 1.2341, Accuracy = 50.00%
Epoch   5: Loss = 0.5213, Accuracy = 75.00%
Epoch  10: Loss = 0.2187, Accuracy = 90.00%
Epoch  15: Loss = 0.1023, Accuracy = 95.00%

Final accuracy: 95.00%
```

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
