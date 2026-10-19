> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fbd41958622d2eb7599d0de48489861d559d462c7f67c8f871551233536aceb6.

# errors

Full path: iqm.station_control.interface.errors

Data models and mapping utilities for IQM REST API error handling.

This module provides the [`IQMServerError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError") DTO, which defines the standard JSON structure for error responses across the IQM ecosystem. It also contains the logic to bridge the gap between HTTP status codes and the `IQMError` exception hierarchy.

The mapping logic supports:

1.  **Serialization & Encoding:** Transforming server-side exceptions into  
    [`IQMServerError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError") payloads while determining the appropriate HTTP status code and preserving error metadata (codes, messages, and sources).

2.  **Reconstruction & Decoding:** Converting received [`IQMServerError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError")  
    data back into the `IQMError` hierarchy on the client side, ensuring failure data remains actionable in application logic.

Functions

|  |  |
|----|----|
| [`map_from_error_to_status_code`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.map_from_error_to_status_code.html#iqm.station_control.interface.errors.map_from_error_to_status_code "iqm.station_control.interface.errors.map_from_error_to_status_code")(error) | Map a IQMError to an HTTPStatus code. |
| [`map_from_status_code_to_error`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.map_from_status_code_to_error.html#iqm.station_control.interface.errors.map_from_status_code_to_error "iqm.station_control.interface.errors.map_from_status_code_to_error")(status_code) | Map an HTTPStatus code to a IQMError. |

Classes

|  |  |
|----|----|
| [`IQMServerError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError") | Data transfer model for communicating error details over the REST API. |

Inheritance

![Inheritance diagram of iqm.station_control.interface.errors](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-692a00d874afe922ac1bd2dc959aabf7f905468e.png)
