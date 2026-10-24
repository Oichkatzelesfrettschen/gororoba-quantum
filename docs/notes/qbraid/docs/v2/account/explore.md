> Full piece: [https://docs.qbraid.com/v2/account/explore.md](https://docs.qbraid.com/v2/account/explore.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9aa633a78c9017cb53764f2f88c4bc4f7de8a38ce66e99746602b523c29d2e6a.

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

# Partner guide

> Prepare a project and its environment for publication on qBraid Explore.

# Adding your project

Use this guide to contribute a solution or project to the qBraid [Explore page](https://account.qbraid.com/explore). qBraid reviews the project and prepares its environment so users can run it in Lab.

To browse projects, events, and challenges, or submit a project through Account, see [Explore catalog](https://docs.qbraid.com/v2/account/explore-catalog).

## Step 1: Create a public GitHub repository

Create a public GitHub repository containing your project. You can include example notebooks, executable Python files, or code in other languages, such as C++ or Julia.

Include a README that describes the project and explains how to use it. Review existing Explore projects for examples, or ask your qBraid contact for guidance.

qBraid reviews your README and provides feedback. If it does not clearly describe the project, or includes setup instructions that do not apply to qBraid, we may ask for a separate Markdown file with qBraid-specific instructions. We can link the listing to that file so users see it when they open the project.

## Step 2: Send us environment and project details

Send all the details below in one email to [contact@qbraid.com](mailto:contact@qbraid.com) or your qBraid point of contact. We use these details to create the environment and prepare the project listing.

### Environment details

- Send the minimal package dependencies needed to run your code and examples, such as a `requirements.txt` or the relevant dependencies from `pyproject.toml`. Do not send a full `pip list`.
- Include square logos in both light and dark versions. qBraid uses them for the environment sidebar image and kernel logo.
- State any non-Python runtime or GPU requirements. We can arrange a custom Docker container or GPU resources and confirm the requirements with you.

### Project details

- Include a one- or two-sentence description for Explore.
- Provide tags that help users find the project.
- Include the public GitHub repository URL from Step 1.

If you have already submitted the project through **Add your project** in Account, mention that request in the email so we can match it to the environment details. The in-app form does not replace the environment requirements above.

## Step 3: What happens next

1. qBraid creates the environment and shares it with your qBraid account.
2. Find it under **Shared environments** in Lab and test your code and examples.
3. Tell your qBraid contact about any changes you need.
4. Once you are satisfied with the environment, qBraid adds the project to Explore.
5. Review the published listing and request any final changes.

## Questions?

Contact [contact@qbraid.com](mailto:contact@qbraid.com) or your qBraid point of contact.
