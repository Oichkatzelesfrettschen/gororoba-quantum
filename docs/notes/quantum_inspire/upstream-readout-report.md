# Upstream routes and unsent readout report

The [failed Tuna qualification](../../evidence/tuna-projector-geometry/tuna-qualification.md)
needs provider-side acquisition evidence, while the retained QX result-width behavior needs
an explicit simulator result contract. The two observations concern different boundaries.
The reports below are prepared for review and remain unsent.

## Verified contact routes

The [public-source receipt](../../evidence/tuna-projector-geometry/readout-upstream-public-sources.json)
records HTTP statuses, source digests and retrieval times on 2026-10-27. The official
[FAQ](https://www.quantum-inspire.com/faq/) directs feedback, questions and bugs to
**support@quantum-inspire.com**, requesting a description, reproduction, expected/actual
behavior and code. That support address is the first route for served Tuna configuration,
account-specific completed-job traces, or a platform/documentation discrepancy spanning
components. The public Tuna dashboard also invites feedback through Slack, but the inspected
pages supply no verified public invitation URL or named channel.

| Boundary | Verified upstream route | Appropriate report |
|---|---|---|
| QX result serialization and local qxelarator behavior | [QX simulator issues](https://github.com/QuTech-Delft/qx-simulator/issues) | Minimal local reproducer, exact version and result fields; distinguish execution of classical variables from returned result representation |
| OpenSquirrel measurement map/export | [OpenSquirrel issues](https://github.com/QuTech-Delft/OpenSquirrel/issues), [discussions](https://github.com/QuTech-Delft/OpenSquirrel/discussions) | Reproducer whose local exporter output is wrong, with source/configuration identity |
| Quantify Scheduler pulse/acquisition compilation | [Quantify Scheduler issues](https://gitlab.com/quantify-os/quantify-scheduler/-/issues) | A local schedule/threshold/integration reproducer or a Quantum Inspire deployment attribution is required before treating the anomaly as a library issue |
| Language specification | [cQASM specification issues](https://github.com/QuTech-Delft/cQASM-spec/issues) | Ambiguous language meaning; provider transport serialization is a separate contract |
| SDK transport | [Quantum Inspire SDK issues](https://github.com/QuTech-Delft/quantuminspire/issues) | SDK-specific data conversion or transport defect reproduced independently of hardware response |
| Qiskit adapter | [Qiskit provider issues](https://github.com/QuTech-Delft/qiskit-quantuminspire/issues) | Qiskit-to-cQASM or result conversion defect; the retained qualification used direct cQASM and does not implicate this adapter |
| Tuna utility notebooks | [QuantumInspireUtilities issues](https://github.com/DiCarloLab-Delft/QuantumInspireUtilities/issues) | Utility/notebook defects, rather than unlocalized hardware or service faults |

The Quantify route is corroborated by the OpenSquirrel maintainer link to
[Quantify Scheduler issue 488](https://gitlab.com/quantify-os/quantify-scheduler/-/issues/488),
whose public page returned HTTP 200. The [Quantify project site](https://quantify-os.org/)
links its GitLab organization. The served Tuna stack remains unidentified; an unexplained
hardware response alone does not warrant attributing a defect to Quantify Scheduler.

The provider's [release page](https://www.quantum-inspire.com/release-notes/) directly links
the QuTech-Delft software repositories. The QX marketing page still links the older QE-Lab
organization; prefer the provider's release-page routes for triage. GitHub metadata confirms
the listed repositories have issues enabled and are unarchived. A request for a standalone
`QuTech-Delft/qxelarator` repository returned 404; the QX project is the verified route.

## Relevant issue history

The [issue-context receipt](../../evidence/tuna-projector-geometry/readout-upstream-issue-context.json)
records historical discussions; a closed issue does not establish the deployed service version.

- [QX #63](https://github.com/QuTech-Delft/qx-simulator/issues/63), closed June 2024,
  concerns independent classical-bit and qubit registers. The closing comment says cQASM 3.0
  treats bits and qubits independently. [#149](https://github.com/QuTech-Delft/qx-simulator/issues/149)
  and [#154](https://github.com/QuTech-Delft/qx-simulator/issues/154) concern parsing and managing
  those variables and intermediate measurements. Their completion does not establish that
  the returned histogram exposes the final classical register.
- [QX #118](https://github.com/QuTech-Delft/qx-simulator/issues/118) discusses measurement-register
  versus state output and simulator/hardware JSON compatibility. It is historical context,
  not the current output specification.
- [OpenSquirrel #270](https://github.com/QuTech-Delft/OpenSquirrel/issues/270), closed October 2024,
  reports an exporter that used the qubit number as the acquisition index rather than starting
  at zero and incrementing per qubit. The inspected local 0.9.1 exporter already has per-qubit
  counters. The historical defect motivates requesting the served exporter and reconstruction
  versions; it does not show that Tuna still has that defect.
- [OpenSquirrel #506](https://github.com/QuTech-Delft/OpenSquirrel/issues/506) records an ALAP
  timing-constraint failure and a resolution in 0.8.0. It demonstrates why an exported schedule
  and the compiled analog schedule are different evidence surfaces, without attributing the
  present successful-but-anomalous acquisition to that old failure.

## Unsent support report: Tuna repeated-readout response

**Subject:** Tuna-17 early/terminal binary response differs; request acquisition-map and timing provenance

A three-circuit Tuna-17 qualification completed on 2026-10-27. Each circuit requested
4096 shots and returned 4096 width-20 binary strings. The controls nominally prepare all
17 qubits in zero or one, measure q4/q11/q6 into bits17/18/19, then measure all qubits into
bits0–16 after a barrier, with zero explicit settling wait. The smallest retained source
that exhibits the prepared-zero anomaly follows, with whitespace minimized for presentation;
the retained file and its digest remain the byte-level source authority:

```text
version 3.0
qubit[17] q
bit[20] b
init q
barrier q
b[17] = measure q[4]
b[18] = measure q[11]
b[19] = measure q[6]
barrier q
b[0:16] = measure q
```

The prepared-one control inserts X on each of q0 through q16 before the first barrier.
With bit0 decoded from the right, early q11 reports one in 4039/4096 nominal-zero shots
and 1510/4096 nominal-one shots. Terminal q11 reports one in 113/4096 and 3795/4096,
respectively. The early contrast is -2529/4096 while the terminal contrast is 3682/4096.
Early/final q11 disagreement in the nominal-zero control is 3948/4096. These are binary
response frequencies; they are not calibrated physical-state populations.

The provider's stored file bytes match the submitted source digests. Local OpenSquirrel
0.9.1 preserves the declared destinations and maps q11 acquisitions to bits18 then11.
The stored file exposes `compile_stage=none` and empty `compile_properties`, leaving the
served pulse program, integration windows and reconstruction provenance unavailable.
The qualification screen refused further scientific interpretation. A fixed permutation
and polarity of the three early bits does not repair the complete screen.

Please clarify whether this repeated-measurement pattern and compact classical register
are supported, and provide, where retained:

1. Served compiler/exporter/control-stack versions and configuration identity.
2. Per-qubit acquisition-channel/index to classical-bit reconstruction map, including shot order.
3. Scheduled pulse and acquisition-window starts/ends, integration kernel, discriminator
   rotation/threshold and calibration timestamp for the early and terminal measurements.
4. Whether changing only classical destinations can change scheduling, acquisition settings
   or reconstruction, and whether the 300 ns dashboard notice describes pulse duration,
   acquisition duration, or another interval.
5. Reset/repetition timing and any retained analog IQ or multilevel response needed to
   distinguish assignment, overlap, carryover and physical transitions.

The existing diagnostic evidence and source hashes are linked in the
[readout diagnosis](../../evidence/tuna-projector-geometry/readout-cause-diagnosis.md).
For a private support exchange, completed job identifiers are 1616329, 1616330 and 1616331.
A public software issue can omit those identifiers and the raw account record. The report
makes no claim that a particular software defect or resonator mechanism caused the response.

## Unsent QX contract report

**Subject:** Clarify classical-register versus per-qubit measurement-register output

The [retained QX semantics investigation](qx-runs.md) reports that qxelarator 0.10.0 and
completed QX jobs return a width equal to declared qubits and retain each qubit's last
measurement, while the destination classical bit is absent from the result representation.
The following deterministic source distinguishes those representations:

```text
version 3.0
qubit[2] q
bit[4] b
init q
X q[0]
b[2] = measure q[0]
X q[0]
b[0:1] = measure q
```

The language-level final classical register is `0100`; the retained local behavior returns
`00`, the final per-qubit measurement register. This source is a reproduction request based
on retained evidence, not a fresh execution in the contact-research step. The official
[hello-world page](https://www.quantum-inspire.com/kbase/hello-quantum-world/) describes the
histogram as the classical binary register, while the
[Tuna page](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/) explicitly
states that returned shots follow classical-bit order with user-controlled destinations.

Please identify the current QX version and output contract: is the classical register
available through another result field or API, is the per-qubit register deliberate, and
which documentation should state the backend distinction? The independent-register work
in issues #63/#149/#154 appears to concern language execution; result serialization may be
a separate boundary. A QX terminal distribution check cannot qualify preservation of Tuna's
intermediate classical records, and a noiseless simulator cannot reproduce the analog
Tuna anomaly without an independently justified model.

The Ry emulator is a third backend, not an alternate QX configuration. Its retained
[parser/result limitations](ry-emulator.md) and live backend flags require their own contract;
those observations should remain a separate issue if clarification is requested.

## Read-only readiness observations

The [backend and account observation](../../evidence/tuna-projector-geometry/readout-destination-readiness.json),
[full usage observation](../../evidence/tuna-projector-geometry/readout-destination-usage-observation.json),
[public routes](../../evidence/tuna-projector-geometry/readout-upstream-public-sources.json),
[full normalized terms](../../evidence/tuna-projector-geometry/readout-destination-terms-text.json), and
[calibration availability](../../evidence/tuna-projector-geometry/readout-destination-monitoring.json)
are timestamped reads. The account ledger completed at 19:07:57 UTC with 426 jobs,
7,788,544 completed shots, 4963.250562 reported execution seconds and zero transaction rows.
Tuna was enabled/executing at 19:07:59 UTC, with an empty account queue and zero remaining
account pause; the configured pause was 30 seconds. Its API limits remained 131072 shots
and 300 seconds per job. QX was enabled/idle; the Ry emulator was enabled/idle at 19:09:11 UTC
and retained its API `is_hardware=true` flag. These backend flags describe routing, not
physical equivalence between the emulator and a QPU. The account page still describes free hardware/emulator access;
the terms limit free use to the stated noncommercial conditions and the FAQ limits hardware
queue occupancy to three jobs. The repository's stricter single queued hardware batch and
account-wide pause remain binding.

The complete FAQ, account and terms text matched across two fresh fetches per page at
19:11:22–23 UTC after the runner's deterministic HTML-text normalization. Runtime admission
compares that visible policy text rather than unstable page-wrapper bytes. The receipt also
retains raw HTML digests as retrieval evidence.

These snapshots do not qualify a successor case. Each single-job submission in a sequential
case must bind the reviewed manifest, source, compiler receipt, analyzer and written decision;
refresh structural availability, account-wide pause, queue and applicable terms immediately
before guarded submission. A public calibration endpoint timeout supplies no fresh T1,
assignment fidelity or QNDness value. A provider's idle state does not repair the failed
measurement path.
