> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.qcm_data_client.QCMDataClient.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.qcm_data_client.QCMDataClient.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 61fd82b3ef59e54313c9304292d781752799c8babcafbf12f6a254b95f0fd8e9.

# QCMDataClient

Module: [`exa.common.qcm_data.qcm_data_client`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.qcm_data_client.html#module-exa.common.qcm_data.qcm_data_client "exa.common.qcm_data.qcm_data_client")

*class* QCMDataClient(*root_url*, *fallback_root_url=''*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Python client for QCM (Quantum Computer Management) Data API.

Parameters:  
- **root_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – URL pointing to QCM Data service. This URL can point to a local file storage as well. In that case, the URL should point to a directory which has a directory structure identical to QCM Data service (for example /chip-data-records/), and files containing data in identical format returned by QCM Data service. For example, CHAD files should be named {chip_label}.json, like M156_W531_A09_L09.json, and contain a list instead of a single object.

- **fallback_root_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Same as root_url, used if a query via root_url returns nothing.

Attributes

|  |  |
|----|----|
| [`root_url`](#exa.common.qcm_data.qcm_data_client.QCMDataClient.root_url "exa.common.qcm_data.qcm_data_client.QCMDataClient.root_url") | Returns the remote QCM Data service URL. |

Methods

|  |  |
|----|----|
| [`get_chip_design_record`](#exa.common.qcm_data.qcm_data_client.QCMDataClient.get_chip_design_record "exa.common.qcm_data.qcm_data_client.QCMDataClient.get_chip_design_record") | Get a raw chip design record matching the given chip label. |

*property* root_url*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Returns the remote QCM Data service URL.

get_chip_design_record(*chip_label*)  
Get a raw chip design record matching the given chip label.

Parameters:  
**chip_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Chip label.

Returns:  
Data record matching the given chip label.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")

Inheritance

![Inheritance diagram of exa.common.qcm_data.qcm_data_client.QCMDataClient](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-55476cda9bb71a8905ff65f3bc9699c0b7fa1ae7.png)
