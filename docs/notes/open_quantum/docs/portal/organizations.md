> Full piece: [https://docs.openquantum.com/portal/organizations/](https://docs.openquantum.com/portal/organizations/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d375fd01d1a15927c66e057112354c0d90ef15baa2e301711d0e6719a5b5fec7.

# Organizations

Beta Feature

Organization support is currently in beta. If you'd like to create a shared organization for your team, reach out to us at <support@openquantum.com>.

Organizations let teams share credits and collaborate on quantum jobs. Team members in the same organization can see each other's jobs, share a credit balance, and manage access from the portal.

## Your Default Organization

When you sign up, a default organization is created for you. All jobs and credits are associated with this organization. For most individual users, this is all you need.

## What Organizations Enable

With a shared organization, your team can:

- **Share credits** -- One credit balance for the whole team, no need for individual purchases.
- **Share job access** -- Everyone in the organization can view, monitor, and download results for all jobs.
- **Collaborate** -- Run experiments from different machines and review each other's results in the portal.

## Switching Organizations

If you belong to multiple organizations, you can switch between them in the portal. The active organization determines:

- Which credit balance is used for jobs.
- Which jobs you see on the [Jobs](https://www.openquantum.com/jobs) page.
- Which SDK keys are available.

When using the SDK, specify the organization with the `organization_id` parameter or the `OPENQUANTUM_ORGANIZATION_ID` environment variable. You can list your organizations programmatically — see [Authentication](https://docs.openquantum.com/core-sdk/authentication/#organization-id) for details.

## Getting Access

To set up a shared organization for your team, contact us at <support@openquantum.com>. We'll help you get started with:

- Creating your organization.
- Inviting team members.
- Configuring shared credit balances.

## Use Cases

- **Solo researcher** -- Your default organization is all you need.
- **Lab or team** -- Share credits and job visibility across your group.
- **Multiple projects** -- Separate organizations keep credits and jobs isolated between projects.
