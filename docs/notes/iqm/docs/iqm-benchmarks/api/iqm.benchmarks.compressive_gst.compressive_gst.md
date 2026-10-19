> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 377442fb53bbc68a88e1b6ae407603d140322c0ae54e40b48a471ef4e98b1243.

# iqm.benchmarks.compressive_gst.compressive_gst

Compressive gate set tomography.

The full benchmark executes the following steps:  
1.  Generation of circuits to measure

2.  Running of said circuits on the backend

3.  Conversion of the ideal gate set into numpy arrays to be processed by mGST

4.  Optional generation of an initialization for mGST

5.  Running mGST to get first gate set estimates

6.  Gauge optimization to the target gates using pyGSTi’s gauge optimizer

7.  Optional rerun of mGST on bootstrap data to produce error bars

8.  Generation of error measures and result tables

9.  Generation of matrix plots for the reconstructed gate set

Functions

|  |  |
|----|----|
| [`create_predefined_gate_set`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.create_predefined_gate_set.html#iqm.benchmarks.compressive_gst.compressive_gst.create_predefined_gate_set "iqm.benchmarks.compressive_gst.compressive_gst.create_predefined_gate_set")(gate_set, ...) | Create a list of quantum circuits corresponding to a predefined gate set. |
| [`parse_gate_set`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set.html#iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set "iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set")(configuration, num_qubits, ...) | Handles different gate set inputs and produces a valid gate set. |
| [`parse_layouts`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.parse_layouts.html#iqm.benchmarks.compressive_gst.compressive_gst.parse_layouts "iqm.benchmarks.compressive_gst.compressive_gst.parse_layouts")(qubit_layouts) | Checks for correct setting of qubit_layouts in the configuration and return a correct type. |

Classes

|  |  |
|----|----|
| [`CompressiveGST`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.html#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST")(backend, configuration) | SPAM-robust characterization of a set of quantum gates. |
| [`GSTConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration")(\*, benchmark, shots, ...) | Compressive GST configuration base. |

Inheritance

![Inheritance diagram of iqm.benchmarks.compressive_gst.compressive_gst](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-e04b1fdf537d952dbb0214de345847026746112e.png)
