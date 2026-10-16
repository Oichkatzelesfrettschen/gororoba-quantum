> Full piece: [https://www.quantum-inspire.com/kbase/low-level-api/](https://www.quantum-inspire.com/kbase/low-level-api/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 ee57cad5a0adf3459393e11f7860778b4dd706c1d1cdcf6ea99848b5bc4f2764.

# Low-level API

Below we describe the low-level API to the Quantum Inspire platform. Quantum Inspire also offers a Software Development Kit (SDK) to advanced users that will allow programmatic control over all functionality using Python. For more information see the [Software Development Kit](https://www.quantum-inspire.com/kbase/software-development-kit/) page.

## Application Programmer Interface (API)

The [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) API can be found on <https://api.quantum-inspire.com/>. OpenAPI documentation is published on <https://api.quantum-inspire.com/docs>

Forms are provided for all endpoints to create new objects or modify existing objects.

## OpenAPI client

To consume the API, Quantum Inspire has provided an api-client that handles all communication. This api-client can be installed from [PyPI](https://pypi.org/project/qi-compute-api-client/).

A basic example consumer of this schema written in [Python](https://www.python.org/) might look like this:

```python
import time
import compute_api_client
from compute_api_client.rest import ApiException
from pprint import pprint

configuration = compute_api_client.Configuration(
    host = "https://api.quantum-inspire.com"
)

# Quantum Inspire uses bearer tokens, provided by our IdP.
configuration.access_token = os.environ["ACCESS_TOKEN"]

async with compute_api_client.ApiClient(configuration) as api_client:
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    algorithm_in = compute_api_client.AlgorithmIn()
    try:
        api_response = await api_instance.create_algorithm_algorithms_post(algorithm_in)
        print("The response of AlgorithmsApi->create_algorithm_algorithms_post:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AlgorithmsApi->create_algorithm_algorithms_post: %s\n" % e)
```

[Previous](https://www.quantum-inspire.com/kbase/opensquirrel/) [Next](https://www.quantum-inspire.com/kbase/libket/)
