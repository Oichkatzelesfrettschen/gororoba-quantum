> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.OperationClass.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.OperationClass.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a452ba48d07386fa7f612ac2f3f5e323b0c6e7e498fba09edaaa446d289ed264.

# iqm.pulse.validation.OperationClass

iqm.pulse.validation.OperationClass*: [TypeAlias](https://docs.python.org/3.11/library/typing.html#typing.TypeAlias "(in Python v3.11)")* *= type\[iqm.models.playlist.instructions.Wait\] \| type\[iqm.models.playlist.instructions.IQPulse\] \| type\[iqm.models.playlist.instructions.RealPulse\] \| type\[iqm.models.playlist.instructions.VirtualRZ\] \| type\[iqm.models.playlist.instructions.ConditionalInstruction\] \| type\[iqm.models.playlist.instructions.MultiplexedIQPulse\] \| type\[iqm.models.playlist.instructions.ReadoutTrigger\]*  
Union of operation classes station-control actually uses, across AWG and readout controllers.

Local alias because iqm.models.playlist.instructions.Operation is a constrained TypeVar meant only to parametrize Instruction\[Operation\], not a general-purpose union type for typing sets/tuples of classes.
