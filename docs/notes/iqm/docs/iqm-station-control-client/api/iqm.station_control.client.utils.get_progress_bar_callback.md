> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.utils.get_progress_bar_callback.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.utils.get_progress_bar_callback.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 553b2c9cb0e1d21e715d5368152b67693dce6094af38889b77ffd6cd1f331ebb.

# iqm.station_control.client.utils.get_progress_bar_callback

get_progress_bar_callback()  
Return a callback that creates or updates progress bars from status updates.

Notebook rendering keeps one display handle per status label so multiple bars can update in place at the same time. Labels therefore need to be unique across concurrently active loops; if two loops reuse the same label they will update the same rendered bar.

Return type:  
[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\], *None*\]
