# ibm-quantum-schemas

## NAME

ibm-quantum-schemas 0.12.20260921 -- Pydantic models for the Runtime wire
formats (executor, sampler, estimator, noise learner).

## SYNOPSIS

```python
from ibm_quantum_schemas.executor.version_2_0.models import OptionsModel, QuantumProgramModel
OptionsModel(rep_delay=250e-6).model_dump_json()
```

| Substrate | Status |
| --- | --- |
| Build host | python-ibm-quantum-schemas 0.12.20260921 (Arch), the runtime 0.50 floor in gororoba_quantum/AGENTS.md; pydantic 2.13.5 |
| Kaggle | `ibm-quantum-schemas==0.12.20260921` in the `quantum-tools` group (`scripts/kaggle_run.py` `PIN_GROUPS`), the host's version, so a kernel cannot resolve a newer release under `qiskit-ibm-runtime`'s `<1` bound; `pydantic` arrives as a runtime dependency; one of the seven pins added to the group after the retained CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu`, whose `pin_groups.json` records the twelve earlier members only; not yet installed on a kernel |

## CAPABILITIES IN THIS REPOSITORY

- Local validation of job payload fields without the service: the models
  validate and serialize `OptionsModel`, `QuantumProgramModel`,
  `QuantumProgramResultModel`, `SchedulerTimingModel`,
  `StretchValueModel`, `PauliLindbladMapModel` and the QPY/OpenQASM 3 data
  wrappers (names introspected; the example constructs `OptionsModel`).
- `SchedulerTimingModel` and `StretchValueModel` are the schemas behind the
  `scheduler_timing` and `stretch_values` execution options named in
  gororoba_quantum/AGENTS.md ("Stretch", "Billing"); they model the scheduler timing and stretch
  data of a result, which is schedule evidence and not billing evidence.
- Versions: `executor` carries `version_0_1` through `version_2_0`, `sampler`
  and `estimator` `version_0_1`, `noise_learner_v3` `version_0_1` to
  `version_0_3`.
- Not covered: sending anything. The package defines formats only.

## API ENTRY POINTS

Submodules, by introspection:

`ibm_quantum_schemas` public names (0), by introspection:

Models of `executor.version_2_0`:

`ibm_quantum_schemas.executor.version_2_0.models` public names (33), by introspection:

classes:

```text
  BaseModel, BaseParamsModel, ChunkPart, ChunkSpan, CircuitItemModel,
  CompressedQpyDataModel, CompressedTensorModel, F64CompressedTensorModel,
  ItemMetadataModel, MetadataModel, OpenQasm3DataModel, OptionsModel,
  ParamsModel, PauliLindbladMapModel, QuantumCircuit, QuantumProgramModel,
  QuantumProgramResultItemModel, QuantumProgramResultModel,
  SamplexItemModel, SamplexModel, SchedulerTimingModel, StretchValueModel,
  TypeAliasType
```

## EXAMPLES

```python
import importlib.metadata as md
import pydantic
from ibm_quantum_schemas.executor.version_2_0.models import OptionsModel, QuantumProgramModel

print("ibm-quantum-schemas", md.version("ibm-quantum-schemas"), "| pydantic", pydantic.VERSION)
print("OptionsModel fields:", list(OptionsModel.model_fields))
opts = OptionsModel(init_qubits=True, rep_delay=250e-6, scheduler_timing=True)
print("validated:", opts.model_dump_json())
try:
    OptionsModel(rep_delay="not a number")
except pydantic.ValidationError as e:
    print("invalid rep_delay:", e.errors()[0]["type"], "|", e.errors()[0]["loc"])
print("QuantumProgramModel fields:", list(QuantumProgramModel.model_fields))
```

Output:

```text
ibm-quantum-schemas 0.12.20260921 | pydantic 2.13.5
OptionsModel fields: ['init_qubits', 'rep_delay', 'scheduler_timing', 'stretch_values', 'experimental']
validated: {"init_qubits":true,"rep_delay":0.00025,"scheduler_timing":true,"stretch_values":false,"experimental":{}}
invalid rep_delay: float_parsing | ('rep_delay',)
QuantumProgramModel fields: ['shots', 'circuits', 'items', 'semantic_role', 'meas_level', 'passthrough_data']
```

## INTEROP WITH QISKIT

Indirect: qiskit-ibm-runtime builds these models from Qiskit circuits (QPY
and OpenQASM 3 wrappers). Not exercised directly here.

## CPU AND GPU

CPU (Pydantic).

## TRAPS

- Version modules coexist; import the version a given runtime release uses
  (`executor.version_2_0` is the highest present, not necessarily the one
  runtime 0.50 sends).
- `OptionsModel` defaults `stretch_values` to `False` and `experimental` to
  an empty dict, as the example's dump shows.

## LICENSE

Apache-2.0.
