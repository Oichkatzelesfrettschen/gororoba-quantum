> Full piece: [https://cloud.quandela.com/webide/guide/entity-manage-guide/00-introduction](https://cloud.quandela.com/webide/guide/entity-manage-guide/00-introduction)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/entity-manage-guide/00-introduction.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Introduction

## Overview of the Entity Manager Role

In this system, the **Entity Manager** is a permissioned user within an organization (referred to as an "entity") who is responsible for managing shared resources (tokens, jobs, platforms), users, and entity-level configurations. This role is designed to empower organizations to self-manage their environment while maintaining secure, scoped control.

Entity Managers do not manage the system globally — their access and capabilities are restricted to their own entity and based on explicitly assigned permissions.

Depending on the permissions granted, an Entity Manager may:

- Invite, remove, or configure other users within the entity
- Manage tokens, jobs, platform access, and usage data
- Handle subscriptions, billing, and credit purchases for the entity

## System Structure

The system is divided into two main environments:

**Account Management** ([http://account.quandela.com/](http://account.quandela.com/))

![image-20250626-043605.png](https://cloud.quandela.com/webide/docs-assets/1365114920.png)

Focuses on entity setup, user management, billing, and permissions.
Entity-related sections include:

- **Overview**: Dashboard summary
- **Entity Setting**:
  - `Member`: Manage users within the entity
  - `Setting`: Update entity metadata
  - `Resource Permissions`: Manage fine-grained permission rules
- **Entity Billing**:
  - `Subscription`: Manage current offer and plan
  - `Invoice and Card`: View billing history and update payment methods
  - `Buy Credit`: Add usage credit for cloud services

**Cloud Management** ([https://cloud.quandela.com/webide/](https://cloud.quandela.com/webide/))

![image-20250626-043811.png](https://cloud.quandela.com/webide/docs-assets/1365114927.png)

Focuses on operational tools, platform access, resource (jobs, qrng) consumption, and entity-wide application usage.
Entity-related sections include:

- **Overview**: Entity dashboard overview
- **Entity Manager**:
  - `Entity Jobs`, `Entity Tokens`, `Entity Platforms`
  - `Assign Platforms`, `Entity Quantum Toolbox`, `Assign Quantum Toolbox`
  - `Entity QRNG Consumption`, `Platform Booking`

> Personal profile sections (e.g. *Your Profile*, *Your Billing*) are not covered in this guide.

## Permission-Based Access Control (resource:action)

The system uses a fine-grained access control model where each capability is expressed as a combination of:

- **Resource**: the type of object being managed (e.g. `user`, `token`, `job`)
- **Action**: the operation being allowed (e.g. `create`, `view`, `edit`)

For example:

- `user:create` – Create new entity users
- `token:create` – Generate new access tokens
- `invoice:view` – View entity-level invoices
- `platform_booking:booking` – Book computation time on a platform

UI elements are shown or hidden dynamically based on the active user's permission set.

This ensures that users only see what they are allowed to act on — reducing errors and improving security.
