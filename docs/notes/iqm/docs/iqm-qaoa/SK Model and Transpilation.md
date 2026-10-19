> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/SK%20Model%20and%20Transpilation.html](https://docs.iqm.tech/4.7/iqm-qaoa/SK%20Model%20and%20Transpilation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 76b15fef5098bffd036c5cbbc9329329de76411af87ad5a4b12e59080d820b9c.

# SK Model and Transpilation

The purpose of this notebook is to showcase the QAOA library working from the problem definition all the way to execution on a real hardware.

In particular, here we use QAOA to solve an instance of the Sherrington-Kirkpatrick (SK) model, a very densely connected problem, to illustrate the advantage of using our custom transpiler over the Qiskit default transpiler.

```
from iqm.applications.sk import sk_generator
from iqm.qaoa.circuits import qiskit_circuit, transpiled_circuit
from iqm.qaoa.qubo_qaoa import QUBOQAOA
from iqm.qiskit_iqm import IQMProvider
from qiskit_aer import AerSimulator
```

The SK model describes a number of binary variables, every pair of which interacts with a random interaction strength. We will solve a problem of size `problem_size`, i.e., this will be the number of binary variables and also the number of qubits that we use. The number of `shots` is set to default maximum on Resonance.

```
problem_size = 6
shots = 20000
```

We create an instance of the SK model of size `problem_size`. We specify the random distribution of the interactions between the variables to be “gaussian” (with mean 0 and variance 1). A few other distributions are possible (e.g., “uniform” or “rademacher”).

We print out the largest, lowest and average energy of the model, calculated by brute-forcing over all possible bitstrings of length `problem_size`. This may be slow if `problem_size` has been set higher than ~30.

```
my_sk_problem = next(sk_generator(n=problem_size, n_instances=1, distribution="gaussian"))
print("Problem upper bound: ", my_sk_problem.upper_bound)
print("Problem lower bound: ", my_sk_problem.lower_bound)
print("Problem average energy: ", my_sk_problem.average_quality)
```

In the following, we set up the connection to Resonance and define a simulator backend of the Garnet QPU.

Note: in general, you also need to specify the ‘usage mode’. For running on a real machine (in pay-as-you-go usage mode), the url would change to https://resonance.iqm.tech/garnet. For a specific timeslot the url would change to https://resonance.iqm.tech/garnet:timeslot

```
import os

SERVER_URL = "https://resonance.iqm.tech"
# If the token isn't saved in the environment, replace this by the token as a string.
API_TOKEN = os.environ.get("IQM_RESONANCE_API_TOKEN")
iqm_backend = IQMProvider(SERVER_URL, token=API_TOKEN, quantum_computer="garnet:mock").get_backend()
simulator = AerSimulator(method="statevector")
```

Create the QUBO QAOA instance from the problem instance, train it and then construct the QAOA circuits using 4 different methods:

- The perfect circuit without any transpilation.

- The circuit transpiled for IQM hardware, using Qiskit default transpilation function.

- The circuit transpiled for IQM hardware, using our custom transpiler.

- The circuit transpiled for IQM hardware, using the swap network strategy.

The `train` method has several possible parameters, but here the default setting is used (which uses analytical formulas since the QAOA has one layer).

```
my_qaoa = QUBOQAOA(problem=my_sk_problem, num_layers=1, initial_angles=[0.1, 0.2])
my_qaoa.train()

qc_perfect = qiskit_circuit(my_qaoa, measurements=True)

qc_default = transpiled_circuit(my_qaoa, backend=iqm_backend, transpiler="Default")

qc_hw = transpiled_circuit(my_qaoa, backend=iqm_backend, transpiler="HardwiredTranspiler")

qc_sn = transpiled_circuit(my_qaoa, backend=iqm_backend, transpiler="SwapNetwork")
```

Run the perfect circuit on perfect (noiseless simulator), print out the average energy of the samples.

```
job_perfect = simulator.run(qc_default, shots=shots)

result_dict_perfect = job_perfect.result().get_counts()
print("Energy of the samples: ", my_sk_problem.average_quality_counts(result_dict_perfect))
```

Run the Qiskit-transpiled circuit on our hardware, print out the average energy of the samples and the number of gates used.

```
job_default = iqm_backend.run(qc_default, shots=shots)

result_dict_default = job_default.result().get_counts()
print("Energy of the samples: ", my_sk_problem.average_quality_counts(result_dict_default))
print("Gates in the circuit: ", qc_default.count_ops())
```

Run the custom-transpiled circuit on our hardware, print out the average energy of the samples and the number of gates used.

```
job_hw = iqm_backend.run(qc_hw, shots=shots)

result_dict_hw = job_hw.result().get_counts()
print("Energy of the samples: ", my_sk_problem.average_quality_counts(result_dict_hw))
print("Gates in the circuit: ", qc_hw.count_ops())
```

Run the swap-network-transpiled circuit on our hardware, print out the average energy of the samples and the number of gates used.

```
job_sn = iqm_backend.run(qc_sn, shots=shots)

result_dict_sn = job_sn.result().get_counts()
print("Energy of the samples: ", my_sk_problem.average_quality_counts(result_dict_sn))
print("Gates in the circuit: ", qc_sn.count_ops())
```

If everything went as expected, the hardwired transpiler and the swap network transpiler should perform better than the `qiskit` default transpiler. The hardwired transpiler minimizes the number of 2QB gates used whereas the swap network transpiler minimizes the overall depth of the circuit. Based on the average energy obtained with the two approaches, we can judge which is better for our hardware (and this particular problem size).
