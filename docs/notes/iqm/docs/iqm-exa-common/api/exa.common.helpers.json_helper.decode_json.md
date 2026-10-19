> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.json_helper.decode_json.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.json_helper.decode_json.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26c6bb3648f1bd9ef9ef982ce20016ed36cb19c61889750cf55e07e17442df11.

# exa.common.helpers.json_helper.decode_json

decode_json(*obj*)  
Custom json decoder for object, in case it is represented as complex number, ndarray or tuple. Otherwise decoder won’t be applied

Here is an example of encoded/decoded json with complex number and ndarray:

```
>>> import base64
>>> import numpy as np
>>> from exa.common.helpers.json_helper import decode_json
>>> complex_encoded = {'__complex__': True, 'real': 3, 'imag': 4}
>>> decode_json(complex_encoded)
(3+4j)

>>> data_b64 = base64.b64encode(np.arange(4).reshape(2, 2))
>>> ndarray_encoded = {'__ndarray__': True, 'data': data_b64.decode('utf-8'), 'dtype': 'int64', 'shape':[2, 2]}
>>> decode_json(ndarray_encoded)
array([[0, 1],
       [2, 3]])
```

Parameters:  
**obj** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")
