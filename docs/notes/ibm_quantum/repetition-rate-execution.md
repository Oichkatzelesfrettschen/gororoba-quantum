> Full piece: [https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution](https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution)

# Qubit initialization

### Package versions

The code on this page was developed using the following requirements.
We recommend using these versions or newer.

```
qiskit-ibm-runtime~=0.47.0
```

When a circuit is executed on an IBM(R) quantum processing unit (QPU), an implicit reset is typically inserted at the beginning of the circuit to ensure the qubits are initialized to zero. This is controlled by the `init_qubits` flag, set as a [primitive execution option](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-execution-options).

However, imperfections in the reset process can introduce state-preparation errors. To alleviate the error, the QPU also inserts repetition delay time (or `rep_delay`) between circuits. Each backend has a different default `rep_delay`, but it's usually set to balance reset fidelity against total execution time. Run `backend.default_rep_delay` to find the default `rep_delay` for a specific QPU.

Because all IBM QPUs use dynamic repetition rate execution, you can change the `rep_delay` for each job. Circuits you submit in a primitive job are batched together for execution on the QPU. These circuits are executed by iterating over the circuits for each shot requested; the execution is column-wise over a matrix of circuits and shots, as illustrated in the following figure.

![The first column represents shot 0.  The circuits are run in order from 0 through 3.  The second column represents shot 1.  The circuits are run in order from 0 through 3.  The remaining columns follow the same pattern. ](https://quantum.cloud.ibm.com/docs/images/guides/repetition-rate-execution/circuits_shots_matrix1.avif "Column-wise execution matrix")

Because `rep_delay` is inserted between circuits, each shot of the execution encounters this delay. Therefore, as you lower the `rep_delay`, the total QPU execution time decreases, at the expense of increasing the state preparation error rate, as the following image illustrates:

![This image shows that as the rep\_delay value is lowered, the state preparation error rate increases.](https://quantum.cloud.ibm.com/docs/images/guides/repetition-rate-execution/rep_delay.avif "Repetition delay versus error rate")

If you set both `rep_delay=0` and `init_qubits=False`, the circuits "merge" together, since the qubits will begin in the final state from the previous shot.

Note that while circuits in a primitive job are batched together for QPU execution, there is no guarantee on the order the circuits from PUBs are executed. For example, if you submit `pubs=[pub1, pub2]`, circuits from `pub1` might not run before those from `pub2`. There is also no guarantee that circuits from the same job would run as a single batch on the QPU.

## Specify `rep_delay` for a primitive job

> **Verify the rep\_delay value for a QPU**
>
> Always verify the supported `rep_delay` range for the specific QPU you are using. These values are not the same for every QPU and can also change over time.
>
> Please note that an increase in `rep_delay` will have a direct impact on your execution time and capacity consumption.

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

service = QiskitRuntimeService()

# Make sure your backend supports it
backend = service.least_busy(
    operational=True, min_num_qubits=100, dynamic_reprate_enabled=True
)

# Determine the allowable range
backend.rep_delay_range
sampler = Sampler(mode=backend)

# Specify a value in the supported range
sampler.options.execution.rep_delay = 0.0005
```

## Next steps

> **Recommendations**
>
> - Try an example in the [Quantum approximate optimization algorithm (QAOA)](https://quantum.cloud.ibm.com/docs/tutorials/quantum-approximate-optimization-algorithm) tutorial.
> - Review how to [get started with Estimator](https://quantum.cloud.ibm.com/docs/guides/get-started-with-estimator).
> - Review how to [get started with Sampler](https://quantum.cloud.ibm.com/docs/guides/get-started-with-sampler).
