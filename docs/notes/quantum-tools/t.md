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
