> Full piece: [https://docs.qbraid.com/v2/account/sign-in.md](https://docs.qbraid.com/v2/account/sign-in.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 fa92a7d53d36422a8b7f63e471de0cdf6bf1ebcc1d8c92ea24fef28ae9e57e4e.

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

# Sign in

> Create an account and sign in with Google, a password, an email code, or a passkey.

Open [qBraid Account](https://account.qbraid.com/signin). Choose the sign-in method available for your account.

## Use your email

Enter your email address and continue. If a registered passkey is available, your device can prompt you to use it. Otherwise, select an available method, such as your password or **Email a code**.

For an email code, check your inbox and enter the code in the sign-in form. Accounts that use Google sign-in do not use this email-code flow. Return to **Sign in with Google** for those accounts.

Use [Reset your password](#reset-your-password) if you need to recover an email-and-password account.

## Reset your password

1. Open [Reset Password](https://account.qbraid.com/forgot-password).
2. Enter your account email and select **Send Reset Code**.
3. Enter the six-digit code from your email.
4. Enter and confirm a new password. It must contain at least eight characters, including a lowercase letter, an uppercase letter, a number, and a special character.
5. Select **Reset Password**. After success, the page returns you to sign-in.

Select **Use a different email** if you entered the wrong address. If the reset fails, review the error before trying again. Accounts registered through Google should use **Sign in with Google**.

## Use Google

Select **Sign in with Google** and choose the Google account associated with your qBraid account.

## Create an account

Open [Sign up](https://account.qbraid.com/signup). Register with Google or complete the email registration form, including the password requirements shown there. Complete email verification if prompted.

If you arrived through an organization invitation, finish registration and return to the invitation to accept it. See [Join an organization](https://docs.qbraid.com/v2/account/organizations/invitations).

## Complete first-login setup

If cookie preferences appear, make your choice first. New accounts then complete four setup steps:

1. **Your role**: choose your role.
2. **What you'll do here**: select at least one intended use.
3. **Where we found each other**: choose how you heard about qBraid.
4. **About you**: provide a username, first name, and last name. A profile photo is optional.

Select **Next** between steps, then **Enter qBraid** to finish. If you select **Other**, fill in the accompanying explanation.

The **Getting Started** tour opens with **Welcome to qBraid** after setup. Follow it to explore the dashboard and run a simulator circuit, or select **Skip for now**, then confirm **Skip tour**. Restart it later from **? > Tour menu** in the top bar.

## Add a passkey

After signing in, open [Profile](https://docs.qbraid.com/v2/account/profile#manage-passkeys) to register a passkey. Passkeys let you use a device's fingerprint, face, or security key for later sign-ins.
