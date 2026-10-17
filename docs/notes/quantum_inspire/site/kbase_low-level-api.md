> Full piece: [https://www.quantum-inspire.com/kbase/low-level-api/](https://www.quantum-inspire.com/kbase/low-level-api/)
> Retrieved 2026-10-16T22:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 fbc0c3ca3c7e503b0092a4fde57f8010a0c975e441b3469bfd8206090aa0abf8.

# Low-level API

Below we describe the low-level API to the Quantum Inspire platform. Quantum Inspire also offers a Software Development Kit (SDK) to advanced users that will allow programmatic control over all functionality using Python. For more information see the [Software Development Kit](https://www.quantum-inspire.com/kbase/software-development-kit/) page.

## Application Programmer Interface (API)

The [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) API can be found on <https://api.quantum-inspire.com/>. OpenAPI documentation is published on <https://api.quantum-inspire.com/docs>

Forms are provided for all endpoints to create new objects or modify existing objects.

## OpenAPI client

To consume the API, Quantum Inspire has provided an api-client that handles all communication. This api-client can be installed from [PyPI](https://pypi.org/project/qi-compute-api-client/).

A basic example consumer of this schema written in [Python](https://www.python.org/) might look like this:

[Previous](https://www.quantum-inspire.com/kbase/opensquirrel/) [Next](https://www.quantum-inspire.com/kbase/libket/)
