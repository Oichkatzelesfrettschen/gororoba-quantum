> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 0e319bcb8ea203f08d76b72f077dbba49c35d1d72f5ee8482ea32ca7e3863578.

# Noise Model

``` default
>>> import perceval as pcvl
>>> noise_model = pcvl.NoiseModel(brightness=0.3, g2=0.05)
>>> computer = pcvl.SimulatedComputer("SLOS")
>>> computer.noise = noise_model
```

*class* perceval.utils.noise_model.NoiseModel(*brightness=None*, *indistinguishability=None*, *g2=None*, *g2_distinguishable=None*, *transmittance=None*, *phase_imprecision=None*, *phase_error=None*)  
The NoiseModel class contains all noise parameters which are supported by Perceval. Default value of each parameter means “no noise”, so a NoiseModel constructed with all default parameters leads to a perfect simulation.

Parameters:  
- **brightness** (`Optional`\[`float`\]) – first lens brightness of a quantum dot

- **indistinguishability** (`Optional`\[`float`\]) – chance two photons are indistinguishable

- **g2** (`Optional`\[`float`\]) – g²(0) - second order intensity autocorrelation at zero time delay. This parameter is correlated with how often two photons are emitted by the source instead of a single one.

- **g2_distinguishable** (`Optional`\[`bool`\]) – g2-generated photons indistinguishability

- **transmittance** (`Optional`\[`float`\]) – system-wide transmittance (warning, can interfere with the brightness parameter)

- **phase_imprecision** (`Optional`\[`float`\]) – maximum precision of the phase shifters (0 means infinite precision)

- **phase_error** (`Optional`\[`float`\]) – maximum random noise on the phase shifters (in radian)
