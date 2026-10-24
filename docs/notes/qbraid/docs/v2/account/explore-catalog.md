> Full piece: [https://docs.qbraid.com/v2/account/explore-catalog.md](https://docs.qbraid.com/v2/account/explore-catalog.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 45641bc622f9096f62b233a5f87ae5b6e6127793d62ea8266e2e7f1197525ec0.

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

# Explore catalog

> Find projects, courses, events, and challenges, or submit a project for the qBraid catalog.

For partner onboarding, custom environments, and publication review, see the [Partner guide](https://docs.qbraid.com/v2/account/explore).

## Find a project

Open [Explore](https://account.qbraid.com/explore) and search the project catalog. Select a project to read its README, releases, repository information, and tags.

When a project offers a Lab launch, use its launch control to clone the repository and start a compute environment. Review the selected workspace and compute profile before launching. A listed project can have restricted access or show **Coming Soon** before its public release.

## Submit your project

1. Prepare a GitHub repository with the code and a README that explains how to use it.
2. Open **Explore**.
3. Select **Add your project**, then **Get Started**.
4. Enter the project title and GitHub repository URL.
5. Submit the request for review.

qBraid fetches the repository's description, README, and language information from GitHub. A successful submission displays **Request Submitted**. Submission does not publish the project immediately.

If the project needs a custom environment, follow the [Partner guide](https://docs.qbraid.com/v2/account/explore#step-2-send-us-environment-and-project-details) to send dependencies, runtime requirements, logos, and listing details. The guide covers environment testing and publication review.

## Events and challenges

Use **Events & Hackathons** for upcoming events and archived event details. Registration, meeting, and website links depend on the event. The **Challenges** tab contains available challenges and their entry requirements.

## Learn

Open [Learn](https://account.qbraid.com/learn) to browse and search courses. Select a course for its description and available learning materials. Availability and access depend on the course. See [Learn with qBook](https://docs.qbraid.com/v2/home/learning) for course launch and resume instructions.

The Explore page links to qBraid's Discord and GitHub communities. Use [Support](https://docs.qbraid.com/v2/account/support) for account help. The standalone Community page is a placeholder.
