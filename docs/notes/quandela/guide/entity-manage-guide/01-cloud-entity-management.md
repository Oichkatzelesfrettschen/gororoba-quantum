> Full piece: [https://cloud.quandela.com/webide/guide/entity-manage-guide/01-cloud-entity-management](https://cloud.quandela.com/webide/guide/entity-manage-guide/01-cloud-entity-management)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/entity-manage-guide/01-cloud-entity-management.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Cloud — Entity Management

## Entity Jobs & Tokens

### 1. View and manage jobs (re-run/cancel/change limit) under the entity

**Purpose:**
To view, monitor, and take actions on jobs that are executed within the scope of your entity. This includes checking job status, viewing results, canceling jobs, or rerunning them when necessary.

**Permission:**

- `job:view` – View job list and job details
- `job:cancel` – Cancel a waiting or running job
- `job:rerun` – Rerun an error job
- `job:edit` – Update a waiting job

**Procedure:**

![image-20250628-092048.png](https://cloud.quandela.com/webide/docs-assets/1364754451.png)

**Step 1**: On the sidebar menu, go to **Entity Manager > Entity Jobs**.

**Step 2**: A list of recent jobs under your entity will be displayed.

**Step 3**: Click on a job row to view detailed logs and output results.

**Step 4** *(if permissions apply)*:

![image-20250628-094121.png](https://cloud.quandela.com/webide/docs-assets/1364754458.png)

- To cancel a running job, click **"Cancel"** in the job actions menu.
- To rerun a job, click **"Re-run"**, fill payload and confirm the action.
- To change limit of job, click **"Change limit"** and confirm the action.

### 2. Generate tokens

**Purpose:**
To create a new token under the entity, allowing users or applications to authenticate and access specific services (e.g., platforms, quantum toolbox).

**Permission:**

- `token:create`

**Procedure:**

![image-20250628-092732.png](https://cloud.quandela.com/webide/docs-assets/1364754464.png)

**Step 1**: From the sidebar menu, go to **Entity Manager > Entity Tokens**.

**Step 2**: Click the **"Create New"** button.

**Step 3**: In the token creation form:

- **Select user**: Choose the user who will own this token.
- **Token name**: Enter a descriptive name, e.g., `api_key_dev`.
- **Priority**: Choose a priority level to influence job scheduling (if supported).
- **Duration**: Set how long the token will be valid (e.g., `30` days).
- **Mark as Explorer Token** (checkbox):
  - Select this if the token is intended for free-tier use.
  - Explorer Tokens are limited to the **Explorer Offer** and consume **free credits** only.

**Step 4**: Click **Create** to finalize the token.

### 3. View and manage tokens (revoke/delete) under the entity

**Purpose:**
To view the list of all tokens issued under your entity and manage them — primarily by revoking (deleting) expired, unused, or unnecessary tokens.

**Permission:**

- `token:view` – View list and details of tokens
- `token:delete` – Revoke (delete) a token

**Procedure:**

![image-20250628-092912.png](https://cloud.quandela.com/webide/docs-assets/1364754470.png)

**Step 1**: From the sidebar, go to **Entity Manager > Entity Tokens**.

**Step 2**: The token list displays a table with the following columns (can be toggled on/off):

- **Selection** – Checkbox to select tokens for bulk action (delete)
- **Action** – Available actions (e.g., delete/revoke)
- **User** – The user who owns the token
- **Token name** – Name given at creation
- **Priority** – Token execution priority
- **Status** – Indicates if token is active, expired, or revoked
- **Value** – The actual token string or partial value
- **Created time** – When the token was generated
- **Expiration time** – When the token will expire
- **Used times** – Number of times the token was used
- **Last used** – Timestamp of last use
- **Duration of last used** – Duration of the last job executed with the token

**Step 3**: To revoke a token:

- Click the **Action** icon (often a trash/bin or vertical ellipsis)
- Select **Revoke** or **Delete**

![image-20250628-092949.png](https://cloud.quandela.com/webide/docs-assets/1364754476.png)

- Confirm the action in the dialog popup

### 4. Update token (name & priority)

**Purpose:**
To rename a token or change its priority level to affect scheduling behavior or organizational tracking.

**Permission:**

- `token:edit`

**Procedure:**

![image-20250628-093118.png](https://cloud.quandela.com/webide/docs-assets/1364754482.png)

**Step 1**: In the **Entity Tokens** list, locate the token you want to update.

**Step 2**: Click the **pencil icon (✏️)** beside the token name to edit.

**Step 3**: In the edit dialog:

- Update the **name** and/or **priority**
- Save changes by clicking **Update**

### 5. View token access (platform / quantum toolbox)

**Purpose:**
To inspect which platforms or quantum toolbox a specific token is authorized to access.

**Permission:**

- `token:view`

**Procedure:**

![image-20250628-093216.png](https://cloud.quandela.com/webide/docs-assets/1364754488.png)

**Step 1**: From the **Entity Tokens** list, click the **token name** you want to inspect.

**Step 2**: The token detail page opens, showing:

- Assigned **Platforms**
- Assigned **Quantum Toolbox**

## Entity Platforms & Assignments

### 1. View platforms assigned to the entity.

**Purpose:**
To see the list of platforms that are available to your entity for use, booking, or job execution.

**Permission:**

- `platform:view`

**Procedure:**

![image-20250628-093406.png](https://cloud.quandela.com/webide/docs-assets/1364754494.png)

**Step 1**: Navigate to **Entity Manager > Entity Platforms** from the sidebar.

**Step 2**: The table shows all platforms assigned to your entity, including:

- **Platform name**
- **Status** (e.g., active, unavailable)
- **Price per shot** (if pricing applies)
- **Max duration** (if usage limit is set)

### 2. Assign/unassign platforms to users

**Purpose:**
To delegate access to specific platforms to users within your entity, including setting time limits (max duration) or revoking access when no longer needed.

**Permission:**

- `platform:assign`

**Procedure:**

![image-20250628-093457.png](https://cloud.quandela.com/webide/docs-assets/1364754500.png)

**Step 1**: Go to **Entity Manager > Assign Platforms**.

**Step 2**: Use the **Select User** dropdown to choose the user you want to manage platform access for.

Once a user is selected, two blocks are shown:

**Block 1: Assign New Platform**

- **Platform**: Select a platform from the dropdown list.
- **Max Duration**: Set an optional usage duration limit (e.g., `00:30:00`).
  - Leave as **"no limit"** if unrestricted.
- Click **Add** to assign the platform.

**Block 2: Assigned Platform**

A table listing all platforms currently assigned to the selected user:

- **Action**: Update max_duration / Unassign platform
- **Name**: Platform name
- **Status**: Whether the platform is currently usable
- **Price per shot**: Usage cost, if applicable
- **Max Duration**: Time limit set per execution

> Platforms available in the offer do not need to be assigned.

## Platform Booking (Enterprise Offer)

### 1. View Platform Timesheet

**Purpose:**
To view a weekly calendar showing platform availability, bookings, and maintenance windows for a selected platform.

**Permission:**

- `platform_booking:view`

**Procedure:**

![image-20250628-094341.png](https://cloud.quandela.com/webide/docs-assets/1364754506.png)

**Step 1**: Go to **Entity Manager > Platform Booking**.

**Step 2**: Use the **Platform** dropdown to select the desired platform (e.g., `qpu:belenos`).

**Step 3**: The calendar displays booking slots in the selected week. Each booking block shows:

- Time range (e.g., `19:00 – 20:00`)
- Booking label (e.g., `Sun Power booked`, `Maintenance`)
- Color-coded status

Use the arrow button or the "today" button to navigate between weeks.

💡 **Note:**

- Grey blocks indicate general bookings.
- Orange blocks represent maintenance periods where booking is unavailable.
- Blue blocks are valid bookings made by the entity.

### 2. Book platform time slots

**Purpose:**
To reserve a specific time slot for exclusive access to a quantum platform, available only to Enterprise entities.

**Permission:**

- `platform_booking:booking`

**Procedure:**

![image-20250628-094421.png](https://cloud.quandela.com/webide/docs-assets/1364754512.png)

**Step 1**: In the **Platform Booking Calendar**, click on an **empty slot** within the available time range.

**Step 2**: A **booking popup** appears. Configure:

- **Date** (pre-filled based on selected slot)
- **Time range**: Select **start time** and **end time**

**Step 3**: Click **Save** to finalize the booking.

💡 **Note:**

- You cannot book over existing reservations or maintenance windows.
- Booking time is exclusive: no other entity can access the platform during your reserved slot.
- Use the **gear icon** (⚙️) next to platform dropdown for extra settings if available.

### 3. View reject booking history

**Purpose:**
To review a log of previously rejected platform booking requests by your entity. This helps understand why bookings failed (e.g., overlap, invalid time, system constraints).

**Permission:**

- `platform_booking:view`

---

**Procedure:**

![image-20250628-094530.png](https://cloud.quandela.com/webide/docs-assets/1364754518.png)

**Step 1**: Navigate to **Entity Manager > Platform Booking**.

**Step 2**: At the bottom-left of the calendar, click the **"Open History"** button.

**Step 3**: A history modal will appear, showing:

- **Requested Date & Time**
- **Status** (Booking Rejected / Cancel Rejected)
- **Reason** for rejection (if available)

## Entity Quantum Toolbox & Assignments

### 1. View toolbox assigned to the entity

**Purpose:**
To display a list of quantum toolboxes available for the entity, including their command, pricing per job, and links to documentation.

**Permission:**

- `qt_toolbox:view`

**Procedure:**

![image-20250628-093545.png](https://cloud.quandela.com/webide/docs-assets/1364754524.png)

**Step 1**: On the sidebar, go to **Entity Manager > Entity Quantum Toolbox**.
**Step 2**: The list will show toolboxes with the following columns:

- **Name**
- **Command**
- **Price / job**
- **Link to API description**
- **Documentation page**

### 2. Assign/Unassign toolbox access to users

**Purpose:**
To control which quantum toolbox algorithms are accessible to which users under your entity.

**Permission:**

- `qt_toolbox:assign`

**Procedure:**

![image-20250628-093631.png](https://cloud.quandela.com/webide/docs-assets/1364754530.png)

**Step 1**: Go to **Entity Manager > Assign Quantum Toolbox**.
**Step 2**: Select the user from the dropdown list.
**Step 3**: On the left block, under **Assign New Algorithm**, select a toolbox and click **Add**.
**Step 4**: On the right block, under **Assigned Algorithm**, view the toolboxes already assigned to the user.

To unassign or modify settings, click the **gear icon** next to the assigned toolbox name.

## Entity QRNG Consumption

### 1. Monitor QRNG usage under the entity

**Purpose:**
To provide a detailed log of QRNG (Quantum Random Number Generator) API consumption activities performed by users within the entity.

**Permission:**

- `qrng:view`

**Procedure:**

![image-20250628-093703.png](https://cloud.quandela.com/webide/docs-assets/1364754536.png)

**Step 1**: On the sidebar, go to **Entity Manager > Entity QRNG Consumption**.
**Step 2**: The QRNG Consumption Logs page shows a list of records with the following columns:

- **User**
- **API** (e.g., `/qt/qrng/ints`, `/qt/qrng/bytes`)
- **Size (bytes)**: Indicates the amount of QRNG data consumed.
- **Created Date**: Timestamp of the QRNG request.

**Step 3**: Click on an API path to view details of the request.

![image-20250628-093728.png](https://cloud.quandela.com/webide/docs-assets/1364754542.png)

💡 **Notes:**

- QRNG API usage contributes to entity credit consumption. These transactions are also reflected in the **Credit Transaction** tab under **Entity Billing**, allowing for consolidated monitoring.

![image-20250628-094022.png](https://cloud.quandela.com/webide/docs-assets/1364754548.png)
