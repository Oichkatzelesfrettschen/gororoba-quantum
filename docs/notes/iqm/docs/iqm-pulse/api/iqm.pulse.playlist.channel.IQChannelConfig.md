> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.IQChannelConfig.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.IQChannelConfig.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 18869444946273ff50f34bde207593036ab16cb7507a4308579a28acbaa17882.

# IQChannelConfig

Module: [`iqm.pulse.playlist.channel`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html#module-iqm.pulse.playlist.channel "iqm.pulse.playlist.channel")

*class* iqm.pulse.playlist.channel.IQChannelConfig(*sample_rate*, *frequency*)  
Bases: [`RealChannelConfig`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.RealChannelConfig.html#iqm.pulse.playlist.channel.RealChannelConfig "iqm.pulse.playlist.channel.RealChannelConfig")

Requested configuration of an IQ channel.

Attributes

|  |  |
|----|----|
| [`frequency`](#iqm.pulse.playlist.channel.IQChannelConfig.frequency "iqm.pulse.playlist.channel.IQChannelConfig.frequency") | upconversion frequency for the IQ pulses (in Hz) |
| `sample_rate` | sample rate of the instrument responsible for the channel (in Hz) |

Methods

Parameters:  
- **sample_rate** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

frequency*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
upconversion frequency for the IQ pulses (in Hz)

Inheritance

![Inheritance diagram of iqm.pulse.playlist.channel.IQChannelConfig](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-01b87aca71a98fa0c601cd345a32b7846c10a87d.png)
