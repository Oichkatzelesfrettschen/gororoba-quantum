> Full piece: [https://docs.openquantum.com/vscode/installation/](https://docs.openquantum.com/vscode/installation/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b2254a783d98f177a3ac10fafe269149bf8ea071c2fff4686755401a344ee59a.

# Installation & Setup

The Open Quantum extension runs in Visual Studio Code 1.90 or newer, and in VS Code-compatible editors. You need an Open Quantum account and an SDK key to run circuits; syntax highlighting and error checking work without one.

## 1. Install the extension

Install from the Visual Studio Code Marketplace:

1.  Open the **Extensions** view in VS Code.
2.  Search for **Open Quantum** and click **Install**.

You can also install it from the [Marketplace listing](https://marketplace.visualstudio.com/items?itemName=quantum-rings.openquantum-vscode) in your browser, or from the Command Palette with:

```
ext install quantum-rings.openquantum-vscode
```

Highlighting and error underlines for `.qasm`, `.qasm2`, `.qasm3`, and `.openqasm` files are active immediately.

## 2. Create an SDK key

To run circuits, create a key at [openquantum.com/settings/keys](https://www.openquantum.com/settings/keys). Every new Open Quantum account includes **\$50 of free Spark credits**, so you can run on real hardware without a credit card.

The extension reads the same key file as the Python SDK (`OPENQUANTUM_SDK_KEY`), so if you already use the SDK locally you are ready to run.

## 3. Connect the extension

1.  Open the **Open Quantum** view from the Activity Bar.
2.  Run **Set SDK Key**, from the view or the Command Palette.
3.  Point it at the key JSON you created, or paste the key.

Your organizations, backends, and credits load into the view once the key is set, and the backend list keeps its status and queue depth current while the view is open. If your key has access to more than one organization, choose one from **Settings**.

## Credits

Circuits submitted from the extension are billed to your Open Quantum account, the same as jobs from the portal or the Python SDK. To check your balance or top up, visit your [Open Quantum account](https://www.openquantum.com). For how cost is calculated per backend and shot count, see [Credits & Pricing](https://docs.openquantum.com/concepts/credits/).

## Next Steps

- [Features & Usage](https://docs.openquantum.com/vscode/features/) to run your first circuit and see the full command and settings list.
