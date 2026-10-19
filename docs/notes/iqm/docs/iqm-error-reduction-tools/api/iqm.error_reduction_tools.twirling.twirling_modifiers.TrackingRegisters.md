> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c032941ef2dd29126d391e2a7a25bb7eea93d91813b02f6895f7b45ac4965bcc.

# iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters

*class* iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters(*virtual_z=\<factory\>*, *extra_phi=\<factory\>*, *extra_pi=\<factory\>*, *sqg_number=\<factory\>*, *already_used_sqg=\<factory\>*, *rot_chars=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Container for tracking registers during circuit randomization.

Attributes

|  |  |
|----|----|
| [`virtual_z`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.virtual_z "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.virtual_z") | Track pending Z rotations per qubit. |
| [`extra_phi`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.extra_phi "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.extra_phi") | Track phase values for π rotations. |
| [`extra_pi`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.extra_pi "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.extra_pi") | Track count of π rotations per qubit. |
| [`sqg_number`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.sqg_number "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.sqg_number") | Number of single-qubit gates per qubit. |
| [`already_used_sqg`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.already_used_sqg "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.already_used_sqg") | Number of already processed gates per qubit. |
| [`rot_chars`](#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.rot_chars "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.rot_chars") | Readout twirling character(s) per qubit ('I' or 'X'). |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **virtual_z** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **extra_phi** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **extra_pi** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **sqg_number** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **already_used_sqg** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **rot_chars** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

virtual_z*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
Track pending Z rotations per qubit.

extra_phi*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
Track phase values for π rotations.

extra_pi*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Track count of π rotations per qubit.

sqg_number*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Number of single-qubit gates per qubit.

already_used_sqg*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Number of already processed gates per qubit.

rot_chars*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Readout twirling character(s) per qubit (‘I’ or ‘X’).
