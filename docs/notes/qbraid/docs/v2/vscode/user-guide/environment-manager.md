> Full piece: [https://docs.qbraid.com/v2/vscode/user-guide/environment-manager.md](https://docs.qbraid.com/v2/vscode/user-guide/environment-manager.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 f16f7d2f50a08d18b81fccb27e237d0e64d68aa294e6497296799fad3d393b0b.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# Environment Manager

> Manage your quantum environments directly within Visual Studio Code.

The qBraid Environment Manager extension allows you to manage your Python quantum environments directly within Visual Studio Code. This includes creating, viewing, using, removing, editing, and sharing environments both locally and in the cloud.

### Installation

The Environment Manager extension can be installed directly through the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=qBraid.qbraid-environment-manager) -

<img
  src="https://qbraid-static.s3.us-east-1.amazonaws.com/qbraid-env-manager-vscode/marketplace.png"
  alt="Quantum Env Manager Extension"
  width="85%"
/>

## Managing Environments

### Create

- Create a new environment by clicking on the `Add` icon in the Environment Manager panel.
- Click on the `Create Environment` button to open the environment creation dialog.
- Enter the name and description for the environment, select the Python version, tags, and packages you want to include.
- Click on the `Create` button to create the environment.
- The new environment will be created and added to the Environment Manager panel.

- You can also choose to install an environment from the pre-configured groups such as Qiskit, qBraid, etc. -

<Tabs>
  <Tab title="Create from scratch">
    <img
      src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-create.gif"
      alt="Create Environments from Scratch"
    />
  </Tab>
  <Tab title="Install from Group">
    <img
      src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-install-catalogue.gif"
      alt="Create Environments from Group"
    />
  </Tab>
</Tabs>

### View

- You can view the created Python environments on the Environment Manager panel.
- Click on the `Environment Manager` icon in the Activity Bar on the side of the VS Code window. This will open up the Environment Manager panel where you can see all of your current installed environments.
- You can expand the dropdown pertaining to each environment to see more details, such as the Python version, packages installed, and whether it is currently active.
- Clicking on the `More` button will open up a separate panel with additional options for that environment, such as viewing and updating installed Python packages,
  or sharing the environment with others.
  {" "}
  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-view.gif"
    alt="View Environments"
  />

### Use

- Expand the dropdown for the environment you want to use and click on the `Activate` button.
- Once activated, click on the `Select Kernel` icon. This will open the selection dialog for choosing the Python kernel.
- Select the kernel corresponding to the activated environment.
- You can now run Python commands in this terminal using the selected environment.

<img
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-use.gif"
  alt="Use Environments"
/>

### Edit

- Clicking on the `More` button will open up a separate panel with additional options for that environment.
- You can edit the environment general info by clicking on the `Edit` button. This will allow you to change the name, description, and other details of the environment.
- You can also add/remove packages from the environment by clicking on the `Packages` tab in the same panel:
  - **Add**: Search for the package you want to add, select a version, and click on the `Add` button
  - **Remove**: Click on the `Remove` button next to the package.
- Once you have made all the changes, click on the `Update` button to apply them

  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-package-edit.gif"
    alt="Edit Environments"
  />

### Uninstall

- Click on the `More` button and select the `Uninstall Environment` option.
- A confirmation dialog will appear asking you to confirm the removal of the environment. Once confirmed,
  the environment will be removed from your local machine or qBraid Lab instance (if it is a cloud environment).
  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/envs-uninstall.gif"
    alt="Remove Environments"
  />

### Share

- Click on the `More` button and select the `Share Info` option.
- You can choose to share the environment via:

  - **Email**: Enter the email address of the recipient and click on the `Share` button.
  - **Access Code**: Click on the `Generate Access Code` button. This will generate a unique access code that can be shared with others to access the environment.
    The recipient can then use this code to access the environment in their own qBraid account.

## Managing Compute Resources

- As part of the Environment Manager is the **Compute Manager** extension, which allows you to connect to and manage remote qBraid Lab compute resources, including CPUs and NVIDIA GPUs.
- The Compute Manager allows you to:
  - View available compute resources in the qBraid Lab.
  - Activate or deactivate compute resources.
  - View the status of your compute resources.
  - Manage your compute instances directly from Visual Studio Code.
- To utilize the `Cloud` functionality of the Environment Manager, you must have a running instance of the [qBraid Lab](https://docs.qbraid.com/v2/lab/user-guide/overview).

  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/compute-manager.gif"
    alt="Compute Manager Extension"
    width="65%"
  />
