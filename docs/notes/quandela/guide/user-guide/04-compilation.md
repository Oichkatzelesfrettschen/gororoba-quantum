> Full piece: [https://cloud.quandela.com/webide/guide/user-guide/04-compilation](https://cloud.quandela.com/webide/guide/user-guide/04-compilation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/user-guide/04-compilation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Compilation

To perform a computation on a Processor - you are providing an input state, a circuit, potential post-selection and a command to be executed. All of this is compiled into a sequence of hardware controls that will eventually produce measurements returned to your program or algorithm for further classical processing. The goal of the compilation is therefore to adapt your request to the [Hardware Topology and Constraints](#hardware-topology-and-constraints).

While most of this compilation process runs generally smoothly, it is important to understand how it works to help you getting most of the computation or dealing with special corner cases.

The compilation is in three phases:

- [Adaptation of the input state](#input-state-adaptation)
- [Circuit Transpilation](#circuit-transpilation)
- [Detection Configuration](#detection-configuration)

This compilation process might take some time so if you are performing sequence of similar computations, or if you want to reduce the time spent on QPU, you can perform [pre-compilation](#pre-compilation) on the equivalent simulator.

## Hardware Topology and Constraints

Each platform (physical or simulated) is exposing its specifications in the API or through the web interface.

The specifications cover:

1. the number of photons that you can send to the chip (`remote_qpu.constraints['max_photon_count']`)
2. the input modes where these photons can be sent (`remote_qpu.specs['connected_input_modes']`)
3. the characteristic of the photonic chip (`remote_qpu.specs['specific_circuit']`)
4. potentially the type of the photon detector and the possible constraints on the detection
5. and finally the native commands that the QPU control can handle (`remote_qpu.specs['available_commands']`)

> These parameters might depend on the access that you have been granted to the platform by Quandela Team or on the plan you purchased.

For instance, each QPU is implementing a Specific Circuit that can be retrieved when connecting to the QPU:

```python
specific_circuit = remote_qpu.specs['specific_circuit']
```

Most often, a QPU circuit can be configured and you can visualize the circuit and see the available parameters:

```python
pcvl.pdisplay(specific_circuit)
```

![image-20221116-150549.png](https://cloud.quandela.com/webide/docs-assets/97058817.png)

```python
> print(list(specific_circuit.params))
['phi_0', 'phi_2', 'phi_1', 'phi_3']
```

These parameters can be modified to manually configure the circuit - see [Perceval - Parameters](https://perceval.quandela.net/docs/tools.html#parameters).

## Input State Adaptation

The first task of the compilation is to adapt the input state to the physically connected input modes to the circuit. This is achieved by adding routing permutations to your circuit in order connect to actual physical photon source.

For instance for a 6 mode circuit, and a QPU connected to mode `[0,2,4]`, the adaptation will be as follow:

| `\|1,0,1,0,0,0>` | `\|0,0,1,1,0,0>` | `\|0,0,1,0,1,0>` |
| :---: | :---: | :---: |
| ![image-20221117-132412.png](https://cloud.quandela.com/webide/docs-assets/98697241.png) | ![image-20221117-132309.png](https://cloud.quandela.com/webide/docs-assets/98435079.png) | ![image-20221117-132340.png](https://cloud.quandela.com/webide/docs-assets/98697235.png) |

> The consequence of this automatic input adaptation is that the circuit or the unitary will be modified - in particular if your initial circuit was compatible with the specific circuit of the processor, it won't be compatible anymore and will go through Transpilation.

## Circuit Transpilation

If the circuit is not compatible with the **Specific Circuit** (or a subset of it), it is converted into its unitary matrix (see [Perceval - Unitary Matrix](https://perceval.quandela.net/docs/circuits.html#unitary-matrices)). Assuming the number of modes of the photonic chip is greater or equal than the required number of modes, the transpilation process will attempt to find a sub-circuit able to encode the unitary as accurately as possible, while the unused modes parameters will be configured to act as complete mirror to avoid any transmission between the modes of interest and the extraneous modes.

![image-20221117-084654.png](https://cloud.quandela.com/webide/docs-assets/98402305.png)

> Note that while it is possible that the fidelity of the unitary implementation improves on a larger size than the one of the unitary (due to redundancy of parameters that can compensate for potential manufacturing defects), on the other hand use of a larger chip is also likely to reduce the total transmission. The choice of the optimal processor for a given circuit will be a balance between these two factors that will also depend on the algorithm sensibility to loss and fidelity.

## Detection Configuration

Finalization of the computing is performed during photon detections. Most of the time, we are interested in coincidences between multiple photon detections and configure the *physical post-selection* to keep only detection with a minimal number of mode in a coincidence. This is done with `remote_qpu.mode_post_selection(n)` in the configuration of a remote processor.

> This parameter implemented on the circuit logic connected to the photon detector is actually very important to understand. If you set it too low, you will mainly detect incomplete states. If you set it too high, your request might take a lot of time for completing a sampling. Before configuring this parameter, make sure to estimate the actual time it might take, based on the circuit transmittance that is provided in the platform performance. For a given circuit, you can also estimate the expected number of coincidences using the associated simulator.

## Pre-Compilation

The compilation sequence can be time-consuming (generally dependent on the number of modes of your circuit). To save QPU time, or to accelerate a sequence of tasks, you can take benefit of **pre-compilation** and even prepare pre-compilation on simulator and apply it on the QPU.

Indeed, when you receive results back from a specific simulator or from a QPU - you can retrieve the result of the Input State Adaptation in `computed_input` and the result of the transpilation in `computed_circuit`. You can then use directly these values on subsequent jobs as following:

```python
# run the circuit on SIMULATOR first

remote_qpu = pcvl.RemoteProcessor("sim:ascella", token_qcloud)
remote_qpu.with_input(input_state)
remote_qpu.set_circuit(circuit)
remote_qpu.mode_post_selection(n_post_selection)

# synchronous syntax
sampler = pcvl.algorithm.Sampler(remote_qpu, max_shots_per_call=3*nsamples)
results = sampler.sample_count(nsamples)["results"]

compiled_circuit = results["computed_circuit"]
compiled_input = results["computed_input"]

remote_qpu = pcvl.RemoteProcessor("qpu:ascella", token_qcloud)
remote_qpu.with_input(compiled_input)
remote_qpu.set_circuit(compiled_circuit)

# asynchronous syntax
async_job = sampler.sample_count.execute_async(nsamples)

previous_prog = 0
with tqdm(total=1, bar_format='{desc}{percentage:3.0f}%|{bar}|') as tq:
    tq.set_description(f'Get {nsamples} samples from {remote_qpu.name}')
    while not async_job.is_complete:
        tq.update(async_job.status.progress-previous_prog)
        previous_prog = async_job.status.progress
        time.sleep(1)
    tq.update(1-previous_prog)
    tq.close()

results = async_job.get_results()
```
