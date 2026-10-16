# lmfit

## NAME

lmfit 1.3.4 -- non-linear least-squares fitting with named, bounded
parameters, uncertainty estimates and model composition.

## SYNOPSIS

```python
import lmfit
model = lmfit.Model(lambda t, amp, tau, w, phi, off: off + amp * np.exp(-t / tau) * np.cos(w * t + phi))
params = model.make_params(amp=0.5, tau=100.0, w=0.03, phi=0.0, off=0.5)
params["tau"].set(min=1)
fit = model.fit(data, params, t=t, weights=1 / sigma)
fit.params["tau"].value, fit.params["tau"].stderr, fit.redchi
```

| Substrate | Status |
| --- | --- |
| Build host | python-lmfit 1.3.4 (Arch) |
| Kaggle | `lmfit==1.3.4` in the `quantum-tools` group; unmeasured on a kernel |

## CAPABILITIES IN THIS REPOSITORY

- Ramsey, T1 and T2 fits of retained jobs and replays with stated
  uncertainty: the example fits a damped Ramsey fringe from the density-matrix
  replay and recovers T2 and the readout-limited amplitude (see below).
- The readout-factor question as a fit parameter: for a Ramsey fringe measured
  through readout assignment matrix `A`, the fringe amplitude is
  `(1 - P(1|0) - P(0|1)) / 2` times the coherence (0.5 at a perfect readout and
  unit contrast). In the example the fitted amplitude is 0.4891 against 0.4908
  for the retained factor 0.9817; a fitted amplitude that is
  well below the product of this factor and the coherence the device allows is
  the signature the findings note reads in qubits 0 and 1 of Kingston.
- Global fits with shared parameters across experiments via
  `lmfit.Parameters` expressions (`expr="..."`) and `lmfit.minimize` with a
  residual function, for example a common readout factor across several
  delays; `lmfit.report_fit` prints the correlation table.
- Model comparison (`ModelResult.aic`, `bic`, `redchi`) for deciding between
  one- and two-exponential decays (`aic` and `bic` print in the example).
- qiskit-experiments performs its own SciPy fitting
  ([qiskit-experiments.md](qiskit-experiments.md)); lmfit serves repository
  analyses outside that framework.

## API ENTRY POINTS

`lmfit` public names (24), by introspection:

classes:

```text
  CompositeModel, Interpreter, Minimizer, MinimizerException, Model,
  Parameter, Parameters
```

functions:

```text
  ci_report, conf_interval, conf_interval2d, create_params, fit_report,
  minimize, report_ci, report_fit
```

modules:

```text
  confidence, jsonutils, lineshapes, minimizer, model, models, parameter,
  printfuncs, version
```

## EXAMPLES

### Ramsey fringe on the replay: tau against T2, amplitude against the readout factor

```python
import json, sys
sys.path.insert(0, "gororoba_quantum")
import numpy as np
import lmfit
import calibration_snapshot as cs
from qiskit import QuantumCircuit, transpile


def main():
    snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
    sim = cs.noise_simulator(snap)
    q0 = snap["qubits"][0]
    dt = snap["dt"]
    delays_us = np.arange(0, 301, 20)
    omega = 2 * np.pi * 0.005                 # 5 kHz software detuning, rad per microsecond

    circuits = []
    for t in delays_us:
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.delay(int(round(t * 1e-6 / dt)), 0, unit="dt")
        qc.rz(omega * t, 0)                   # software detuning
        qc.h(0)
        qc.measure(0, 0)
        circuits.append(qc)
    tcs = transpile(circuits, sim, initial_layout=[0], optimization_level=1, seed_transpiler=1)
    shots = 20000
    res = sim.run(tcs, shots=shots, seed_simulator=2).result()
    p0 = np.array([res.get_counts(i).get("0", 0) / shots for i in range(len(tcs))])

    print('p0:', np.round(p0, 3))
    model = lmfit.Model(lambda t, amp, tau, w, phi, off: off + amp * np.exp(-t / tau) * np.cos(w * t + phi))
    params = model.make_params(amp=0.5, tau=100.0, w=omega, phi=0.0, off=0.5)
    params["tau"].set(min=1)
    fit = model.fit(p0, params, t=delays_us, weights=np.full(len(p0), np.sqrt(shots / 0.25)))
    for name in ("amp", "tau", "w", "off"):
        p = fit.params[name]
        print(f"{name:3s} = {p.value:.4f} +/- {p.stderr:.4f}")
    print("reduced chi-square:", round(fit.redchi, 3), " AIC", round(fit.aic, 1), " BIC", round(fit.bic, 1), " success", fit.success)
    print("snapshot: T2 =", round(q0["t2"] * 1e6, 1), "us, T1 =", round(q0["t1"] * 1e6, 1),
          "us, readout factor =", round(1 - q0["e10"] - q0["e01"], 4), "")


if __name__ == "__main__":  # transpile of many circuits starts spawn workers
    main()
```

Output:

```text
p0: [0.996 0.88  0.637 0.37  0.187 0.132 0.223 0.401 0.604 0.751 0.786 0.73
 0.585 0.438 0.316 0.284]
amp = 0.4891 +/- 0.0027
tau = 373.3409 +/- 5.6080
w   = 0.0313 +/- 0.0001
off = 0.5057 +/- 0.0010
reduced chi-square: 1.064  AIC 5.0  BIC 8.9  success True
snapshot: T2 = 366.7 us, T1 = 313.2 us, readout factor = 0.9817
```

## INTEROP WITH QISKIT

None needed: lmfit consumes NumPy arrays. The example builds the data from
Qiskit circuits (`delay` instructions plus an `rz` software detuning)
simulated by the snapshot density-matrix backend, and it needs the `__main__`
guard because `transpile` of many circuits starts spawn workers.

## CPU AND GPU

CPU. The example fit (5 parameters, 16 points) is instantaneous next to the
density-matrix simulation that produces its data.

## TRAPS

- Without `weights`, `redchi` and `stderr` assume unit variance; pass
  `weights = 1 / sigma` with the binomial `sigma = sqrt(p (1 - p) / shots)`
  (the example uses the maximum-variance value `sqrt(shots / 0.25)`).
- A software detuning that aliases against the delay spacing (25 kHz with 20 us
  steps is exactly one half period per step) produces a flat, unfit-able
  signal: the first attempt at this example returned its starting values.
  Choose `omega * step` well below pi.
- A fit that does not move keeps the initial values and reports huge
  `stderr`; check `fit.success` and `fit.nfev`.
- `tau` is a free decay constant only if the data contain the decay; bound it
  (`min=1`) to keep the optimizer from the negative branch.

## LICENSE

BSD-3-Clause.
