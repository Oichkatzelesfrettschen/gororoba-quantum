> Full piece: [https://docs.openquantum.com/qbraid/overview/](https://docs.openquantum.com/qbraid/overview/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0ea9fe8c8f7615f4891195740230e364d16685ea1c733e03bd8f225676af6f57.

# qBraid Integration

Run your [qBraid](https://www.qbraid.com/) circuits on real quantum hardware through Open Quantum. Link your accounts once, then target any Open Quantum backend from the qBraid runtime you already use; execute on QPUs from IonQ, Rigetti, IQM, and AQT without changing circuit code.

The integration is available inside [qBraid Lab](https://www.qbraid.com/lab) notebooks and from any local environment using the qBraid SDK.

## Overview

Once your qBraid and Open Quantum accounts are linked, Open Quantum backends appear as qBraid devices and can be selected with the standard qBraid runtime API:

``` python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")
device = provider.get_device("openquantum:iqm:qpu:garnet")
```

Open Quantum handles transpilation, routing, and result formatting, and bills the job to your Open Quantum credits. You do **not** need qBraid credits to run on Open Quantum backends.

## qBraid SDK

The [qBraid SDK](https://github.com/qBraid/qBraid) is a platform-agnostic quantum runtime framework that runs anywhere Python runs, including local editors such as VS Code. It supports over 10 major languages with built-in cross-framework transpilation and handles the full lifecycle of a quantum job through one interface. Full documentation and the API reference are available at [docs.qbraid.com](https://docs.qbraid.com/v2/sdk/user-guide/overview).

Using it with Open Quantum backends works the same way as any other qBraid-supported device: write your circuit as you normally would, then simply target an Open Quantum device string through the qBraid runtime instead of another provider.

See [Installation & Authentication](https://docs.openquantum.com/qbraid/installation/) to get set up.

## qBraid Lab

[qBraid Lab](https://www.qbraid.com/lab) is a web-based IDE for quantum computing. Inside Lab, the qBraid SDK is already installed and your qBraid API key is detected automatically, so you can simply run circuits without any local setup.

## How the Integration Works

1.  **Link accounts.** Connect your qBraid and Open Quantum accounts once via the qBraid website. See [Installation & Authentication](https://docs.openquantum.com/qbraid/installation/) for a step-by-step guide.
2.  **Select an Open Quantum device.** Call `provider.get_device()` with an Open Quantum device id (for example, `openquantum:iqm:qpu:garnet`).
3.  **Run.** Submit your circuit with `device.run()`. The job executes on Open Quantum hardware and the cost is drawn from your Open Quantum credits.
4.  **Retrieve results.** Call `job.result()` and read measurement counts with `result.data.get_counts()`.

## Next Steps

- [Installation & Authentication](https://docs.openquantum.com/qbraid/installation/) -- configure accounts and credentials.
- [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) -- target Open Quantum QPUs.
- [Examples](https://docs.openquantum.com/qbraid/examples/) -- run complete circuits.
