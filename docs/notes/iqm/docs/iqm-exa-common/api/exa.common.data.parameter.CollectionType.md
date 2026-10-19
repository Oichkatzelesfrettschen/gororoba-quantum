> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4ff449aab56dd6bb8fb771ff0c668891d036a83f4d4da0a745f9a53e05ff89d5.

# CollectionType

Module: [`exa.common.data.parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html#module-exa.common.data.parameter "exa.common.data.parameter")

*class* CollectionType(*value*)  
Bases: [`IntEnum`](https://docs.python.org/3.11/library/enum.html#enum.IntEnum "(in Python v3.11)")

Parameter collection type.

Attributes

|  |  |
|----|----|
| [`SCALAR`](#exa.common.data.parameter.CollectionType.SCALAR "exa.common.data.parameter.CollectionType.SCALAR") | Scalar, not a list of any kind. |
| [`LIST`](#exa.common.data.parameter.CollectionType.LIST "exa.common.data.parameter.CollectionType.LIST") | Python list. |
| [`NDARRAY`](#exa.common.data.parameter.CollectionType.NDARRAY "exa.common.data.parameter.CollectionType.NDARRAY") | Numpy ndarray. |

Methods

|  |  |
|----|----|
| [`cast`](#exa.common.data.parameter.CollectionType.cast "exa.common.data.parameter.CollectionType.cast") | Cast the given value to this collection type. |

SCALAR *= 0*  
Scalar, not a list of any kind.

LIST *= 1*  
Python list.

NDARRAY *= 2*  
Numpy ndarray.

cast(*value*)  
Cast the given value to this collection type.

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")

Inheritance

![Inheritance diagram of exa.common.data.parameter.CollectionType](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-e70931cd0a8a09e149792eadddf161441a247c80.png)
