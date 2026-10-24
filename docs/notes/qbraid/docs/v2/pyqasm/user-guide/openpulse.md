> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/openpulse.md](https://docs.qbraid.com/v2/pyqasm/user-guide/openpulse.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 5ac9375228fa9fdc99c2ab8a2bf2cf11aa7544febca7a6eb79ae081d0a618078.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# OpenPulse

> A low-level pulse programming extension of OpenQASM 3, giving developers direct control over the physical signals that manipulate qubits.

## Overview

**OpenPulse** extends **OpenQASM3** beyond the gate model by introducing constructs for **ports**, **frames**, and **waveforms** that describe the actual control signals sent to quantum hardware. This allows programmers to implement custom calibrated gates, adjust frequencies and phases dynamically, and align timing at the hardware level. With **OpenPulse**, quantum programs can bridge the gap between high-level circuits and the physical pulses that drive qubit operations.

## PyQASM 🤝 OpenPulse

**PyQASM** now understands and validates **OpenPulse** constructs embedded in `OpenQASM3` programs. This includes parsing `cal` blocks and `defcal` definitions and validating pulse-level statements.
While most existing tools focus on gate-level `OpenQASM`, few provide strong support for pulse-level semantics and most of them lack comprehensive semantic analysis -- such as validating scope rules, deterministic durations in defcal, and hardware-level constraints

**PyQASM** aims to fill this gap by:

- Providing a unified parser and validator for both `OpenQASM3` and `OpenPulse`.

- Enforcing semantic correctness of pulse operations, not just syntax.

- Allowing users to configure `backend-specific` rules (duration tracking, frame limits, etc.).

- Building towards a complete analysis and compilation toolkit for pulse-level programs, bridging high-level circuits with low-level control.

This makes **PyQASM** a foundation for researchers and hardware providers who need **validation** and **compilation** of **OpenPulse** programs.

## Core Constructs

The OpenPulse grammar—activated by `defcal grammar "openpulse";` — adds these core constructs to OpenQASM3.

- [**Ports**](https://openqasm.com/versions/3.0/language/openpulse.html#ports) (`port`): Abstract I/O channels representing hardware control lines.

  - Real hardware often restricts the number of active frames per physical port. pyqasm introduces a `frame_limit_per_port` option that users can set when loading a program.

  <CodeGroup>

  ```python QASM-Code
  import pyqasm

  qasm = """
  OPENQASM 3.0;
  defcalgrammar "openpulse";
  cal {
       port d0;
       frame fr1 = newframe(d0, 100.0, 5.0);
       frame fr2 = newframe(d0, 100.0, 5.0);
  }
  """
  module = pyqasm.loads(qasm, frame_limit_per_port = 1)
  module.unroll()
  print(pyqasm.dumps(module))
  ```

  ```qasm output
  ERROR:pyqasm: Error at line 4, column 16 in QASM file

  > > > > > > newframe(d0, 100.0, 5.0)

  pyqasm.exceptions.ValidationError: Port 'd0' has exceeded the 'frame-limit' of '1'

  ```

  </CodeGroup>

- [**Frames**](https://openqasm.com/versions/3.0/language/openpulse.html#frames) (`frame`): Stateful carriers with port, timing, frequency, and phase.

  - Users can configure whether frames are allowed in `defcal` blocks via the `frame_in_defcal` option when loading a program.

  <CodeGroup>

  ```python QASM-Code
  import pyqasm

  qasm = """
  OPENQASM 3.0;
  defcalgrammar "openpulse";
  cal {
       port d0;
       frame fr1 = newframe(d0, 100.0, 5.0);
  }
  defcal gate $0{
       frame fr2 = newframe(d0, 100.0, 5.0);
  }
  """

  module = pyqasm.loads(qasm, frame_in_defcal = False)
  module.unroll()
  print(pyqasm.dumps(module))
  ```

  ```qasm output
  ERROR:pyqasm: Error at line 2, column 16 in QASM file

  > > > > > > newframe(d0, 100.0, 5.0)

  pyqasm.exceptions.ValidationError: 'Frame' initialization in 'defcal' block is not allowed

  ```

  </CodeGroup>

- pyqasm also supports the full set of [**frame manipulators**](https://openqasm.com/versions/3.0/language/openpulse.html#phase-tracking) defined in the OpenPulse grammar
  - `set_frequency()` / `shift_frequency()` / `shift_phase()` / `get_frequency()` / `get_phase()`.

- [**Waveforms**](https://openqasm.com/versions/3.0/language/openpulse.html#waveforms) (`waveform`): Envelopes modulating signals on ports.

  - pyqasm supports all `waveform` types defined in the OpenPulse specification -- `gaussian`, `sech`, `gaussian_square`, `drag`, `constant`, `sine`, `mix`, `sum`, `phase_shift`, `scale`.
  - validates all declarations conform to the OpenPulse grammar, including parameter correctness and waveform compatibility.

- [**Capture**](https://openqasm.com/versions/3.0/language/openpulse.html#capture-instruction) (`capture`): Measurement/capture operations.

  - pyqasm also supports the `capture` operations defined in the OpenPulse grammar -- `capture_v1()`, `capture_v2()`, `capture_v3()`, `capture_v4()`.

- **Operations** within `cal` / `defcal`:

  - [**play()**](https://openqasm.com/versions/3.0/language/openpulse.html#play-instruction) — apply a waveform via a frame.

    - By default, `play` is intended for use inside `defcal` blocks. pyqasm introduces a configurable option, `play_in_cal_block`, which allows users to enable or restrict the use of `play` instructions inside `cal` blocks as well.

    <CodeGroup>

    ```python QASM-Code
    import pyqasm

    qasm = """
    OPENQASM 3.0;
    defcalgrammar "openpulse";
    cal {
       port d0;
       frame fr1 = newframe(d0, 100.0, 5.0);
       waveform wf = constant(1.0+2.0im, 100.0ns);
       play(fr1, wf);
    }
    """
    module = pyqasm.loads(qasm, play_in_cal_block = False)
    module.unroll()
    print(pyqasm.dumps(module))
    ```

    ```qasm output
    ERROR:pyqasm: Error at line 5, column 11 in QASM file

    > > > > > > play(fr1, wf)

    pyqasm.exceptions.ValidationError: 'Play' function is only allowed in 'defcal' block

    ```

    </CodeGroup>

  - [**delay()**](https://openqasm.com/versions/3.0/language/openpulse.html#delay) — Advance the `time-cursor` of a frame by a given `duration`.

  - [**barrier()**](https://openqasm.com/versions/3.0/language/openpulse.html#barrier) — `synchronize` the time-cursor of multiple frames to the same point in time.

## Capabilities

- [**Duration Tracking**](https://openqasm.com/versions/3.0/language/openpulse.html#timing)

  - Each frame carries an internal **time-cursor** that advances as operations (`play`, `delay`, `capture`) are applied.
  - pyqasm performs semantic tracking of `durations`, ensuring that timing across frames remains consistent throughout the program.
  - This enables correct validation of `defcal` blocks, which must have deterministic total durations across all execution paths.

- **PyQASM** Supports [**Frames-Collisions**](https://openqasm.com/versions/3.0/language/openpulse.html#collisions) validation in `defcal` blocks.
- **PyQASM** also unrolls `cal` blocks, which is useful for debugging and visualization. Since, `defcal` are acted as functions, we are not unrolling them.

<Tab title="NOTE:">
  - **Currently, pyqasm does not support `extern` declarations in OpenPulse
  blocks**.
</Tab>

<Tab>
  For more details, please refer to the [OpenPulse
  specification](https://openqasm.com/versions/3.0/language/openpulse.html).
</Tab>

## Examples

<Tabs>
<Tab title="Qubit Spectroscopy">
<CodeGroup>

```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
defcalgrammar "openpulse";

complex[float[32]] amp = 1.0 + 2.0im;
cal {
   port d0;
   frame driveframe = newframe(d0, 5.0e9, 0.0);
   waveform wf = gaussian(amp, 16ns, 4ns);
}

const float frequency_start = 4.5e9;
const float frequency_step = 1e6;
const int frequency_num_steps = 3;

defcal saturation_pulse $0 {
   play(driveframe, constant(amp, 100e-6s));
}

cal {
   set_frequency(driveframe, frequency_start);
}

for int i in [1:frequency_num_steps] {
   cal {
       shift_frequency(driveframe, frequency_step);
   }
   saturation_pulse $0;
}
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))
```

```qasm output
OPENQASM 3.0;
qubit[1] __PYQASM_QUBITS__;
defcalgrammar "openpulse";
cal {
 port d0;
 frame driveframe = newframe(d0, 5000000000.0, 0.0, 0ns);
 waveform wf = gaussian(1.0 + 2.0im, 16.0ns, 4.0ns);
}
defcal saturation_pulse() $0 {
 play(driveframe, constant(amp, 0.0001s));
}
cal {
 set_frequency(driveframe, 4500000000.0);
}
cal {
 shift_frequency(driveframe, 4501000000.0);
}
saturation_pulse __PYQASM_QUBITS__[0];
cal {
 shift_frequency(driveframe, 4502000000.0);
}
saturation_pulse __PYQASM_QUBITS__[0];
cal {
 shift_frequency(driveframe, 4503000000.0);
}
saturation_pulse __PYQASM_QUBITS__[0];
```

</CodeGroup>
</Tab>
<Tab title="Rabi Time Spectroscopy">
<CodeGroup>
```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
defcalgrammar "openpulse";
qubit[4] q;
const duration pulse_length_start = 20ns;
const duration pulse_length_step = 1ns;
const int pulse_length_num_steps = 3;
cal {
   port d0;
   frame driveframe = newframe(d0, 5.0e9, 0.0);
}
for int i in [1:pulse_length_num_steps] {
    duration pulse_length = pulse_length_start + (i-1)*pulse_length_step;
    duration sigma = pulse_length / 4;
    // since we are manipulating pulse lengths it is easier to define and play the waveform in a `cal` block
    cal {
        waveform wf = gaussian(1.0 + 2.0im, pulse_length, sigma);
        // assume frame can be linked from a vendor supplied `cal` block
        play(driveframe, wf);
    }
    measure $0;
}
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm output
OPENQASM 3.0;
qubit[4] __PYQASM_QUBITS__;
defcalgrammar "openpulse";
cal {
 port d0;
 frame driveframe = newframe(d0, 5000000000.0, 0.0, 0ns);
}
cal {
 waveform wf = gaussian(1.0 + 2.0im, 20.0ns, 5.0ns);
 play(driveframe, wf);
}
measure __PYQASM_QUBITS__[0];
cal {
 waveform wf = gaussian(1.0 + 2.0im, 21.0ns, 5.25ns);
 play(driveframe, wf);
}
measure __PYQASM_QUBITS__[0];
cal {
 waveform wf = gaussian(1.0 + 2.0im, 22.0ns, 5.5ns);
 play(driveframe, wf);
}
measure __PYQASM_QUBITS__[0];
````

</CodeGroup>
</Tab>

<Tab title="Neutral Atom Gate">
<CodeGroup>
```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
defcalgrammar "openpulse";

// Raman transition detuning delta from the 5S1/2 to 5P1/2 transition
const float delta = 100e6;

// Hyperfine qubit frequency
const float qubit_freq = 6.0e9;

// Positional frequencies for the AODS to target the specific qubit
const float q1_pos_freq = 5.0e9;
const float q2_pos_freq = 5.0e9;
const float q3_pos_freq = 5.0e9;

// Calibrated amplitudes and durations for the Raman pulses supplied via the AOD envelopes
const complex[float[32]] q1*π_half_amp = 1.0 + 2.0im;
const complex[float[32]] q2*π*half_amp = 1.0 + 2.0im;
const complex[float[32]] q3*π_half_amp = 1.0 + 2.0im;
const duration pi_half_time = 10.0ns;

// Time-proportional phase increment
const float tppi_1 = 1.0;
const float tppi_2 = 1.0;
const float tppi_3 = 1.0;

cal {
port eom_a_port;
port eom_b_port;
port aod_port;

    // Define the Raman frames, which are detuned by an amount delta from the  5S1/2 to 5P1/2 transition
    // and offset from each other by the qubit_freq
    frame raman_a_frame = newframe(eom_a_port, delta, 0.0);
    frame raman_b_frame = newframe(eom_b_port, delta-qubit_freq, 0.0);
    const complex[float[32]] raman_a_amp = 1.0 + 2.0im;
    const complex[float[32]] raman_b_amp = 1.0 + 2.0im;

    // Three frames to phase track each qubit's rotating frame of reference at it's frequency
    frame q1_frame = newframe(aod_port, qubit_freq, 0.0);
    frame q2_frame = newframe(aod_port, qubit_freq, 0.0);
    frame q3_frame = newframe(aod_port, qubit_freq, 0.0);

    // Generic gaussian envelope
    waveform pi_half_sig = gaussian(1.0 + 2.0im, pi_half_time, 100ns);

    // Waveforms ultimately supplied to the AODs. We mix our general Gaussian pulse with a sine wave to
    // put a sideband on the outgoing pulse. This helps us target the qubit position while maintainig the
    // desired Rabi rate.
    waveform q1_pi_half_sig = mix(pi_half_sig, sine(q1_π_half_amp, pi_half_time, q1_pos_freq-qubit_freq, 0.0));
    waveform q2_pi_half_sig = mix(pi_half_sig, sine(q2_π_half_amp, pi_half_time, q2_pos_freq-qubit_freq, 0.0));
    waveform q3_pi_half_sig = mix(pi_half_sig, sine(q3_π_half_amp, pi_half_time, q3_pos_freq-qubit_freq, 0.0));

}
// π/2 pulses on all three qubits
defcal rx(angle theta) $1, $2, $3 {
// Simultaneous π/2 pulses
play(raman_a_frame, constant(raman_a_amp, pi_half_time));
play(raman_b_frame, constant(raman_b_amp, pi_half_time));
play(q1_frame, q1_pi_half_sig);
play(q2_frame, q2_pi_half_sig);
play(q3_frame, q3_pi_half_sig);
}
// π/2 pulse on only qubit $2
defcal rx(angle theta) $2 {
play(raman_a_frame, constant(raman_a_amp, pi_half_time));
play(raman_b_frame, constant(raman_b_amp, pi_half_time));
play(q2_frame, q2_pi_half_sig);
}
// Ramsey sequence on qubit 1 and 3, Hahn echo on qubit 2
for duration tau_val in [1us:1us:2us] {

    // First π/2 pulse
    rx(pi/2) $1, $2, $3;
    // First half of evolution time
    cal {
        delay[tau_val/2] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
    }
    // Hahn echo π pulse composed of two π/2 pulses
    for int ct in [0:1]{
        rx(π/2) $2;
    }
    cal {
        // Align all frames
        barrier raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;

        // Second half of evolution time
        delay[tau_val/2] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;

        // Time-proportional phase increment signals different amount
        shift_phase(q1_frame, tppi_1 * tau_val);
        shift_phase(q2_frame, tppi_2 * tau_val);
        shift_phase(q3_frame, tppi_3 * tau_val);
    }

    // Second π/2 pulse
    rx(π/2) $1, $2, $3;

}
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm output
OPENQASM 3.0;
qubit[4] __PYQASM_QUBITS__;
defcalgrammar "openpulse";
cal {
 port eom_a_port;
 port eom_b_port;
 port aod_port;
 frame raman_a_frame = newframe(eom_a_port, 100000000.0, 0.0, 0ns);
 frame raman_b_frame = newframe(eom_b_port, -5900000000.0, 0.0, 0ns);
 const complex[float[32]] raman_a_amp = 1.0 + 2.0im;
 const complex[float[32]] raman_b_amp = 1.0 + 2.0im;
 frame q1_frame = newframe(aod_port, 6000000000.0, 0.0, 0ns);
 frame q2_frame = newframe(aod_port, 6000000000.0, 0.0, 0ns);
 frame q3_frame = newframe(aod_port, 6000000000.0, 0.0, 0ns);
 waveform pi_half_sig = gaussian(1.0 + 2.0im, 10.0ns, 100.0ns);
 waveform q1_pi_half_sig = mix(pi_half_sig, sine(1.0 + 2.0im, 10.0ns, -1000000000.0, 0.0));
 waveform q2_pi_half_sig = mix(pi_half_sig, sine(1.0 + 2.0im, 10.0ns, -1000000000.0, 0.0));
 waveform q3_pi_half_sig = mix(pi_half_sig, sine(1.0 + 2.0im, 10.0ns, -1000000000.0, 0.0));
}
defcal rx(angle theta) $1, $2, $3 {
 play(raman_a_frame, constant(raman_a_amp, pi_half_time));
 play(raman_b_frame, constant(raman_b_amp, pi_half_time));
 play(q1_frame, q1_pi_half_sig);
 play(q2_frame, q2_pi_half_sig);
 play(q3_frame, q3_pi_half_sig);
}
defcal rx(angle theta) $2 {
 play(raman_a_frame, constant(raman_a_amp, pi_half_time));
 play(raman_b_frame, constant(raman_b_amp, pi_half_time));
 play(q2_frame, q2_pi_half_sig);
}
rx(1.5707963267948966) __PYQASM_QUBITS__[1], __PYQASM_QUBITS__[2], __PYQASM_QUBITS__[3];
cal {
 delay[500.0ns] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
}
rx(1.5707963267948966) __PYQASM_QUBITS__[2];
rx(1.5707963267948966) __PYQASM_QUBITS__[2];
cal {
 barrier raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
 delay[500.0ns] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
 shift_phase(q1_frame, 0.9735361584457891);
 shift_phase(q2_frame, 0.9735361584457891);
 shift_phase(q3_frame, 0.9735361584457891);
}
rx(1.5707963267948966) __PYQASM_QUBITS__[1], __PYQASM_QUBITS__[2], __PYQASM_QUBITS__[3];
rx(1.5707963267948966) __PYQASM_QUBITS__[1], __PYQASM_QUBITS__[2], __PYQASM_QUBITS__[3];
cal {
 delay[1000.0ns] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
}
rx(1.5707963267948966) __PYQASM_QUBITS__[2];
rx(1.5707963267948966) __PYQASM_QUBITS__[2];
cal {
 barrier raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
 delay[1000.0ns] raman_a_frame, raman_b_frame, q1_frame, q2_frame, q3_frame;
 shift_phase(q1_frame, 2.920608475337346);
 shift_phase(q2_frame, 2.920608475337346);
 shift_phase(q3_frame, 2.920608475337346);
}
rx(1.5707963267948966) __PYQASM_QUBITS__[1], __PYQASM_QUBITS__[2], __PYQASM_QUBITS__[3];
````

</CodeGroup>
</Tab>
<Tab title="Multiplexed Readout & Capture">
<CodeGroup>
```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
defcalgrammar "openpulse";

const duration electrical_delay = 100ns;
const float q0_ro_freq = 5.0e9;
const float q1_ro_freq = 6.0e9;

cal {
// the transmission/captures ports are the same for $0 and $1
port ro_tx;
port ro_rx;
// readout stimulus and capture frames of different frequencies
frame q0_stimulus_frame = newframe(ro_tx, q0_ro_freq, 0.0);
frame q0_capture_frame = newframe(ro_rx, q0_ro_freq, 0.0);
frame q1_stimulus_frame = newframe(ro_tx, q1_ro_freq, 0.0);
frame q1_capture_frame = newframe(ro_rx, q1_ro_freq, 0.0);

}
defcal multiplexed_readout_and_capture $0, $1 -> bit[2] {
bit[2] b;
int sairam;
waveform q0_ro_wf = constant(1.0 + 2.0im, 100ns);
waveform q1_ro_wf = constant(1.0 + 2.0im, 100ns);

    // multiplexed readout
    play(q0_stimulus_frame, q0_ro_wf);
    play(q1_stimulus_frame, q1_ro_wf);

    // simple boxcar kernel
    waveform ro_kernel = constant(1.0 + 2.0im, 100ns);
    barrier q0_stimulus_frame, q1_stimulus_frame, q0_capture_frame, q1_capture_frame;
    delay[electrical_delay] q0_capture_frame, q1_capture_frame;
    b[0] = capture_v2(q0_capture_frame, ro_kernel);
    b[1] = capture_v2(q1_capture_frame, ro_kernel);
    return b;

}

multiplexed_readout_and_capture $0, $1;
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm output
OPENQASM 3.0;
qubit[2] __PYQASM_QUBITS__;
defcalgrammar "openpulse";
cal {
 port ro_tx;
 port ro_rx;
 frame q0_stimulus_frame = newframe(ro_tx, 5000000000.0, 0.0, 0ns);
 frame q0_capture_frame = newframe(ro_rx, 5000000000.0, 0.0, 0ns);
 frame q1_stimulus_frame = newframe(ro_tx, 6000000000.0, 0.0, 0ns);
 frame q1_capture_frame = newframe(ro_rx, 6000000000.0, 0.0, 0ns);
}
defcal multiplexed_readout_and_capture() $0, $1 -> bit[2] {
 bit[2] b;
 int sairam;
 waveform q0_ro_wf = constant(1.0 + 2.0im, 100.0ns);
 waveform q1_ro_wf = constant(1.0 + 2.0im, 100.0ns);
 play(q0_stimulus_frame, q0_ro_wf);
 play(q1_stimulus_frame, q1_ro_wf);
 waveform ro_kernel = constant(1.0 + 2.0im, 100.0ns);
 barrier q0_stimulus_frame, q1_stimulus_frame, q0_capture_frame, q1_capture_frame;
 delay[electrical_delay] q0_capture_frame, q1_capture_frame;
 b[0] = capture_v2(q0_capture_frame, ro_kernel);
 b[1] = capture_v2(q1_capture_frame, ro_kernel);
 return b;
}
multiplexed_readout_and_capture __PYQASM_QUBITS__[0], __PYQASM_QUBITS__[1];
````

</CodeGroup>
</Tab>
</Tabs>
