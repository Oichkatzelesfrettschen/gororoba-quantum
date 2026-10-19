> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.repr_mimebundle.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.repr_mimebundle.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 edb5a62015e32f2ddbae7e9b4a1b9e901bd7d5ccfad76e296cda331544d3f406.

# exa.common.helpers.notebook_helper.repr_mimebundle

repr_mimebundle(*node*, *include=None*, *exclude=None*)  
Backing implementation of `SettingNode._repr_mimebundle_()`.

Builds the lazy ipywidgets renderer when `ipywidgets` is importable; otherwise returns a static root-only summary. The widget bundle also carries cheap `text/html` / `text/plain` fallbacks so non-widget frontends still show something.

Parameters:  
- **node** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")) – The node to render.

- **include** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – MIME types to include, forwarded to the widget’s mimebundle.

- **exclude** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – MIME types to exclude, forwarded to the widget’s mimebundle.

Returns:  
A MIME bundle mapping MIME type to representation.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), *Any*\] \| [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), *Any*\], [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), *Any*\]\]
