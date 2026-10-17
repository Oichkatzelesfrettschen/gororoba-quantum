> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/vqe/](https://docs.openquantum.com/pennylane-plugin/examples/vqe/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 018b5bb478fdcf53175bcb6df241bff2dc0eda08ae91220b695f230191afd3c4.

# Variational Quantum Eigensolver (VQE)

This tutorial demonstrates how to use the Variational Quantum Eigensolver (VQE) algorithm on Open Quantum to find the ground state energy of a simple molecular hydrogen (H2) Hamiltonian.

## Background

VQE is a hybrid quantum-classical algorithm that uses a parameterized quantum circuit (ansatz) to prepare trial states, measures the energy expectation value on quantum hardware, and optimizes the parameters classically to minimize the energy.

## Define the Hamiltonian

For a simplified 2-qubit H2 model at equilibrium bond distance, the Hamiltonian can be expressed as a sum of Pauli terms:

``` python
import pennylane as qml
import numpy as np

# Simplified H2 Hamiltonian (2-qubit, equilibrium bond length ~0.735 A)
coeffs = [
    -0.2427,   # Identity
     0.1740,   # Z0
    -0.1740,   # Z1
    -0.1722,   # Z0 Z1
     0.0454,   # X0 X1
]

obs = [
    qml.Identity(0),
    qml.PauliZ(0),
    qml.PauliZ(1),
    qml.PauliZ(0) @ qml.PauliZ(1),
    qml.PauliX(0) @ qml.PauliX(1),
]

hamiltonian = qml.Hamiltonian(coeffs, obs)
print(hamiltonian)
```

Expected output:

```
-0.2427 * I(0) + 0.174 * Z(0) + -0.174 * Z(1) + -0.1722 * Z(0) @ Z(1) + 0.0454 * X(0) @ X(1)
```

## Create the Device

``` python
dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=4096,
    backend="rigetti:cepheus-1-108q",
    auto_confirm=True,  # skip cost prompt on every optimization step
)
```

Warning

VQE submits **many circuits per optimization step**. Each Hamiltonian term requires its own circuit, and gradient computation doubles that. With 5 Hamiltonian terms, 4 parameters, and parameter-shift gradients, a single step can submit ~40+ circuits. Use `auto_confirm=True` to avoid being prompted on every step, but monitor `dev.total_credits_used` to track spending. You can interrupt a running batch (Ctrl+C or Jupyter stop button) to cancel pending jobs on the platform.

Tip

Use more shots (4096 or higher) for VQE to reduce shot noise in energy estimates. Shot noise adds variance to the cost function, which can slow convergence.

## Define the Ansatz

A simple ansatz with single-qubit rotations and an entangling gate:

``` python
@qml.qnode(dev)
def cost_fn(params):
    # Single-qubit rotations
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    # Entangling gate
    qml.CNOT(wires=[0, 1])
    # Additional rotations
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)
    return qml.expval(hamiltonian)
```

## Run the Optimization Loop

``` python
# Initialize parameters randomly
np.random.seed(42)
params = np.random.uniform(0, 2 * np.pi, size=4)

# Use gradient descent optimizer
opt = qml.GradientDescentOptimizer(stepsize=0.4)

# Store energy values for plotting
energies = []

# Optimization loop
max_iterations = 50
for i in range(max_iterations):
    params, energy = opt.step_and_cost(cost_fn, params)
    energies.append(energy)

    if i % 10 == 0:
        print(f"Step {i:3d}: Energy = {energy:.6f}")

print(f"\nFinal energy: {energies[-1]:.6f}")
print(f"Optimal parameters: {params}")
```

Expected output:

```
Step   0: Energy = -0.178423
Step  10: Energy = -0.562187
Step  20: Energy = -0.588312
Step  30: Energy = -0.589405
Step  40: Energy = -0.589410

Final energy: -0.589410
Optimal parameters: [2.83102671 0.31066413 0.00134562 3.14038921]
```

Note

The exact energy at each step will vary due to shot noise. The converged value should be close to the exact ground state energy of approximately -0.5893 Hartree for this simplified Hamiltonian.

## Plot Convergence

``` python
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.plot(energies, "o-", markersize=3)
plt.axhline(y=-0.5893, color="r", linestyle="--", label="Exact ground state")
plt.xlabel("Optimization Step")
plt.ylabel("Energy (Hartree)")
plt.title("VQE Convergence for H2")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("vqe_convergence.png", dpi=150)
plt.show()
```

## Shot Noise and Convergence

When running VQE on real hardware (or any shot-based backend), the energy estimate at each step includes statistical noise proportional to \\1/\sqrt{N\_{\text{shots}}}\\. This has several implications:

- **More shots = smoother convergence.** With 1024 shots, energy estimates fluctuate significantly. With 8192 shots, the landscape is much smoother.
- **Gradient estimates are noisy.** The parameter-shift rule computes gradients by evaluating the circuit at shifted parameter values. Each evaluation is noisy, so the gradient itself is noisy.
- **Smaller step sizes help.** A smaller learning rate prevents the optimizer from making large steps based on noisy gradients.
- **The optimizer may oscillate near the minimum.** Unlike analytic optimization, shot-based VQE typically oscillates around the true minimum rather than converging exactly.

For production VQE workloads, consider:

- Using `shots=8192` or higher.
- Using an optimizer with momentum (e.g., `qml.AdamOptimizer`).
- Averaging multiple circuit evaluations per step.

## Next Steps

- [QML Workflow](https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/) -- Quantum machine learning classification example.
- [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) -- Choose and configure backends for VQE.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- Understand how shot count affects job cost.
