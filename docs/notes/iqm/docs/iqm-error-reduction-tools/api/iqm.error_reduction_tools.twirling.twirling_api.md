> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 39b80d02cd802af5f614a807aeaf54382b975013f8914b6183733e902dd44579.

# iqm.error_reduction_tools.twirling.twirling_api

Circuit twirling API for readout error mitigation.

Provides [`TwirlingConfiguration`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration") for controlling twirling behaviour and [`CircuitTwirler`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler") for the full twirl → submit → retrieve lifecycle.

Typical usage:

```
from iqm.error_reduction_tools.twirling.twirling_api import CircuitTwirler, TwirlingConfiguration

config = TwirlingConfiguration(readout_twirl_strategy="LOCAL", seed=42)
twirler = CircuitTwirler(client, config=config)
twirler.twirl(circuits).submit(shots=20_000)
counts = twirler.retrieve_counts()
```

Classes

|  |  |
|----|----|
| [`CircuitTwirler`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler")(\[client, config, ...\]) | Manages the twirl → submit → retrieve lifecycle for readout-twirled circuits. |
| [`TwirlingConfiguration`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration")(\[...\]) | Configuration for circuit twirling. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.twirling.twirling_api](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-34c0ead827d5080efe3fe4807a707ce9c25d149f.png)
