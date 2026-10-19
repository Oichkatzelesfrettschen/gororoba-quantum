> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.software_version_helper.get_all_software_versions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.software_version_helper.get_all_software_versions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 23cf0cdf911ac99bb1e9f5938af8c54718b25bc5861223660857ec9fe6767b9d.

# exa.common.helpers.software_version_helper.get_all_software_versions

get_all_software_versions()  
Get all available software version information.

Currently, this function collects all Python package versions and Python interpreter version.

Returns: All software components in a dictionary that maps each package name to its version  
information. A package’s version information contains the base version, and the string “(local editable)” in the case the package is a local editable installation.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
