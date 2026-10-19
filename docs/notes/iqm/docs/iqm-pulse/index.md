> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/index.html](https://docs.iqm.tech/4.7/iqm-pulse/index.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 146ad5e72eae34b6218008a0c8d86ccafed055e491c754fac8159e305c86a4e5.

# IQM Pulse

Version:  
15.0.0

Date:  
2026-10-06

IQM Pulse provides an abstraction that transforms high-level quantum circuit operations to a unified set of lower-level instructions for [IQM](https://iqm.tech/) quantum computers.

A quantum circuit is an abstract mathematical construct which conveniently hides all implementation details such as the timing of microwave pulses, waveform shapes, sampling rates, signal capture, and so on. But in order to execute a circuit you need to convert it into a schedule of hardware instructions which involve all of the above.

IQM Pulse provides

- a framework for defining abstract quantum gates/operations, as well as their concrete implementations in terms of hardware instructions

- machinery to easily construct circuit-level gate sequences, and compile them into instruction schedules.

- a set of ready-made gates with implementations.

IQM Pulse is not a standalone tool, but is used in IQM’s client libraries, IQM Client and EXA. To use them effectively, you are encouraged to familiarize yourself with IQM Pulse, especially the most common concepts.

## Contents

- [iqm-pulse](https://docs.iqm.tech/4.7/iqm-pulse/readme.html)
  - [Installation](https://docs.iqm.tech/4.7/iqm-pulse/readme.html#installation)
- [Concepts and classes](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html)
  - [Quick reference](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#quick-reference)
  - [Instructions](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#instructions)
  - [Schedules](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#schedules)
  - [TimeBoxes](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#timeboxes)
  - [QuantumOps](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#quantumops)
  - [GateImplementations](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#gateimplementations)
  - [Playlists](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html#playlists)
- [Using ScheduleBuilder](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html)
  - [Creating TimeBoxes](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html#creating-timeboxes)
  - [Composing TimeBoxes](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html#composing-timeboxes)
  - [Resolving TimeBoxes into a Schedule](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html#resolving-timeboxes-into-a-schedule)
  - [Miscellaneous features](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html#miscellaneous-features)
  - [Common pitfalls](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html#common-pitfalls)
- [Custom gate implementations](https://docs.iqm.tech/4.7/iqm-pulse/custom_gates.html)
  - [QuantumOp](https://docs.iqm.tech/4.7/iqm-pulse/custom_gates.html#quantumop)
  - [Custom gate implementations](https://docs.iqm.tech/4.7/iqm-pulse/custom_gates.html#id1)
  - [Registering gates and implementations](https://docs.iqm.tech/4.7/iqm-pulse/custom_gates.html#registering-gates-and-implementations)
- [Pulse timing](https://docs.iqm.tech/4.7/iqm-pulse/pulse_timing.html)
  - [Measure and ReadoutTrigger](https://docs.iqm.tech/4.7/iqm-pulse/pulse_timing.html#measure-and-readouttrigger)
  - [Fast feedback timing](https://docs.iqm.tech/4.7/iqm-pulse/pulse_timing.html#fast-feedback-timing)
- [API reference](https://docs.iqm.tech/4.7/iqm-pulse/API.html)
  - [pulse](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.html)

- [References](https://docs.iqm.tech/4.7/iqm-pulse/references.html)
- [Changelog](https://docs.iqm.tech/4.7/iqm-pulse/changelog.html)
- [License](https://docs.iqm.tech/4.7/iqm-pulse/license.html)

## Indices and tables

- [Index](https://docs.iqm.tech/4.7/iqm-pulse/genindex.html)

- [Module Index](https://docs.iqm.tech/4.7/iqm-pulse/py-modindex.html)

- [Search Page](https://docs.iqm.tech/4.7/iqm-pulse/search.html)
