> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/environments.md](https://docs.qbraid.com/v2/lab/user-guide/environments.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c8b692445d7b0b183695a228b291723e1da2d231943823f1c96cf5d9b7b66f14.

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

> Install, create, share, and manage Python virtual environments for quantum computing.

The [Environment Manager](https://youtu.be/LyavbzSkvRo) is a streamlined quantum software package and virtual
environment management system provided to qBraid end-users through a simple, intuitive graphical user interface.
It offers curated development environments over a range of quantum applications.

Click the **Environments** icon in the top-right of the Lab console to open the Environment Manager sidebar and view
your currently installed environments.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/env_screenshot.png"
    alt="Environment Manager sidebar showing installed environments"
    width="100%"
  />
</div>

## Install environment

1. In the Environment Manager sidebar, click **Add** to view the environments available to install.

2. Environments are organized into **groups** (e.g. Qiskit, CUDA-Q, Pennylane). Click a group to view the environments it contains.

3. Choose an environment, expand its panel, and click **Install**. Once the installation has started, the panel is moved to the **Environments** tab. Click **Browse Environments** to return to the **Environments** tab and view its progress.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/installing_env.gif"
    alt="Installing an environment"
    width="100%"
  />
</div>

4. When the installation is complete, the environment panel's action button will switch from **Installing…** to **Add kernel**.

5. Click on the expanded environment tile to view its description, tags, package count, and Python version.
   From here you can **Add kernel** or **Remove kernel**, and click **More…** to open the full environment editor.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/env_ss.png"
    alt="Expanded environment tile showing details and actions"
    width="100%"
  />
</div>

### Filter environments

Use the toggle buttons at the top of the environment browser to switch between filter modes:

- **All** — show all available environment groups
- **Package** — filter by the primary quantum software package (Qiskit, Pennylane, Cirq, etc.)
- **Subject Matter** — filter by quantum computing domain (Chemistry, Machine Learning, Error Correction, etc.)

You can also type in the search bar to find environments by name or keyword. Use the **Discover via access code** field to add privately shared environments.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/eng_group_browse.png"
    alt="Browse environments with filter toggles and search"
    width="100%"
  />
</div>

### Browse an environment group

Click on any environment group to view the environments inside it. Each environment tile shows its name,
description, tags, package count, and an **Install** button.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/env_browse.png"
    alt="Environment group expanded showing available environments"
    width="100%"
  />
</div>

### Discover via access code

Environments shared via access code are not publicly listed. To install one of these private environments, first enter the access code
in the "Discover via access code" field and click the "**+**" button. This will add the environment to your sidebar. You can then enter
the environment name in the search bar or scroll to find it, and proceed with step 2 above to install it as usual.

If the environment doesn't appear in search results after entering the access code, click **Browse Environments** to go back to the
main sidebar, click the **Refresh** icon, and then click **Add** to return to the search page and browse for the environment again. If the
issue persists, ensure that you've entered the correct access code and are searching for the correct environment name. If you continue to
experience problems, please [contact our support team](mailto:contact@qbraid.com).

## Create environment

1. In the Environment Manager sidebar, click **Add**, then click **Create Environment**.

2. Give your custom environment a name, description, add tags, upload a logo, and specify any packages to install using
   a `requirements.txt` format.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/env_create.png"
    alt="Create Environment form"
    width="100%"
  />
</div>

After clicking **Create**, a new environment panel is created for your custom environment. You can view the environment's
install progress by returning to **My Environments**.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/creating_env.gif"
    alt="Creating a custom environment"
    width="100%"
  />
</div>

3. Once the environment has been created and any package installations have finished, the environment panel's action button
   will switch from **Installing…** to **Add kernel**, and the installed packages number will be updated.

4. Click on **More** to verify/view the environment's list of installed packages. You can use the search bar or scroll through
   the Python package (pip) list to find the exact versions of all packages and package dependencies that were installed. From the
   **More** pop-out, you can also install additional packages, remove packages, add/delete tags, and edit the environment's description.

### Clone environment

You can create a custom environment based on an existing one by cloning it. Clicking the **Clone** button will automatically populate the
`requirements.txt` file and other environment metadata in the "Custom Environment" form. This is useful, for example, if you want to make
and share changes to an environment you don't own.

## Environment editor

Click **More…** on any environment tile to open the full environment editor. From here you can:

- View and edit environment **metadata** (name, description, tags)
- Browse the full **packages list** with search, version info, and remove buttons
- **Add a package** — search PyPI and install the latest version
- **Cloud Sync** — sync the environment to the qBraid cloud for sharing
- **Share** the environment with other users via access code

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/env_more_page.png"
    alt="Environment editor showing metadata, packages, and cloud sync"
    width="100%"
  />
</div>

## Upload to cloud

Before you can share or publish an environment, you must first upload it to the qBraid cloud.
In the environment editor, scroll to the **Cloud Sync** section and click **Upload to Cloud**.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/Upload_button.png"
    alt="Upload to Cloud button in environment editor"
    width="100%"
  />
</div>

Once uploaded, the status changes to "Environment is in the cloud" and the button becomes **Sync with Cloud**
for pushing future updates.

## Share environment

In qBraid Lab, you can share your custom environments with other users. This will make your environment visible under their **Add**
environment list. They can then install it, and run code using an exact copy of your environment. This includes support for quantum jobs
and any additional configurations.

To share a custom environment, first click the **More** button in the drop-down to open the environment editor. Then, under 'Share Environment',
select **Generate Access Code** to create a unique access code. Anyone with this code will be able to
[discover](#discover-via-access-code) and [install](#install-environment) the environment with read-only access.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/request_to_publish.png"
    alt="Share environment and publish to catalog options"
    width="100%"
  />
</div>

When you share an environment via access code, you're creating a snapshot of your Python virtual environment
with its specific configurations and installed packages. This snapshot is uploaded to the qBraid cloud, creating a static version accessible
to other users. This shared version remains unchanged, even if you make updates to your local environment. To reflect any changes, you'd need
to generate a new access code and overwrite the existing version in the cloud.

Overwriting a shared environment doesn't affect versions that other users have already downloaded. Instead, an indicator notifies them
of the availability of an updated version. Currently, users must manually check for this indicator. Also, before installing an updated version,
users must uninstall their current one as maintaining multiple versions of a shared environment isn't supported.

## Publish environment

Make your custom environment accessible to the entire qBraid ecosystem by submitting a publish request. Once you've configured your environment to
meet your specifications, open the environment editor using the **More** button and select **Request to publish**. A qBraid admin will review and
test your environment as needed, providing feedback if adjustments are required. Once approved, the environment will be made public, and ownership
will be transferred to qBraid.

## Install new package

Find the environment into which you want to install the package, expand the environment panel using the carrot drop-down, and then click **More**.

At the bottom of the Python packages list, click **Add a package**. Type in the _exact_ name of the package you wish to install into the "Add package…"
search bar, and then hit `Enter` (or click the search icon on the right). This will do a direct search through [PyPI](https://pypi.org/), and return the
_latest_ version available to install. To accept, click on the package, and then click **Add**.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/installing_package.gif"
    alt="Installing a package into an environment"
    width="100%"
  />
</div>

While installing, the environment action button will indicate **Installing…**. Once complete, Lab will notify with a pop-up.

<Note>
  Package installation is blocked while file sync is in progress. Wait for sync
  to complete before installing or removing packages.
</Note>

## Uninstall / cancel install environment

To uninstall an environment or cancel the installation of an environment, click on **More**, and then **Uninstall** or **Cancel Installation**.

<Note>
  Uninstalling an environment also removes its kernel from the launcher. Any
  notebooks using that kernel will need to be switched to a different kernel.
</Note>

## Activate environment (kernel)

Clicking **Add kernel** creates a new ipykernel, see [Add/remove kernels](https://docs.qbraid.com/v2/lab/user-guide/kernels#add-and-remove-kernels) for more.

## Permissions

Some features, such as [publishing environments](#publish-environment), require an Enterprise-level subscription or partnership.
For more information, visit our [subscriptions page](https://account.qbraid.com/account/wallet) or contact us at [contact@qbraid.com](mailto:contact@qbraid.com).
