> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f52bbd921edb7b588cac228dcf57de3818dcb0560095fc50f891e8571977dec5.

# qubit_selector

Full path: iqm.qubit_selector.qubit_selector

Automatically select the best layout for running an algorithm on IQM’s quantum computer.

Classes

|  |  |
|----|----|
| [`CalibrationDataManager`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CalibrationDataManager.html#iqm.qubit_selector.qubit_selector.CalibrationDataManager "iqm.qubit_selector.qubit_selector.CalibrationDataManager") | Manage calibration data retrieval for the QPU. |
| [`CalibrationType`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CalibrationType.html#iqm.qubit_selector.qubit_selector.CalibrationType "iqm.qubit_selector.qubit_selector.CalibrationType") | Enumeration representing different types of calibration methods. |
| [`CostEvaluator`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CostEvaluator.html#iqm.qubit_selector.qubit_selector.CostEvaluator "iqm.qubit_selector.qubit_selector.CostEvaluator") | Evaluates cost functions for quantum circuit layouts. |
| [`CostFunction`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CostFunction.html#iqm.qubit_selector.qubit_selector.CostFunction "iqm.qubit_selector.qubit_selector.CostFunction") | Enumeration representing different types of cost functions used in the application. |
| [`LayoutGenerator`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.LayoutGenerator.html#iqm.qubit_selector.qubit_selector.LayoutGenerator "iqm.qubit_selector.qubit_selector.LayoutGenerator") | Generates unique layouts for quantum circuits based on calibration data and backend architecture. |
| [`ObservationType`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.ObservationType.html#iqm.qubit_selector.qubit_selector.ObservationType "iqm.qubit_selector.qubit_selector.ObservationType") | Enumeration representing relevant keys to fetch for each operation in the observations. |
| [`ReadoutMode`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.ReadoutMode.html#iqm.qubit_selector.qubit_selector.ReadoutMode "iqm.qubit_selector.qubit_selector.ReadoutMode") | Enumeration representing how to use readout fidelity in cost function evaluation. |

Inheritance

![Inheritance diagram of iqm.qubit_selector.qubit_selector](https://docs.iqm.tech/4.7/iqm-qubit-selector/_images/inheritance-35f3e1f4a30735404bf0afdc394563bd450e7000.png)
