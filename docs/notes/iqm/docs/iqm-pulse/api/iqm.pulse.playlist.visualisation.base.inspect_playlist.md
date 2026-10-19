> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.visualisation.base.inspect_playlist.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.visualisation.base.inspect_playlist.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 17a2be713090a328d71da35e99bd063fbb701331475265fa82758528c69511ca.

# iqm.pulse.playlist.visualisation.base.inspect_playlist

iqm.pulse.playlist.visualisation.base.inspect_playlist(*playlist*, *segments=(0,)*)  
Creates an HTML string from the given playlist and segments.

The output can be viewed in a browser or in a Jupyter notebook using `IPython.core.display.HTML`.

Parameters:  
- **playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")) – The Playlist to be visualised

- **segments** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Indices of the Playlist segments to inspect.

Returns:  
The generated raw HTML string.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
