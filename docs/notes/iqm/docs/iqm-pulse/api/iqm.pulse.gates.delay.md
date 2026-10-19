> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 58168395cc9f078fa054f68dffbfd3123bc8f328f36e3a4bda2c773d60dcb66e.

# delay

Full path: iqm.pulse.gates.delay

Force a delay between instructions on the control channels of specific locus components.

Ideally the delay corresponds to an identity gate. In reality it of course allows decoherence to act on the quantum state for some time.

Module Attributes

|  |  |
|----|----|
| [`DELAY_MAX_DURATION_SECONDS`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.DELAY_MAX_DURATION_SECONDS.html#iqm.pulse.gates.delay.DELAY_MAX_DURATION_SECONDS "iqm.pulse.gates.delay.DELAY_MAX_DURATION_SECONDS") | Maximum duration for individual Delay operations, in seconds. |

Classes

|  |  |
|----|----|
| [`Delay`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.Delay.html#iqm.pulse.gates.delay.Delay "iqm.pulse.gates.delay.Delay") | Applies a delay on the control channels of its locus components. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.delay](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-30d2cc29715c0bba4d7202a460ad6d69ef960039.png)
