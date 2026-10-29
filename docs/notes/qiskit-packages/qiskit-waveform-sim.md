# qiskit-waveform-sim

qiskit-waveform-sim 0.3.0 (`python-qiskit-waveform-sim`) draws a scheduled
circuit's control waveforms from a Qiskit 2.x `Target`.
`TargetWaveformSimulator(target).compile(scheduled_circuit)` takes each
instruction's duration from the Target and places an envelope on a drive
channel. `get_snippet(channel)` returns the sampled complex waveform at
`dt`. Pulse sheets, IQ oscilloscope plots and an OpenQASM 3 export with
envelope annotations render the result. The circuit must be scheduled
first, with `generate_preset_pass_manager(..., scheduling_method="alap")`,
or given explicit `start_times` when it contains a `BoxOp`.

**Only the timing is calibrated.** On the FakeFez target, an X on qubit 0
compiles to 6 samples at dt = 4 ns, which equals the Target's 24 ns X
duration. The envelope's shape (DRAG), amplitude 0.9, beta 0.08 and sigma
1.5 dt come from `PulseDefaults` placeholders, not calibration data. IBM
removed pulse-level control on 3 February 2025, and Heron r2 publishes no
pulse shapes. The output therefore illustrates schedule timing and channel
overlap. It is no model of the delivered pulse, and no physical claim rests
on its amplitudes.

## Connections

- Its timing authority matches the repository's: the live Target, or a
  retained snapshot in docs/evidence/heron_platform/targets.json, at dt
  4 ns ([ibm_heron_platform.md](../ibm_heron_platform.md)).
- It complements the scheduling and idle analysis of the idle-penalty work.
  It visualizes the ALAP schedule that those analyses charge for idle time.
- qiskit-dynamics, which would simulate pulses, requires qiskit<=1.3 and
  stays uninstalled ([qiskit-ecosystem.md](../qiskit-ecosystem.md)).
