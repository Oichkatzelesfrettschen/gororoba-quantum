> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/platform_specs.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/platform_specs.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 8a719abcdf81cae0455984abf8c5f21f5f4d7c47b70636d3bca945a29d215e81.

# PlatformSpecs

*class* perceval.runtime.platform_specs.PlatformSpecs  
This class represents the specs of any RemoteComputer. It guarantees that some common fields exist by giving some default values.

Common fields are accessible through properties, and should be accessed through them. If a given common field is not filled by the computer, it will return None or a default value of the correct type. If a given RemoteComputer specs contain a field unknown to this class, it can still be accessed through the dict item syntax

``` default
>>> rc = RemoteComputer(...)
>>> rs = rc.specs  # This is a PlatformSpecs object
>>> pdisplay(rs.architecture)
>>> print(rs["this_platform_specific_spec"])
```

List of included fields (not extensive):  
- architecture

- available_commands

- constraints

- min_client_version

- pcvl_version

- software_versions

- parameters

- type

*property* architecture*: [Experiment](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment") \| None*  
The architecture is an Experiment representing the hardware implementation of the platform, including

> - input state with maximum number of photons for each mode
>
> - optical components
>
> - detectors if they are imperfect

Returns:  
The experiment representing the physical hardware of the RemoteComputer, or None if the RemoteComputer isn’t linked to a hardware chip,

*property* available_commands*: list\[str\]*  
Returns:  
the list of command names available for this platform

*property* commands*: list\[[perceval.runtime.command.Command](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#perceval.runtime.command.Command "perceval.runtime.command.Command")\]*  
Returns:  
the list of command available for this platform

*property* connected_input_modes*: list\[int\]*  
Returns:  
A list containing the mode numbers where a photon can be sent to the chip on the platform hardware. The list may be empty if there is no hardware

*property* constraints*: dict\[str, Any\]*  
Returns:  
A dictionary detailing the constraints of the platform (min/max number of modes/photons, …). May be empty if there are no constraints

*property* description*: str*  
Returns:  
A short description of the platform

*property* detector*: str \| None*  
Returns:  
The type of the detection, as a str, or None if there is no hardware

*property* min_client_version*: str*  
Returns:  
The minimum version of perceval that the user must have for the call to this platform to resolve correctly

*property* parameters*: dict\[str, str\]*  
Returns:  
A dictionary containing the possible parameters of the platform. \* The key must be given to the platform using the `set_parameters()` method of the RemoteComputer. \* The value is a description of what the parameter does.

*property* pcvl_version*: str*  
Returns:  
The version of perceval on the platform

*property* software_versions*: dict\[str, str\]*  
Returns:  
The main software versions of the platform (ex: perceval, exqalibur…)

*property* specific_circuit*: ACircuit \| None*  
Returns:  
the hardware implemented circuit of the platform, or None it isn’t linked to a hardware chip, or not representable as a unitary Circuit
