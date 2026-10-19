> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6c6f55ec64393ddd0a56d8ee9291615214b0ebdbd156d6de8a2db20be275f642.

# cpc

Full path: iqm.cpc

IQM Circuit to Pulse Compiler.

IQM Circuit to Pulse Compiler is a Python-based library for converting quantum circuits into [`instruction schedules`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)") (which map `Station Control` controller names to lists of hardware instructions) and Station Control settings required for circuit execution, using the calibration data it is given. The generated schedules and settings can be sent to Station Control for execution on real or simulated quantum hardware.

Subpackages and modules

|  |  |
|----|----|
| [`compiler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.html#module-iqm.cpc.compiler "iqm.cpc.compiler") | Compile quantum circuits into instruction schedules and settings that can be executed on a station. |
| [`core`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.html#module-iqm.cpc.core "iqm.cpc.core") | Core utilities for the Compiler. |
| [`interface`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.html#module-iqm.cpc.interface "iqm.cpc.interface") | Data models used by the API. |
| [`qir_utils`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.qir_utils.html#module-iqm.cpc.qir_utils "iqm.cpc.qir_utils") | Utilities for working with QIR modules. |
| [`quantum_architecture`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.quantum_architecture.html#module-iqm.cpc.quantum_architecture "iqm.cpc.quantum_architecture") | Creating static and dynamic quantum architectures. |
| [`utils`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.html#module-iqm.cpc.utils "iqm.cpc.utils") | Utility functions for the circuit-to-pulse compiler. |
