# Kaggle guides

Kaggle kernels run every simulation of 14 qubits or fewer (root AGENTS.md,
"QPU time and calibration"). These guides play the role
`docs/notes/ibm_quantum/` plays for IBM hardware:

| Guide | Content |
| --- | --- |
| [workflow.md](workflow.md) | `scripts/kaggle_run.py` push, status and collect; authentication; how a result enters the research state |
| [substrates.md](substrates.md) | measured CPU, RAM, disk, GPU, TPU and qubit limits of each machine shape, and what runs on which substrate |
| [hypercomplex-stack.md](hypercomplex-stack.md) | the eight hypercomplex packages built and proved identically on the host and in every kernel |

`kaggle_kernel/AGENTS.md` is the instruction file that travels inside each
kernel, and `kaggle_kernel/kernel_main.py` is the program every kernel runs.
