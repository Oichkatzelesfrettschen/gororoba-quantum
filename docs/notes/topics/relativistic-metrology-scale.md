# Relativistic and astronomical couplings against the measured instabilities

This note compares the size of every relativistic or astronomical effect on the
repository's devices with the instabilities the retained records measure. Every
relativistic phase on these devices sits six or more orders of magnitude below
the smallest instability the records resolve, so no retained or planned
acquisition measures gravity, rotation or motion through the cosmic microwave
background. It also states what the Belenos "light cone" of
`scripts/qd_belenos_cone.py` is.

## The Belenos light cone is a mode-reachability set

`qd_belenos_cone.py` defines the cone of a served mesh by amplitude. A mode is
in the cone when its peak occupancy along the ideal propagation
(`qd_belenos_mesh.peak_occupancy`) exceeds `CONE_FLOOR` (1e-6). A mode is also
in the cone when the exact dephasing channel at `CONE_SIGMA` 0.5 rad heater and
`CONE_SIGMA_THETA` 0.1 rad coupler noise reaches it at `NOISY_FLOOR` (1e-3) or
more. `peak_occupancy` steps the photon's amplitude through the mesh element
list in order, so the "time" axis is position in that list, and the "space"
axis is the mode index. Each beam splitter couples two neighboring modes, so
the reachable modes widen by at most one per beam splitter. That is the discrete causal
cone of a layered circuit, the same object as the backward light cone of a
gate circuit (docs/notes/papers/2411.05760.md). Every mode of the full Belenos
mesh is reachable from any source, which is why the code defines the cone by
amplitude and not by reachability.

The cone has no metric, no proper time and no speed of light. It is the support
of one photon's amplitude in mode space, and an off-cone click flags a count
that the mesh's routing cannot produce. The sedenion content of the box-kite
circuits it reads sits in which 4 x 4 case unitary the mesh realizes
(`qd_belenos_mesh.source_target`). That content has no bearing on the cone's
geometry. The photon itself travels through the chip at its group velocity,
inside the ordinary spacetime light cone like any signal; the notes record
neither the waveguide group index nor the optical path length, so the transit
time tau stays a parameter below.

## Scale of each coupling

Device facts come from docs/notes/quandela/literature.md: the 24-mode Belenos
chip is a 15 x 134 mm^2 laser-written glass interferometer operated at 925 nm
(optical frequency 3.24e14 Hz). The Heron r2 Target snapshot
(docs/evidence/heron_platform/backend_configuration.json) carries no qubit
frequency (0 non-None `frequency` entries), so the Heron rows scale per GHz of
qubit frequency.

| Coupling | Device | Size | Basis |
|---|---|---|---|
| Earth-rotation Sagnac phase, single-pass interferometer enclosing the whole chip footprint | Belenos | at most 6.6e-9 rad | 4 pi Omega_E A / (lambda c), Omega_E = 7.292e-5 rad/s, A = 2.01e-3 m^2; real interferometer loops enclose far less |
| Gravitational redshift between paths 15 mm apart in height, over a chip transit time tau | Belenos | 3.3e-12 rad per ns of tau | 2 pi nu tau g dh / c^2; tau is unrecorded |
| Gravitational redshift across 1 mm of a chip, over 152.3 us | Heron r2 | 6.9e-16 rad per GHz of qubit frequency per us per mm, 1.0e-13 rad per GHz here | the fitted component envelope of the October 20 Ramsey beat model |
| Height of the room-temperature reference oscillator above the chip, taken as 2 m | Heron r2 | fractional 2.2e-16, about 2e-7 Hz per GHz, static | absorbed into the calibrated qubit frequency like any static offset |
| Motion relative to the CMB, 369.82 km/s ([Planck 2018](../papers/1807.06205.md)) | all | gamma - 1 = 7.6e-7, common to qubit, reference and detector | local Lorentz invariance makes a common velocity unobservable in a co-moving experiment |

The measured instabilities these would have to explain:

| Measured instability | Size | Record |
|---|---|---|
| Kingston two-qubit coherence rotation over 4.392 us of added idle | -1.130 rad, a 41.0 kHz detuning | results/live/2026-10-15T030748.903241Z/coherence-analysis.json |
| Belenos run-to-run jump of the superposition class mean | sample SD 0.0038 against a counting error near 0.0004 | results/quandela/bdsc_drift_series_diagnostic_pinned.json |
| Belenos six-state sum-rule deficit | -0.199 mean over 56 contrasts, every one negative | same record, `sum_rules` |
| Heron Ramsey label switching | correlation time 26.2 ms (28.3 ms at the chunk wall period) | results/live/2026-10-21T064222.721454Z/line-switching-759d82d74c57.json |
| Tuna-17 shot-record line | 50.38 +- 3.99 Hz in wall-clock time | results/quantum_inspire/tuna_17_shot_record_line.json |

The smallest of these is a probability change of a few parts in 1e3. The
largest relativistic phase in the first table is 6.6e-9 rad. For the
first-order effect of the Belenos footprint Sagnac phase to equal the 0.0038
jump, the chip would need about 1e6 times its footprint as a coherently
enclosed loop. The Tuna-17 line is at the 50 Hz frequency of the European mains
supply. That points to an electrical or mechanical coupling in the laboratory,
which the same record does not identify.

## What an astronomical coupling would have to show

Earth's rotation itself gives an Earth-fixed device a static Sagnac phase,
which only reorientation or area reversal exposes. A coupling to a direction
fixed among the stars, such as a preferred-frame effect, repeats once per
sidereal day (23 h 56 min 4 s). Laboratory temperature, maintenance and queue load repeat
once per solar day. The two frequencies differ by one cycle per year, so their
phases separate by 2 pi / 365.24 rad per day: 0.0086 rad over the 12 h drift
series and 0.24 rad over 14 days. Telling them apart at one radian needs about
58 days of evenly sampled data with recorded execution times. An attribution
also needs a prediction outside the fit:
- an effect that reverses with the device's orientation;
- an effect that scales with enclosed area;
- a coincidence with an independent particle detector;
- a successful prediction of a later time block.

Ionizing radiation is the one astronomical coupling with a measured effect on
superconducting qubits: correlated error bursts that relax over tens of
milliseconds. The IBM records keep shot order without shot timestamps, so the
26.2 ms switching in the Ramsey arms can only be compared with that timescale,
not attributed to it. An attribution needs the spatial spread of simultaneous
errors across neighboring qubits within one shot, and a relaxation signature
beside the phase signature. A run that reads many neighboring qubits in every
shot can measure both, and that is the only cosmic-origin hypothesis these
devices can test.

## Sources

The relativistic couplings follow the [fiber Sagnac entanglement experiment](../papers/2310.16903.md),
the [millimeter-scale redshift gradient](../papers/2109.12238.md), the
[proper-time visibility witness](../papers/1105.4531.md) and its
[composite-particle extension](../papers/1311.1095.md), the treatment of solar gravity in a freely
falling geocentric frame ([Ashby and Nelson](../papers/ashby-nelson-2009-gps-relativity.md)), the
[local position invariance null test](../papers/ashby-2018-null-test-lpi.md), the
[orientation-dependent Lorentz-violation bounds](../papers/2206.00570.md), the
[spin-entropy covariance limit](../papers/quant-ph-0203033.md) and the
[satellite entanglement link](../papers/1707.01339.md). The radiation coupling follows
[ionizing radiation and transmon coherence](../papers/2001.09190.md),
[chip-wide cosmic-ray error bursts](../papers/2104.05219.md) and
[detector-coincident correlated errors](../papers/2402.03208.md).

## Falsifiers of this note

- A retained instability reproduces with a sidereal period across a campaign
  long enough to separate it from the solar day.
- A Belenos response changes sign when the chip's orientation reverses.
- A Heron correlated-error burst coincides with an independent particle
  detector.

Each would show a coupling far larger than the scales above, so each would
first demand a non-relativistic explanation, such as thermal, electrical or
detector effects.
