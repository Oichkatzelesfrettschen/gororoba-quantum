> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 02ee2bde7e0e0487d3fcbf5ae9619b7931880e678d8bdc434efdfbf879621794.

# detector_experiment

Full path: iqm.qrisp_iqm.qec.detector_experiment

DetectorExperiment — zero-boilerplate QEC detector experiments.

Wraps a Jasp-traceable quantum function that returns detector and observable parity checks, and automates the full LER workflow:

1.  Trace the function → Stim circuit with detector error model (DEM)

2.  Sample via Stim or any hardware backend

3.  Decode with PyMatching

4.  Compare predictions against observables → logical error rate

Also provides batched hardware submission and circuit extraction (to Stim / to IQM) for inspection and visualisation.

## Usage

```
@DetectorExperiment
def my_experiment(*args):
    ...
    return detectors, observables

# Pure Stim (fast)
ler = my_experiment.compute_LER(arg, shots=10_000)

# With a hardware backend
ler = my_experiment.compute_LER(arg, shots=10_000, backend=backend)
```

Classes

|  |  |
|----|----|
| [`DetectorExperiment`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.html#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment") | Decorator that turns a Jasp function into a detector-experiment handle. |

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.qec.detector_experiment](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-27d2fd2cfe319505184f58b02b58603b526a6f05.png)
