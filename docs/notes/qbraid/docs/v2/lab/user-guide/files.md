> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/files.md](https://docs.qbraid.com/v2/lab/user-guide/files.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 bc3f2a31ea4d78fc56336a1614fd05957b3569ffc0d91467fda10bf17f94f5bf.

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

# Files

> Open, create, rename, delete, and download files in the qBraid Lab file browser, and see how file sync differs on subscription and on-demand instances.

## File browser

The file browser and Files menu enable you to work with files and directories on your system. This includes opening, creating,
deleting, renaming, downloading, and copying files and directories. To open the file browser, click on the "Folder"
icon in the left sidebar (or use shortcut `Cmd+Shift+F`).

Navigate by double-clicking folders in the listing or clicking folders at the top of the directory listing. To open any file, double-click on its name, or drag the file into the main work area to create a new tab.

### Show hidden files

Hidden files are those whose names start with a "`.`" (e.g., `.bashrc`, `.gitignore`). These are hidden by default in the file browser to reduce clutter.

From the top-bar menu, click on **View**, and then select **Show Hidden Files** to toggle the visibility of hidden files in
the file browser.

<img src="/v2/lab/_static/hidden-files.png" alt="Show Hidden Files in the Lab View menu" width="95%" />

### Download files

To download a file, open the file browser, right click on the file, and select **Download** from the context menu.

<Note>
  If you can't launch Lab, you can still [download your files from the account
  dashboard](https://docs.qbraid.com/v2/account/usage#download-your-files) without starting a session.
</Note>

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/lab/_static/download-file.png" alt="Download action in the file context menu" width="95%" />
</div>

### Delete files and directories

To delete a file or directory, open the file browser, right-click on the item, and select **Delete** from the context menu.

You can also delete files and directories from the terminal using the `rm` command:

```bash
rm -rf [file_or_directory]
```

<Warning>
  qBraid Lab has no trash or recovery folder. Files deleted from the file browser or with `rm -rf` are removed immediately and cannot be restored. Double-check the item before confirming a deletion or running the command.
</Warning>

If you need to keep a recoverable copy, download the file first (see [Download files](#download-files)) or push it to a remote Git repository before deleting.

If you are deleting files to free up disk space, see [Disk Usage Management](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#disk-usage-management) for how to find large files and directories with `gdu` and how uninstalling unused environments can reclaim the most space.

### Download directories

The JupyterLab file browser does not support directory downloads. Use the terminal to zip a directory, then download the zip file.

First, open terminal in JupyterLab by opening a Launcher tab and selecting **Terminal** under the **Other** section.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/lab/_static/terminal.png" alt="Terminal launcher in JupyterLab" width="95%" />
</div>

Compress the directory with `zip`. Specify the output file name and directory path. The `-r` option includes subdirectories and their contents:

```bash
$ zip -r output_filename.zip /path/to/directory
```

Finally, download the zip file using the file browser. See [Download files](#download-files).

## File sync (subscription instances)

If your subscription Lab instance has been inactive for a few days, your files will be restored from cloud storage when you start a new session. A progress indicator appears above the file browser in the left sidebar while the sync is in progress.

<Note>
  Sync time depends on the size of your directory. Once the sync is complete, refresh
  the **Environments** sidebar to see all of your environments again.
</Note>

## Files on on-demand instances

On-demand instances (GPUs and high-spec CPUs) handle file persistence differently from subscription instances:

- On-demand instances do not sync files from cloud storage at launch. Each instance has its own disk.
- Use the **Files** tab to download files from cloud storage into an instance. Changes do not sync back to cloud storage.
- If the provider supports stopping, your disk and files remain available when you resume. Some instance types only support termination.
- Terminating permanently deletes the disk and all its files.

<Warning>
  Before terminating an on-demand instance, download any important files to your
  local machine or push them to a remote repository. See [On-Demand
  Instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances#file-persistence) for more
  details.
</Warning>
