> Full piece: [https://docs.openquantum.com/qbraid/installation/](https://docs.openquantum.com/qbraid/installation/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 54a71366c933a0ec00afc32d3959c0a4df5cad0985ab6bafa35597a4b6061113.

# Installation & Authentication

To run qBraid circuits on Open Quantum hardware you need a qBraid account, an Open Quantum account, and a one-time link between them.

## 1. Create accounts

- **Open Quantum** — sign up at [openquantum.com](https://www.openquantum.com). Every new account includes **\$50 of free Spark credits**.
- **qBraid** — sign up at [qbraid.com](https://www.qbraid.com).

## 2. Connect

Account linking is a one-time step done from **qBraid's** website:

1.  Open the [qBraid dashboard](https://account.qbraid.com/dashboard).
2.  Navigate to your [profile](https://account.qbraid.com/account/profile).
3.  In the **Integrations** field, select **Open Quantum** and follow the prompts to authorize the link.

## 3. Credentials

### In a Local Environment (e.g. VS Code)

Install the qBraid SDK and provide your qBraid API key. You can find or generate the key in your qBraid account settings.

``` bash
pip install qbraid
```

``` python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")
```

### In qBraid Lab

In [qBraid Lab](https://www.qbraid.com/lab), the qBraid SDK is preinstalled and your qBraid API key is detected automatically, so you can skip entering credentials:

``` python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()  # API key auto-detected in qBraid Lab
```

The same code runs in qBraid Lab and locally; the only difference is whether the API key is auto-detected or supplied explicitly.

## Credits

Open Quantum jobs submitted through qBraid are billed to your **Open Quantum** account. You do not need qBraid credits to run them. To check your Open Quantum balance or top up, visit your [Open Quantum account](https://www.openquantum.com). For how credit cost is calculated per backend and shot count, see [Credits & Pricing](https://docs.openquantum.com/concepts/credits/).

## Next Steps

- [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) -- list available Open Quantum devices and their qBraid device ids.
- [Examples](https://docs.openquantum.com/qbraid/examples/) -- run your first circuit.
