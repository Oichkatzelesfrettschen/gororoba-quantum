> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.value.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.value.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 50d29e46c0e89f0ed47c06a25a0b2bf3b13992a19adac987a2ba2db37f869a70.

# value

Full path: exa.common.data.value

Validation for observation values.

Functions

|  |  |
|----|----|
| [`serialize_value`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.value.serialize_value.html#exa.common.data.value.serialize_value "exa.common.data.value.serialize_value")(value) | Serialize value type to JSON serializable type, to support complex and ndarray types. |
| [`validate_value`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.value.validate_value.html#exa.common.data.value.validate_value "exa.common.data.value.validate_value")(value) | Validate (i.e. deserialize) JSON serializable value to Python type, to support complex and ndarray types. |
