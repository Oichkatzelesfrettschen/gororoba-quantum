> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 bc2f81689086c6122921851e7a5799e925203cc191a17108997f242808427d9a.

# Error mitigation

Error mitigation uses knowledge about a computer’s imperfections to reduce their impact on the returned results. It does not make the underlying hardware error-free: a mitigation may prepare additional sub-computations, change how the measurement budget is distributed, and post-process the collected data.

Perceval provides four mitigation techniques:

- [CompilationAveraging](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/compilation_averaging.html#compilationaveraging) reduces dependence on one physical compilation of an experiment.

- [DistinguishablePhotonMitigation](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html#distinguishablephotonmitigation) corrects part of the error caused by imperfect photon indistinguishability and multi-photon emission.

- [DetectorBalancing](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html#detectorbalancing) compensates for detector losses and unequal detector efficiencies.

- [PhotonRecycling](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#photonrecycling) recovers information from events in which one or two photons were lost.

The techniques address different imperfections and can be combined. A higher correction strength is not always a better choice: it can add compilation or execution overhead, may require more samples and shots to work properly, and every technique has conditions under which it is useful.

## Using mitigations with a Computer

Assign an ordered list of mitigation objects to a [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) before creating or running an execution:

``` default
>>> import perceval as pcvl
>>>
>>> computer = pcvl.SimulatedComputer("SLOS")
>>> computer.mitigations = [
...     pcvl.DistinguishablePhotonMitigation(order=1),
...     pcvl.DetectorBalancing(),
... ]
```

The computer applies the mitigations automatically to compatible computations. The caller still uses the normal [ExecutionFactory](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_factory.html#executionfactory) and [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) interfaces, and receives the usual result dictionary:

``` default
>>> experiment = pcvl.Experiment(pcvl.BS())
>>> experiment.with_input(pcvl.BasicState("|1,1>"))
>>> experiment.min_detected_photons_filter(1)
>>> factory = pcvl.ExecutionFactory(computer, experiment)
>>> with computer.acquire():
...     results = factory.sample_count(max_samples=10_000)
```

[Computations](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation) are decomposed in list order, and post-processing happens in reverse order. The [MitigationFactory](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#mitigationfactory) provides a standard, recommended order for the mitigations.

Note

Error mitigation is applied only to [Commands](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#command) that declare themselves compatible with it. Standard probability and sampling commands are compatible.

Note

The pre and post processing always apply synchronously, no matter what was asked at the [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) level.

## Choosing a preset

The [MitigationFactory](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#mitigationfactory) provides convenient presets:

``` default
>>> mitigation_factory = pcvl.MitigationFactory(pcvl.MitigationLevel.medium)
>>> computer.mitigations = mitigation_factory.build()
```

The presets are:

- `MitigationLevel.none`

- `MitigationLevel.low`

- `MitigationLevel.medium`

- `MitigationLevel.high`

Photon recycling is never enabled by a preset because its experiment and input requirements are more restrictive. It can be enabled explicitly on the factory when appropriate. See [MitigationFactory](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#mitigationfactory) for customization examples.

## Disabling and temporarily changing mitigations

Assign an empty list or `None` to disable all mitigations explicitly:

``` default
>>> computer.mitigations = []
```

Use `Computer.apply_configuration` to change mitigations temporarily:

``` default
>>> temporary_mitigations = [pcvl.DetectorBalancing()]
>>> with computer.apply_configuration(mitigations=temporary_mitigations):
...     results = factory.probs()
```

The previous configuration is restored when the context exits.

Warning

Temporarily changing a computer configuration is generally unsafe when using asynchronous work.

## Remote computers

For a [RemoteComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#remotecomputer), `mitigations` set to `None` means that the remote provider may apply its default mitigations. An empty list explicitly disables them, while a non-empty list requests the selected techniques:

``` default
>>> remote_computer.mitigations = None  # Use the remote platform defaults
>>> remote_computer.mitigations = []    # Disable remote mitigations
>>> remote_computer.mitigations = [pcvl.DetectorBalancing()]
```

By default, the requested mitigations are sent to the remote platform. Set `use_mitigations_remotely` to `False` to execute the required sub-computations remotely but combine and correct their results on the local machine:

``` default
>>> remote_computer.use_mitigations_remotely = False
```

Warning

With local mitigation of remote results, Perceval uses the imperfections known when the execution is launched. They may differ from the platform conditions when the remote job actually runs.

## Class reference

- [MitigationFactory](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html)
  - [Preset levels](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#preset-levels)
  - [Customizing a factory](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#customizing-a-factory)
    - [`MitigationLevel`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationLevel)
    - [`MitigationFactory`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory)
      - [`MitigationFactory.build()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.build)
      - [`MitigationFactory.reset_to_level()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.reset_to_level)
      - [`MitigationFactory.set_compilation_averaging()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.set_compilation_averaging)
      - [`MitigationFactory.set_custom_mitigation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.set_custom_mitigation)
      - [`MitigationFactory.set_detector_balancing()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.set_detector_balancing)
      - [`MitigationFactory.set_distinguishable_photon_mitigation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.set_distinguishable_photon_mitigation)
      - [`MitigationFactory.set_photon_recycling()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/mitigation_factory.html#perceval.runtime.error_mitigation.mitigation_factory.MitigationFactory.set_photon_recycling)
- [CompilationAveraging](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/compilation_averaging.html)
  - [Practical considerations](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/compilation_averaging.html#practical-considerations)
    - [`CompilationAveraging`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/compilation_averaging.html#perceval.runtime.error_mitigation.compilation_averaging.CompilationAveraging)
      - [`CompilationAveraging.extend_computation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/compilation_averaging.html#perceval.runtime.error_mitigation.compilation_averaging.CompilationAveraging.extend_computation)
- [DistinguishablePhotonMitigation](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html)
  - [Practical considerations](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html#practical-considerations)
    - [`DistinguishablePhotonMitigation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html#perceval.runtime.error_mitigation.distinguishable_photon_mitigation.DistinguishablePhotonMitigation)
      - [`DistinguishablePhotonMitigation.extend_computation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html#perceval.runtime.error_mitigation.distinguishable_photon_mitigation.DistinguishablePhotonMitigation.extend_computation)
      - [`DistinguishablePhotonMitigation.overhead()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/distinguishable_photon_mitigation.html#perceval.runtime.error_mitigation.distinguishable_photon_mitigation.DistinguishablePhotonMitigation.overhead)
- [DetectorBalancing](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html)
  - [Practical considerations](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html#practical-considerations)
    - [`DetectorBalancing`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html#perceval.runtime.error_mitigation.detector_balancing.DetectorBalancing)
      - [`DetectorBalancing.extend_computation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html#perceval.runtime.error_mitigation.detector_balancing.DetectorBalancing.extend_computation)
- [PhotonRecycling](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html)
  - [Automatic use with a Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#automatic-use-with-a-computer)
  - [Practical considerations](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#practical-considerations)
    - [`PhotonRecycling`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#perceval.runtime.error_mitigation.photon_recycling.PhotonRecycling)
      - [`PhotonRecycling.extend_computation()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#perceval.runtime.error_mitigation.photon_recycling.PhotonRecycling.extend_computation)
  - [Applying photon recycling directly](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#applying-photon-recycling-directly)
    - [`photon_recycling()`](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/photon_recycling.html#perceval.runtime.error_mitigation.photon_recycling.photon_recycling)
