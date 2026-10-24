> Full piece: [https://docs.qbraid.com/v2/account/organizations/overview.md](https://docs.qbraid.com/v2/account/organizations/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 87f750f45daa1565079c38a41b6589e80d66cb0706501a3e890176a163b504d5.

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

# Overview

> Share resources, manage members, and centralize team billing in a qBraid organization.

A qBraid organization is a workspace with its own members, subscriptions, and credits. Select the organization in the workspace switcher before using its resources or changing its settings.

Your qBraid Default workspace remains available for personal work. Team subscription seats and organization credit allocations are managed separately from a personal subscription.

## Membership and access

- [Create an organization](https://docs.qbraid.com/v2/account/organizations/creating-an-organization) by submitting a request for review.
- [Join an organization](https://docs.qbraid.com/v2/account/organizations/invitations) with an email invitation or invite code.
- [Invite codes](https://docs.qbraid.com/v2/account/organizations/invite-codes) covers shareable codes, join links, QR images, redemption, and limits.
- [Members and invitations](https://docs.qbraid.com/v2/account/organizations/members) covers email invitations, roles, member access, and ownership transfer.
- [Settings](https://docs.qbraid.com/v2/account/organizations/settings) controls organization details and new-member defaults.

Organizations have Admin, Manager, and Member roles, plus one Owner. Available actions depend on your role. The owner can transfer ownership to another active member through **Members > Edit Role**.

## Billing and usage

- [Seats](https://docs.qbraid.com/v2/account/organizations/seats) grant team subscription benefits to individual members.
- [Credits](https://docs.qbraid.com/v2/account/organizations/credits) covers the organization wallet and transfers to members.
- [Credit requests](https://docs.qbraid.com/v2/account/organizations/credit-requests) lets members request an allocation.
- [Subscriptions](https://docs.qbraid.com/v2/account/organizations/subscriptions) covers team plans.
- [Transactions](https://docs.qbraid.com/v2/account/organizations/transactions) records credit movements.
- [Organization usage](https://docs.qbraid.com/v2/account/organizations/usage) shows member consumption and quantum jobs for administrators.

## Your organization profile

[My Profile](https://account.qbraid.com/organizations/profile) shows your membership roles and status in the selected organization. Its **Usage** and **API Keys** tabs provide resource and credential views for that workspace. Organization administrators use the separate organization Usage page for activity across all members.
