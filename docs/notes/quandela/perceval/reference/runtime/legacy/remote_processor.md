> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 d14a53666d71b4ea08300e19f774dff40fe754035f3d31875fc8b518bc931978.

# RemoteProcessor

`RemoteProcessor` class is the entry point for sending a computation on a remote platform (a simulator or a QPU). [Quandela Cloud](https://cloud.quandela.com) is a public cloud service with available QPUs and simulators. An access token on the selected service is required to connect to a remote platform (e.g. an access token to Quandela Cloud with rights is required to follow this tutorial: [Remote computing](https://perceval.quandela.net/docs/v1.3/notebooks/Remote_Computation_Tutorial.html#Remote-Computing)).

Once you have created a token suiting your needs (it needs to be given the rights to run jobs on target platforms), you may save it once and for all on your computer by using the [RemoteConfig](https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html#remoteconfig).

A token value can also be set to every `RemoteProcessor` object

``` default
>>> remote_simulator = RemoteProcessor("platform:name", "YOUR_TOKEN")
```

For the rest of this page, let’s assume a token is saved in your environment.

A given remote platform is only able to support a specific set of commands. For instance, a real QPU is natively able to sample output detections, but not to compute probabilities of output states versus an input state. Hardware constraints might also enforce the coincidence counting type, or the type of detection (threshold detection or photon number resolving).

When creating a `RemoteProcessor`, you can query its capabilities

``` default
>>> remote_simulator = RemoteProcessor("qpu:belenos")
>>> print(remote_simulator.available_commands)
['sample_count', 'samples']
```

This means qpu:belenos is only able to natively answer to sample_count and samples commands (i.e. return the results of a sampling task).

## Creation

`RemoteProcessor` has the same API and fills the same role as a local [Processor](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/processor.html#processor) but are executed remotely by a Cloud platform (a real QPU or an online simulator).

RemoteProcessors are created slightly differently than normal Processors.

First, they require connexion information to a given Cloud provider:  
- A token (or API key) being the credentials to authenticate the user remotely.

- A URL to the Cloud API

- Optionally, a proxy configuration

All these information are used to create a [RPCHandler](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/rpchandler.html#rpchandler) which could be passed instead. Also, these info can be saved in your local computer persistent [RemoteConfig](https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html#remoteconfig).

In terms of circuit initialisation, here are the specifics:

``` default
>>> rp = pcvl.RemoteProcessor("sim:slos", token=..., m=3, noise=pcvl.NoiseModel(0.9))  # m is an optional kwarg here
```

If `m` is not specified, it is inferred from the first added component. They can also be created by converting a local Processor, keeping all defined objects (input state, filter, ports…).

``` default
>>> rp = pcvl.RemoteProcessor.from_local_processor(p, "sim:slos", token=...)
```

From there, all composition rules are the same, and local processors can be added to remote processors.

## Input state

Only non-polarized BasicState and LogicalState input are accepted for RemoteProcessors.

## Computation

The only way to compute with a RemoteProcessor is to use it in a Quantum Algorithm.

## Miscellaneous

Some platforms expose specs (see [PlatformSpecs](https://perceval.quandela.net/docs/v1.3/reference/runtime/platform_specs.html#platformspecs)) that give information about what the platform is, and what it can and can’t do. They can be retrieved using the property `rp.specs`.

Some constraints, available through `rp.constraints`, must be fulfilled in order for a Job to be able to be completed. These include (but are not limited to) the number of photons, the number of modes, the number of photons per mode…

The performances of the source can also be retrieved using the property `rp.performance`.

The needed resources in terms of samples or shots can be estimated by a RemoteProcessor

``` default
>>> rp.estimate_required_shots(nb_samples=10000)
```

Note that this uses a partially noisy local simulation, so it can be expensive to compute.

*class* perceval.runtime.legacy.remote_processor.RemoteProcessor(*name=None*, *token=None*, *url=None*, *proxies=None*, *rpc_handler=None*, *m=None*, *noise=None*)  
check_input(*input_state*)  
Check if a Fock state input matches with the current processor configuration

Return type:  
`None`

compute_physical_logical_perf(*value*)  
Split performance into the physical and logical parts - when available

Parameters:  
**value** (`bool`) – True to compute the physical and logical performances, False otherwise.

estimate_expected_samples(*nshots*, *param_values=None*)  
Compute an estimate number of samples the user can expect given the platform and the user request. The circuit, input state, minimum photon filter are taken into account.

Parameters:  
- **nshots** (`int`) – Number of shots the user is willing to consume

- **param_values** (`Optional`\[`dict`\]) – Key/value pairs for variable parameters inside the circuit. All parameters need to be fixed for this computation to run.

Return type:  
`int`

Returns:  
Estimate of the number of samples of interest the user can expect back

estimate_required_shots(*nsamples*, *param_values=None*)  
Compute an estimate number of required shots given the platform and the user request. The circuit, input state, minimum photon filter are taken into account.

Parameters:  
- **nsamples** (`int`) – Number of expected samples of interest

- **param_values** (`Optional`\[`dict`\]) – Key/value pairs for variable parameters inside the circuit. All parameters need to be fixed for this computation to run.

Return type:  
`int`

Returns:  
Estimate of the number of shots the user needs to acquire enough samples of interest

get_current_noise()  
Return type:  
[`NoiseModel`](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html#perceval.utils.noise_model.NoiseModel "perceval.utils.noise_model.NoiseModel")

Returns:  
The NoiseModel associated to the last performance characterization of the remote platform. Simulators without hardware return a NoiseModel with a default transmittance value. Note that, depending on the platform, the performance dictionary may have more information that can’t be translated into NoiseModel

log_resources(*command*, *extra_parameters*)  
Log resources of the remote processor

Parameters:  
- **command** (`str`) – name of the method used

- **extra_parameters** (`dict`) – extra parameters to log

set_circuit(*circuit*)  
Removes all components and replace them by the given circuit.

Parameters:  
**circuit** (`ACircuit`) – The circuit to start the processor with

Returns:  
Self to allow direct chain this with .add()
