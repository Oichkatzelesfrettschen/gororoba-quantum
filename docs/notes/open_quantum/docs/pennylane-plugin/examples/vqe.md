> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/vqe/](https://docs.openquantum.com/pennylane-plugin/examples/vqe/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 018b5bb478fdcf53175bcb6df241bff2dc0eda08ae91220b695f230191afd3c4.

# Variational Quantum Eigensolver (VQE)

This tutorial demonstrates how to use the Variational Quantum Eigensolver (VQE) algorithm on Open Quantum to find the ground state energy of a simple molecular hydrogen (H2) Hamiltonian.

## Background

VQE is a hybrid quantum-classical algorithm that uses a parameterized quantum circuit (ansatz) to prepare trial states, measures the energy expectation value on quantum hardware, and optimizes the parameters classically to minimize the energy.

## Define the Hamiltonian

For a simplified 2-qubit H2 model at equilibrium bond distance, the Hamiltonian can be expressed as a sum of Pauli terms:

[](#__codelineno-0-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-0-2)`import`` ``numpy`` ``as`` ``np`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`# Simplified H2 Hamiltonian (2-qubit, equilibrium bond length ~0.735 A)`\
[](#__codelineno-0-5)`coeffs`` ``=`` ``[`\
[](#__codelineno-0-6)`    ``-``0.2427``,``   ``# Identity`\
[](#__codelineno-0-7)`     ``0.1740``,``   ``# Z0`\
[](#__codelineno-0-8)`    ``-``0.1740``,``   ``# Z1`\
[](#__codelineno-0-9)`    ``-``0.1722``,``   ``# Z0 Z1`\
[](#__codelineno-0-10)`     ``0.0454``,``   ``# X0 X1`\
[](#__codelineno-0-11)`]`\
[](#__codelineno-0-12)\
[](#__codelineno-0-13)`obs`` ``=`` ``[`\
[](#__codelineno-0-14)`    ``qml``.``Identity``(``0``),`\
[](#__codelineno-0-15)`    ``qml``.``PauliZ``(``0``),`\
[](#__codelineno-0-16)`    ``qml``.``PauliZ``(``1``),`\
[](#__codelineno-0-17)`    ``qml``.``PauliZ``(``0``)`` ``@`` ``qml``.``PauliZ``(``1``),`\
[](#__codelineno-0-18)`    ``qml``.``PauliX``(``0``)`` ``@`` ``qml``.``PauliX``(``1``),`\
[](#__codelineno-0-19)`]`\
[](#__codelineno-0-20)\
[](#__codelineno-0-21)`hamiltonian`` ``=`` ``qml``.``Hamiltonian``(``coeffs``,`` ``obs``)`\
[](#__codelineno-0-22)`print``(``hamiltonian``)`\

Expected output:

[](#__codelineno-1-1)`-0.2427 * I(0) + 0.174 * Z(0) + -0.174 * Z(1) + -0.1722 * Z(0) @ Z(1) + 0.0454 * X(0) @ X(1)`\

## Create the Device

[](#__codelineno-2-1)`dev`` ``=`` ``qml``.``device``(`\
[](#__codelineno-2-2)`    ``"openquantum.device"``,`\
[](#__codelineno-2-3)`    ``wires``=``2``,`\
[](#__codelineno-2-4)`    ``shots``=``4096``,`\
[](#__codelineno-2-5)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-2-6)`    ``auto_confirm``=``True``,``  ``# skip cost prompt on every optimization step`\
[](#__codelineno-2-7)`)`\

Warning

VQE submits **many circuits per optimization step**. Each Hamiltonian term requires its own circuit, and gradient computation doubles that. With 5 Hamiltonian terms, 4 parameters, and parameter-shift gradients, a single step can submit ~40+ circuits. Use `auto_confirm=True` to avoid being prompted on every step, but monitor `dev.total_credits_used` to track spending. You can interrupt a running batch (Ctrl+C or Jupyter stop button) to cancel pending jobs on the platform.

Tip

Use more shots (4096 or higher) for VQE to reduce shot noise in energy estimates. Shot noise adds variance to the cost function, which can slow convergence.

## Define the Ansatz

A simple ansatz with single-qubit rotations and an entangling gate:

[](#__codelineno-3-1)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-3-2)`def`` ``cost_fn``(``params``):`\
[](#__codelineno-3-3)`    ``# Single-qubit rotations`\
[](#__codelineno-3-4)`    ``qml``.``RY``(``params``[``0``],`` ``wires``=``0``)`\
[](#__codelineno-3-5)`    ``qml``.``RY``(``params``[``1``],`` ``wires``=``1``)`\
[](#__codelineno-3-6)`    ``# Entangling gate`\
[](#__codelineno-3-7)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-3-8)`    ``# Additional rotations`\
[](#__codelineno-3-9)`    ``qml``.``RY``(``params``[``2``],`` ``wires``=``0``)`\
[](#__codelineno-3-10)`    ``qml``.``RY``(``params``[``3``],`` ``wires``=``1``)`\
[](#__codelineno-3-11)`    ``return`` ``qml``.``expval``(``hamiltonian``)`\

## Run the Optimization Loop

[](#__codelineno-4-1)`# Initialize parameters randomly`\
[](#__codelineno-4-2)`np``.``random``.``seed``(``42``)`\
[](#__codelineno-4-3)`params`` ``=`` ``np``.``random``.``uniform``(``0``,`` ``2`` ``*`` ``np``.``pi``,`` ``size``=``4``)`\
[](#__codelineno-4-4)\
[](#__codelineno-4-5)`# Use gradient descent optimizer`\
[](#__codelineno-4-6)`opt`` ``=`` ``qml``.``GradientDescentOptimizer``(``stepsize``=``0.4``)`\
[](#__codelineno-4-7)\
[](#__codelineno-4-8)`# Store energy values for plotting`\
[](#__codelineno-4-9)`energies`` ``=`` ``[]`\
[](#__codelineno-4-10)\
[](#__codelineno-4-11)`# Optimization loop`\
[](#__codelineno-4-12)`max_iterations`` ``=`` ``50`\
[](#__codelineno-4-13)`for`` ``i`` ``in`` ``range``(``max_iterations``):`\
[](#__codelineno-4-14)`    ``params``,`` ``energy`` ``=`` ``opt``.``step_and_cost``(``cost_fn``,`` ``params``)`\
[](#__codelineno-4-15)`    ``energies``.``append``(``energy``)`\
[](#__codelineno-4-16)\
[](#__codelineno-4-17)`    ``if`` ``i`` ``%`` ``10`` ``==`` ``0``:`\
[](#__codelineno-4-18)`        ``print``(``f``"Step ``{``i``:``3d``}``: Energy = ``{``energy``:``.6f``}``"``)`\
[](#__codelineno-4-19)\
[](#__codelineno-4-20)`print``(``f``"``\n``Final energy: ``{``energies``[``-``1``]``:``.6f``}``"``)`\
[](#__codelineno-4-21)`print``(``f``"Optimal parameters: ``{``params``}``"``)`\

Expected output:

[](#__codelineno-5-1)`Step   0: Energy = -0.178423`\
[](#__codelineno-5-2)`Step  10: Energy = -0.562187`\
[](#__codelineno-5-3)`Step  20: Energy = -0.588312`\
[](#__codelineno-5-4)`Step  30: Energy = -0.589405`\
[](#__codelineno-5-5)`Step  40: Energy = -0.589410`\
[](#__codelineno-5-6)\
[](#__codelineno-5-7)`Final energy: -0.589410`\
[](#__codelineno-5-8)`Optimal parameters: [2.83102671 0.31066413 0.00134562 3.14038921]`\

Note

The exact energy at each step will vary due to shot noise. The converged value should be close to the exact ground state energy of approximately -0.5893 Hartree for this simplified Hamiltonian.

## Plot Convergence

[](#__codelineno-6-1)`import`` ``matplotlib.pyplot`` ``as`` ``plt`\
[](#__codelineno-6-2)\
[](#__codelineno-6-3)`plt``.``figure``(``figsize``=``(``8``,`` ``5``))`\
[](#__codelineno-6-4)`plt``.``plot``(``energies``,`` ``"o-"``,`` ``markersize``=``3``)`\
[](#__codelineno-6-5)`plt``.``axhline``(``y``=-``0.5893``,`` ``color``=``"r"``,`` ``linestyle``=``"--"``,`` ``label``=``"Exact ground state"``)`\
[](#__codelineno-6-6)`plt``.``xlabel``(``"Optimization Step"``)`\
[](#__codelineno-6-7)`plt``.``ylabel``(``"Energy (Hartree)"``)`\
[](#__codelineno-6-8)`plt``.``title``(``"VQE Convergence for H2"``)`\
[](#__codelineno-6-9)`plt``.``legend``()`\
[](#__codelineno-6-10)`plt``.``grid``(``True``,`` ``alpha``=``0.3``)`\
[](#__codelineno-6-11)`plt``.``tight_layout``()`\
[](#__codelineno-6-12)`plt``.``savefig``(``"vqe_convergence.png"``,`` ``dpi``=``150``)`\
[](#__codelineno-6-13)`plt``.``show``()`\

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
