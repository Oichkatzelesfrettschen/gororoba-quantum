# MCP Server

***

## Getting Started

To run the remote server, you need to paste the following code block into your client's configuration. The remote server URL is `https://www.kaggle.com/mcp`.

### Configuration Examples

#### Gemini CLI

```
 gemini mcp add --transport http kaggle https://www.kaggle.com/mcp
```

Alternatively, you can add the following to your `~/.gemini/settings.json` file:

```

 {
      "mcpServers": {
        "kaggle": {
          "httpUrl": "https://www.kaggle.com/mcp"
        }
      }
    }
```

#### Claude Desktop

```

{
  "mcpServers": {
     "kaggle": {
      "command": "npx",
      "args": [
          "mcp-remote",
          "https://www.kaggle.com/mcp"
      ]
    }
  }
}
```

#### VS Code (settings.json)

```

{
  "servers": {
     "kaggle": {
     "url": "https://www.kaggle.com/mcp",
     "type": "http"
		}
	},
}]
}
```

#### Windsurf

Add the following to your ~/.codeium/mcp\_config.json:

```


{
  "mcpServers": {
    "kaggle": {
      "serverUrl" : "https://www.kaggle.com/mcp"
    }
  }
}
```

***

## Authorization

Some resources, or endpoints require authorization. To unlock full access you can authorize using OAuth 2.0

#### Gemini CLI

Simply run the following command: `/mcp auth kaggle`

#### Other Clients/IDEs

For other clients that do not have a command to initiate auth discovery you can call the `authorize` tool

### Token Authentication

If your client is not OAuth 2.0 compliant, you can also use token authentication.

If you don't already have a token navigate to [Settings](/settings) &gt; Generate New Token &gt; "Copy". The token should begin with "KGAT"

#### Gemini CLI

```

"mcpServers": {
    "kaggle": {
      "transport": "http",
      "httpUrl": "https://www.kaggle.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  },
```

#### Claude Desktop

```

    {
  "mcpServers": {
     "kaggle": {
      "command": "npx",
      "args": [
          "mcp-remote",
          "https://www.kaggle.com/mcp",
          "--header",
          "Authorization: Bearer YOUR_TOKEN"
      ]
    }
  }
}
```

#### Vscode

```

"servers": {
  "kaggle": {
    "url": "https://www.kaggle.com/mcp",
    "type": "http",
      "headers" : {
      "authorization": "Bearer YOUR_TOKEN"
		}
	}
}
```

#### Windsurf

```

    {
  "mcpServers": {
    "kaggle": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://www.kaggle.com/mcp",
        "--header",
        "Authorization: Bearer YOUR_TOKEN"
      ]
    }
  }
}
```

***

## Tool Definitions

<details><summary><h3>Notebooks</h3></summary>
<div class="tool-header">
  <h5>○ cancel_notebook_session</h5>
  <p>Cancel a notebook session.</p>
</div>
<h5>Request: <code>ApiCancelKernelSessionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>kernel_session_id</td><td><code>int32</code></td><td>The ID of the kernel session to cancel.</td></tr>
</tbody></table>
<h5>Response: <code>ApiCancelKernelSessionResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>error_message</td><td><code>string</code></td><td>Optional error message if the cancellation failed.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ create_notebook_session</h5>
  <p>Create a new notebook session.</p>
</div>
<h5>Request: <code>ApiCreateKernelSessionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>slug</td><td><code>string</code></td><td>The full slug of the kernel to create an interactive session for, in the format `{username}/{kernel-slug}`.</td></tr>
  <tr><td>language</td><td><code>string</code></td><td>The language that the kernel is written in. One of "python", "r" and "rmarkdown".</td></tr>
  <tr><td>kernel_type</td><td><code>string</code></td><td>The type of kernel. Options are 'notebook' or 'script'.</td></tr>
  <tr><td>docker_image</td><td><code>string</code></td><td>Which docker image to run with.</td></tr>
  <tr><td>machine_shape</td><td><code>string</code></td><td>The machine shape to use for this session.</td></tr>
  <tr><td>enable_internet</td><td><code>bool</code></td><td>Whether or not the kernel should be able to access the internet in this session.</td></tr>
</tbody></table>
<h5>Response: <code>Operation</code></h5>
<p>This method returns a long-running operation.</p>

<div class="tool-header">
  <h5>○ download_notebook_output</h5>
  <p>Download the output of a notebook.</p>
</div>
<h5>Request: <code>ApiDownloadKernelOutputRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
  <tr><td>file_path</td><td><code>string</code></td><td>Relative path to a specific file inside the databundle.</td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td>The version number of the kernel.</td></tr>
</tbody></table>
<h5>Response: <code>HttpRedirect</code></h5>
<p>Returns a URL to download the output.</p>

<div class="tool-header">
  <h5>○ download_notebook_output_zip</h5>
  <p>Download the zipped output of a notebook.</p>
</div>
<h5>Request: <code>ApiDownloadKernelOutputZipRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>kernel_session_id</td><td><code>int32</code></td><td>The ID of the kernel session to download the output from.</td></tr>
</tbody></table>
<h5>Response: <code>FileDownload</code></h5>
<p>Returns a file download object.</p>

<div class="tool-header">
  <h5>○ get_notebook_info</h5>
  <p>Get information about a notebook.</p>
</div>
<h5>Request: <code>ApiGetKernelRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>user_name</td><td><code>string</code></td><td>The username of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
</tbody></table>
<h5>Response: <code>ApiGetKernelResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
    <tr>
    <td>metadata</td>
    <td>
      <details>
        <summary>ApiKernelMetadata</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>author</td><td><code>string</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>last_run_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>language</td><td><code>string</code></td></tr>
          <tr><td>kernel_type</td><td><code>string</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>enable_gpu</td><td><code>bool</code></td></tr>
          <tr><td>enable_tpu</td><td><code>bool</code></td></tr>
          <tr><td>enable_internet</td><td><code>bool</code></td></tr>
          <tr><td>category_ids</td><td><code>repeated string</code></td></tr>
          <tr><td>dataset_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>kernel_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>competition_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>model_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>total_votes</td><td><code>int32</code></td></tr>
          <tr><td>current_version_number</td><td><code>int32</code></td></tr>
          <tr><td>docker_image</td><td><code>string</code></td></tr>
          <tr><td>machine_shape</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The metadata of the kernel.</td>
  </tr>
    <tr>
    <td>blob</td>
    <td>
      <details>
        <summary>ApiKernelBlob</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>source</td><td><code>string</code></td></tr>
          <tr><td>language</td><td><code>string</code></td></tr>
          <tr><td>kernel_type</td><td><code>string</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The content of the kernel.</td>
  </tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_notebook_session_status</h5>
  <p>Get the status of a notebook session.</p>
</div>
<h5>Request: <code>ApiGetKernelSessionStatusRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>user_name</td><td><code>string</code></td><td>The username of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
</tbody></table>
<h5>Response: <code>ApiGetKernelSessionStatusResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>status</td><td><code>KernelWorkerStatus</code></td><td>The status of the session. Possible values: <code>QUEUED</code>, <code>RUNNING</code>, <code>COMPLETE</code>, <code>ERROR</code>, <code>CANCEL_REQUESTED</code>, <code>CANCEL_ACKNOWLEDGED</code>, <code>NEW_SCRIPT</code>.</td></tr>
  <tr><td>failure_message</td><td><code>string</code></td><td>Optional failure message.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_notebook_files</h5>
  <p>List the files in a notebook.</p>
</div>
<h5>Request: <code>ApiListKernelFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>user_name</td><td><code>string</code></td><td>The username of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListKernelFilesResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
    <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiListKernelFilesItem</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>size</td><td><code>int64</code></td></tr>
          <tr><td>creation_date</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The list of files.</td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td>The next page token.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_notebook_session_output</h5>
  <p>List the output files of a notebook session.</p>
</div>
<h5>Request: <code>ApiListKernelSessionOutputRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>user_name</td><td><code>string</code></td><td>The username of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListKernelSessionOutputResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
    <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiKernelSessionOutputFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>file_name</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The list of output files.</td>
  </tr>
  <tr><td>log</td><td><code>string</code></td><td>The session log.</td></tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td>The next page token.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ save_notebook</h5>
  <p>Save a notebook and run it from top to bottom.</p>
</div>
<h5>Request: <code>ApiSaveKernelRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td>The kernel's unique ID number.</td></tr>
  <tr><td>slug</td><td><code>string</code></td><td>The full slug of the kernel to push to.</td></tr>
  <tr><td>new_title</td><td><code>string</code></td><td>The title to be set on the kernel.</td></tr>
  <tr><td>text</td><td><code>string</code></td><td>The kernel's source code.</td></tr>
  <tr><td>language</td><td><code>string</code></td><td>The language that the kernel is written in. One of "python", "r" and "rmarkdown".</td></tr>
  <tr><td>kernel_type</td><td><code>string</code></td><td>The type of kernel. Cannot be changed once the kernel has been created.</td></tr>
  <tr><td>dataset_data_sources</td><td><code>repeated string</code></td><td>A list of dataset data sources that the kernel should use.</td></tr>
  <tr><td>kernel_data_sources</td><td><code>repeated string</code></td><td>A list of kernel data sources that the kernel should use.</td></tr>
  <tr><td>competition_data_sources</td><td><code>repeated string</code></td><td>A list of competition data sources that the kernel should use.</td></tr>
  <tr><td>category_ids</td><td><code>repeated string</code></td><td>A list of tag IDs to associated with the kernel.</td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td>Whether or not the kernel should be private.</td></tr>
  <tr><td>enable_gpu</td><td><code>bool</code></td><td>Whether or not the kernel should run on a GPU. DEPRECATED: use `machine_shape` instead.</td></tr>
  <tr><td>enable_tpu</td><td><code>bool</code></td><td>Whether or not the kernel should run on a TPU. DEPRECATED: use `machine_shape` instead.</td></tr>
  <tr><td>enable_internet</td><td><code>bool</code></td><td>Whether or not the kernel should be able to access the internet.</td></tr>
  <tr><td>docker_image_pinning_type</td><td><code>string</code></td><td>Which docker image to use for executing new versions going forward.</td></tr>
  <tr><td>model_data_sources</td><td><code>repeated string</code></td><td>A list of model data sources that the kernel should use.</td></tr>
</tbody></table>
<h5>Response: <code>ApiSaveKernelResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>ref</td><td><code>string</code></td><td>The reference of the kernel.</td></tr>
  <tr><td>url</td><td><code>string</code></td><td>The URL of the kernel.</td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td>The new version number of the kernel.</td></tr>
  <tr><td>error</td><td><code>string</code></td><td>An error message if the save failed.</td></tr>
  <tr><td>invalid_tags</td><td><code>repeated string</code></td><td>A list of invalid tags.</td></tr>
  <tr><td>invalid_dataset_sources</td><td><code>repeated string</code></td><td>A list of invalid dataset sources.</td></tr>
  <tr><td>invalid_competition_sources</td><td><code>repeated string</code></td><td>A list of invalid competition sources.</td></tr>
  <tr><td>invalid_kernel_sources</td><td><code>repeated string</code></td><td>A list of invalid kernel sources.</td></tr>
  <tr><td>invalid_model_sources</td><td><code>repeated string</code></td><td>A list of invalid model sources.</td></tr>
  <tr><td>kernel_id</td><td><code>int32</code></td><td>The ID of the kernel.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ search_notebooks</h5>
  <p>Search for notebooks.</p>
</div>
<h5>Request: <code>ApiListKernelsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition</td><td><code>string</code></td><td>Display kernels using the specified competition.</td></tr>
  <tr><td>dataset</td><td><code>string</code></td><td>Display kernels using the specified dataset.</td></tr>
  <tr><td>parent_kernel</td><td><code>string</code></td><td>Display kernels that have forked the specified kernel.</td></tr>
  <tr><td>group</td><td><code>KernelsListViewType</code></td><td>Display your kernels, collaborated, bookmarked or upvoted kernels. Possible values: <code>PROFILE</code>, <code>UPVOTED</code>, <code>EVERYONE</code>, <code>COLLABORATION</code>, <code>FORK</code>, <code>BOOKMARKED</code>, <code>RECENTLY_VIEWED</code>, <code>PUBLIC_AND_USERS_PRIVATE</code>.</td></tr>
  <tr><td>kernel_type</td><td><code>string</code></td><td>Display kernels of a specific type.</td></tr>
  <tr><td>language</td><td><code>string</code></td><td>Display kernels in a specific language. One of "all", "python", "r", "sqlite" and "julia".</td></tr>
  <tr><td>output_type</td><td><code>string</code></td><td>Display kernels with a specific output type. One of "all", "visualization" and "notebook".</td></tr>
  <tr><td>search</td><td><code>string</code></td><td>Display kernels matching the specified search terms.</td></tr>
  <tr><td>sort_by</td><td><code>KernelsListSortType</code></td><td>Sort the results. Possible values: <code>HOTNESS</code>, <code>COMMENT_COUNT</code>, <code>DATE_CREATED</code>, <code>DATE_RUN</code>, RELEVANCE, <code>SCORE_ASCENDING</code>, <code>SCORE_DESCENDING</code>, <code>VIEW_COUNT</code>, <code>VOTE_COUNT</code>.</td></tr>
  <tr><td>user</td><td><code>string</code></td><td>Display kernels by a particular user or group.</td></tr>
  <tr><td>page</td><td><code>int32</code></td><td>Page number.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListKernelsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
    <tr>
    <td>kernels</td>
    <td>
      <details>
        <summary>repeated ApiKernelMetadata</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>author</td><td><code>string</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>last_run_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>language</td><td><code>string</code></td></tr>
          <tr><td>kernel_type</td><td><code>string</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>enable_gpu</td><td><code>bool</code></td></tr>
          <tr><td>enable_tpu</td><td><code>bool</code></td></tr>
          <tr><td>enable_internet</td><td><code>bool</code></td></tr>
          <tr><td>category_ids</td><td><code>repeated string</code></td></tr>
          <tr><td>dataset_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>kernel_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>competition_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>model_data_sources</td><td><code>repeated string</code></td></tr>
          <tr><td>total_votes</td><td><code>int32</code></td></tr>
          <tr><td>current_version_number</td><td><code>int32</code></td></tr>
          <tr><td>docker_image</td><td><code>string</code></td></tr>
          <tr><td>machine_shape</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>List of kernels.</td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td>Next page token.</td></tr>
</tbody></table>

</details>

<details><summary><h3>Benchmarks</h3></summary>
<div class="tool-header">
  <h5>○ create_benchmark_task_from_prompt</h5>
  <p>Create a new benchmark task from a prompt.</p>
</div>
<h5>Request: <code>CreateBenchmarkTaskFromPromptRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>prompt</td><td><code>string</code></td><td>A natural language prompt describing the benchmark task to be created.</td></tr>
</tbody></table>
<h5>Response: <code>CreateBenchmarkTaskFromPromptResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>task</td>
    <td>
      <details>
        <summary>BenchmarkTask</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>type</td><td>BenchmarkTaskType</td><td>The type of the benchmark task. Possible values: BENCHMARK_TASK_TYPE_UNSPECIFIED, BENCHMARK_TASK_TYPE_BENCHMARK.</td></tr>
          <tr><td>version</td>
    <td>
      <details>
        <summary>BenchmarkTaskVersion</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>task_id</td><td><code>int32</code></td></tr>
          <tr><td>version_number</td><td><code>int32</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>display_type</td><td>BenchmarkLeaderboardDisplayType</td></tr>
          <tr><td>definition</td><td><code>string</code></td></tr>
          <tr><td>source_kernel_session_id</td><td><code>int32</code></td></tr>
          <tr><td>aggregation_type</td><td>BenchmarkTaskVersionAggregationType</td></tr>
          <tr><td>child_task_versions</td><td><code>repeated BenchmarkTaskVersion</code></td></tr>
          <tr><td>parent_task_version_ids</td><td><code>repeated int32</code></td></tr>
          <tr><td>is_public</td><td><code>bool</code></td></tr>
          <tr><td>owner_user</td><td>kaggle.users.UserAvatar</td></tr>
          <tr><td>type</td><td>BenchmarkTaskType</td></tr>
          <tr><td>permissions</td><td>Permissions</td></tr>
        </tbody></table>
      </details>
    </td>
</tr>
          <tr><td>update_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>definition_type</td><td>BenchmarkTaskDefinitionType</td><td>The definition type of the benchmark task. Possible values: BENCHMARK_TASK_DEFINITION_TYPE_UNSPECIFIED, NOTEBOOK, PROMPTFOO.</td></tr>
          <tr><td>owner_user_id</td><td><code>int32</code></td></tr>
          <tr><td>owner_user</td><td>kaggle.users.UserAvatar</td></tr>
          <tr><td>source_kernel_id</td><td><code>int32</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>vote_count</td><td><code>int32</code></td></tr>
          <tr><td>has_up_voted</td><td><code>bool</code></td></tr>
          <tr><td>forum_id</td><td><code>int32</code></td></tr>
          <tr><td>is_public</td><td><code>bool</code></td></tr>
          <tr><td>permissions</td><td>Permissions</td></tr>
          <tr><td>can_administer</td><td><code>bool</code></td></tr>
          <tr><td>categories</td>
    <td>
      <details>
        <summary>kaggle.tags.TagList</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr>
            <td>tags</td>
            <td>
              <details>
                <summary>repeated kaggle.tags.Tag</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>type</td><td>kaggle.tags.TagType</td></tr>
        </tbody></table>
      </details>
    </td>
</tr>
        </tbody></table>
      </details>
    </td>
    <td>The benchmark task that was created.</td>
  </tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_benchmark_leaderboard</h5>
  <p>Get the leaderboard for a benchmark.</p>
</div>
<h5>Request: <code>ApiGetBenchmarkLeaderboardRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the user or organization that owns the benchmark.</td></tr>
  <tr><td>benchmark_slug</td><td><code>string</code></td><td>The slug of the benchmark.</td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td>The version number of the benchmark to get the leaderboard for. If not provided, the latest version is used.</td></tr>
</tbody></table>
<h5>Response: <code>ApiBenchmarkLeaderboard</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>rows</td>
    <td>
      <details>
        <summary>repeated LeaderboardRow</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>model_version_name</td><td><code>string</code></td></tr>
          <tr><td>model_version_slug</td><td><code>string</code></td></tr>
          <tr>
            <td>task_results</td>
            <td>
              <details>
                <summary>repeated TaskResult</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>task_id</td><td><code>int32</code></td></tr>
                  <tr><td>score</td><td>double</td></tr>
                  <tr><td>status</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td>The rows of the leaderboard.</td>
  </tr>
</tbody></table>
</details>

<details><summary><h3>Competitions</h3></summary>
<div class="tool-header">
  <h5>○ create_code_competition_submission</h5>
  <p>Submit a kernel to a competition.</p>
</div>
<h5>Request: <code>ApiCreateCodeSubmissionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
  <tr><td>kernel_owner</td><td><code>string</code></td><td>The username of the owner of the kernel.</td></tr>
  <tr><td>kernel_slug</td><td><code>string</code></td><td>The slug of the kernel.</td></tr>
  <tr><td>kernel_version</td><td><code>int32</code></td><td>The version number of the kernel.</td></tr>
  <tr><td>file_name</td><td><code>string</code></td><td>The name of the file to submit.</td></tr>
  <tr><td>submission_description</td><td><code>string</code></td><td>A description for the submission.</td></tr>
</tbody></table>
<h5>Response: <code>ApiCreateCodeSubmissionResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>message</td><td><code>string</code></td><td>An error message if the submission failed.</td></tr>
  <tr><td>ref</td><td><code>int32</code></td><td>The ID of the submission.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ submit_to_competition</h5>
  <p>Submit a new competition submission.</p>
</div>
<h5>Request: <code>ApiCreateSubmissionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>blob_file_tokens</td><td><code>string</code></td><td>Token identifying location of uploaded submission file.</td></tr>
  <tr><td>submission_description</td><td><code>string</code></td><td>Description of competition submission.</td></tr>
</tbody></table>
<h5>Response: <code>ApiCreateSubmissionResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>message</td><td><code>string</code></td><td>Error message from InvalidArgument.</td></tr>
  <tr><td>ref</td><td><code>int32</code></td><td>The ID of the submission.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ download_competition_data_file</h5>
  <p>Download a single data file for a competition.</p>
</div>
<h5>Request: <code>ApiDownloadDataFileRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>file_name</td><td><code>string</code></td><td>Name of the file to download.</td></tr>
</tbody></table>
<h5>Response: <code>HttpRedirect</code></h5>
<p>Returns a URL to download the file.</p>

<div class="tool-header">
  <h5>○ download_competition_data_files</h5>
  <p>Download all data files for a competition.</p>
</div>
<h5>Request: <code>ApiDownloadDataFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
</tbody></table>
<h5>Response: <code>HttpRedirect</code></h5>
<p>Returns a URL to download the files.</p>

<div class="tool-header">
  <h5>○ download_competition_leaderboard</h5>
  <p>Download the leaderboard for a competition.</p>
</div>
<h5>Request: <code>ApiDownloadLeaderboardRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
</tbody></table>
<h5>Response: <code>FileDownload</code></h5>
<p>Returns a file download object.</p>

<div class="tool-header">
  <h5>○ get_competition</h5>
  <p>Get competition metadata.</p>
</div>
<h5>Request: <code>ApiGetCompetitionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
</tbody></table>
<h5>Response: <code>ApiCompetition</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td></td></tr>
  <tr><td>ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>title</td><td><code>string</code></td><td></td></tr>
  <tr><td>url</td><td><code>string</code></td><td></td></tr>
  <tr><td>description</td><td><code>string</code></td><td></td></tr>
  <tr><td>organization_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>organization_ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>category</td><td><code>string</code></td><td></td></tr>
  <tr><td>reward</td><td><code>string</code></td><td></td></tr>
  <tr>
    <td>tags</td>
    <td>
      <details>
        <summary>repeated ApiCategory</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>full_path</td><td><code>string</code></td></tr>
          <tr><td>competition_count</td><td><code>int32</code></td></tr>
          <tr><td>dataset_count</td><td><code>int32</code></td></tr>
          <tr><td>script_count</td><td><code>int32</code></td></tr>
          <tr><td>total_count</td><td><code>int32</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>deadline</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>kernel_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>team_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>user_has_entered</td><td><code>bool</code></td><td></td></tr>
  <tr><td>user_rank</td><td><code>int32</code></td><td></td></tr>
  <tr><td>merger_deadline</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>new_entrant_deadline</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>enabled_date</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>max_daily_submissions</td><td><code>int32</code></td><td></td></tr>
  <tr><td>max_team_size</td><td><code>int32</code></td><td></td></tr>
  <tr><td>evaluation_metric</td><td><code>string</code></td><td></td></tr>
  <tr><td>awards_points</td><td><code>bool</code></td><td></td></tr>
  <tr><td>is_kernels_submissions_only</td><td><code>bool</code></td><td></td></tr>
  <tr><td>submissions_disabled</td><td><code>bool</code></td><td></td></tr>
  <tr><td>thumbnail_image_url</td><td><code>string</code></td><td></td></tr>
  <tr><td>host_name</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_competition_data_files_summary</h5>
  <p>Get a summary of the data files for a competition.</p>
</div>
<h5>Request: <code>ApiGetCompetitionDataFilesSummaryRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
</tbody></table>
<h5>Response: <code>ApiFilesSummary</code></h5>

<div class="tool-header">
  <h5>○ get_competition_leaderboard</h5>
  <p>Get the leaderboard for a competition.</p>
</div>
<h5>Request: <code>ApiGetLeaderboardRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>override_public</td><td><code>bool</code></td><td>By default we return the private leaderboard if it's available, otherwise the public LB. This flag lets you override to get public even if private is available.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token.</td></tr>
</tbody></table>
<h5>Response: <code>ApiGetLeaderboardResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>submissions</td>
    <td>
      <details>
        <summary>repeated ApiLeaderboardSubmission</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>team_id</td><td><code>int32</code></td></tr>
          <tr><td>team_name</td><td><code>string</code></td></tr>
          <tr><td>submission_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>score</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_competition_submission</h5>
  <p>Get metadata about a competition submission.</p>
</div>
<h5>Request: <code>ApiGetSubmissionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>ref</td><td><code>int32</code></td><td>SubmissionId.</td></tr>
</tbody></table>
<h5>Response: <code>ApiSubmission</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>ref</td><td><code>int32</code></td><td></td></tr>
  <tr><td>total_bytes</td><td><code>int64</code></td><td></td></tr>
  <tr><td>date</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>description</td><td><code>string</code></td><td></td></tr>
  <tr><td>error_description</td><td><code>string</code></td><td></td></tr>
  <tr><td>file_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>public_score</td><td><code>string</code></td><td></td></tr>
  <tr><td>private_score</td><td><code>string</code></td><td></td></tr>
  <tr><td>status</td><td><code>SubmissionStatus</code></td><td>Possible values: PUBLIC, PRIVATE, CANCELLED, ERROR, STUCK, COMPLETE, NONE.</td></tr>
  <tr><td>submitted_by</td><td><code>string</code></td><td></td></tr>
  <tr><td>submitted_by_ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>team_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>url</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ search_competitions</h5>
  <p>Search for competitions.</p>
</div>
<h5>Request: <code>ApiListCompetitionsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>group</td><td>CompetitionListTab</td><td>Filter competitions by a particular group. Possible values: <code>COMPETITION_LIST_TAB_GENERAL</code>, <code>COMPETITION_LIST_TAB_ENTERED</code>, <code>COMPETITION_LIST_TAB_COMMUNITY</code>, <code>COMPETITION_LIST_TAB_HOSTED</code>, <code>COMPETITION_LIST_TAB_UNLAUNCHED</code>, <code>COMPETITION_LIST_TAB_UNLAUNCHED_COMMUNITY</code>, <code>COMPETITION_LIST_TAB_EVERYTHING</code>.</td></tr>
  <tr><td>category</td><td>HostSegment</td><td>Filter competitions by a particular category. Possible values: <code>HOST_SEGMENT_UNSPECIFIED, <code>HOST_SEGMENT_FEATURED</code>, <code>HOST_SEGMENT_GETTING_STARTED</code>, <code>HOST_SEGMENT_MASTERS</code>, <code>HOST_SEGMENT_PLAYGROUND</code>, <code>HOST_SEGMENT_RECRUITMENT</code>, <code>HOST_SEGMENT_RESEARCH</code>, <code>HOST_SEGMENT_COMMUNITY</code>, <code>HOST_SEGMENT_ANALYTICS</code>.</code></td></tr>
  <tr><td>sort_by</td><td>CompetitionSortBy</td><td>Sort the results. Possible values: <code>COMPETITION_SORT_BY_GROUPED</code>, <code>COMPETITION_SORT_BY_BEST</code>, <code>COMPETITION_SORT_BY_PRIZE</code>, <code>COMPETITION_SORT_BY_EARLIEST_DEADLINE</code>, <code>COMPETITION_SORT_BY_LATEST_DEADLINE</code>, <code>COMPETITION_SORT_BY_NUMBER_OF_TEAMS</code>, <code>COMPETITION_SORT_BY_RELEVANCE</code>, <code>COMPETITION_SORT_BY_RECENTLY_CREATED</code>.</td></tr>
  <tr><td>search</td><td><code>string</code></td><td>Filter competitions by search terms.</td></tr>
  <tr><td>page</td><td><code>int32</code></td><td>Page number.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListCompetitionsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>competitions</td>
    <td>
      <details>
        <summary>repeated ApiCompetition</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>organization_name</td><td><code>string</code></td></tr>
          <tr><td>organization_ref</td><td><code>string</code></td></tr>
          <tr><td>category</td><td><code>string</code></td></tr>
          <tr><td>reward</td><td><code>string</code></td></tr>
          <tr>
            <td>tags</td>
            <td>
              <details>
                <summary>repeated ApiCategory</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>ref</td><td><code>string</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>full_path</td><td><code>string</code></td></tr>
                  <tr><td>competition_count</td><td><code>int32</code></td></tr>
                  <tr><td>dataset_count</td><td><code>int32</code></td></tr>
                  <tr><td>script_count</td><td><code>int32</code></td></tr>
                  <tr><td>total_count</td><td><code>int32</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>deadline</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>kernel_count</td><td><code>int32</code></td></tr>
          <tr><td>team_count</td><td><code>int32</code></td></tr>
          <tr><td>user_has_entered</td><td><code>bool</code></td></tr>
          <tr><td>user_rank</td><td><code>int32</code></td></tr>
          <tr><td>merger_deadline</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>new_entrant_deadline</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>enabled_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>max_daily_submissions</td><td><code>int32</code></td></tr>
          <tr><td>max_team_size</td><td><code>int32</code></td></tr>
          <tr><td>evaluation_metric</td><td><code>string</code></td></tr>
          <tr><td>awards_points</td><td><code>bool</code></td></tr>
          <tr><td>is_kernels_submissions_only</td><td><code>bool</code></td></tr>
          <tr><td>submissions_disabled</td><td><code>bool</code></td></tr>
          <tr><td>thumbnail_image_url</td><td><code>string</code></td></tr>
          <tr><td>host_name</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_competition_data_files</h5>
  <p>List the data files for a competition.</p>
</div>
<h5>Request: <code>ApiListDataFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListDataFilesResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiDataFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
  <tr><td>children_fetch_time_ms</td><td><code>int32</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_competition_data_tree_files</h5>
  <p>List the data files by directory for a competition.</p>
</div>
<h5>Request: <code>ApiListDataTreeFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>path</td><td><code>string</code></td><td>The path of the directory to list files from.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token.</td></tr>
</tbody></table>
<h5>Response: <code>ApiDirectoryContent</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>directories</td>
    <td>
      <details>
        <summary>repeated ApiDirectory</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>relative_url</td><td><code>string</code></td></tr>
          <tr><td>total_directories</td><td><code>int64</code></td></tr>
          <tr><td>total_files</td><td><code>int64</code></td></tr>
          <tr><td>total_children</td><td><code>int64</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr><td>relative_url</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>total_children</td><td><code>int64</code></td><td></td></tr>
  <tr><td>total_directories</td><td><code>int64</code></td><td></td></tr>
  <tr><td>total_files</td><td><code>int64</code></td><td></td></tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ search_competition_submissions</h5>
  <p>Search for competition submissions.</p>
</div>
<h5>Request: <code>ApiListSubmissionsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>sort_by</td><td><code>SubmissionSortBy</code></td><td>Possible values: <code>SUBMISSION_SORT_BY_DATE</code>, <code>SUBMISSION_SORT_BY_NAME</code>, <code>SUBMISSION_SORT_BY_PRIVATE_SCORE</code>, <code>SUBMISSION_SORT_BY_PUBLIC_SCORE</code>.</td></tr>
  <tr><td>group</td><td><code>SubmissionGroup</code></td><td>Possible values: <code>SUBMISSION_GROUP_ALL</code>, <code>SUBMISSION_GROUP_SUCCESSFUL</code>, <code>SUBMISSION_GROUP_SELECTED</code>.</td></tr>
  <tr><td>page</td><td><code>int32</code></td><td>Page number.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size, i.e., maximum number of results to return.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListSubmissionsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>submissions</td>
    <td>
      <details>
        <summary>repeated ApiSubmission</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>int32</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr><td>date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>error_description</td><td><code>string</code></td></tr>
          <tr><td>file_name</td><td><code>string</code></td></tr>
          <tr><td>public_score</td><td><code>string</code></td></tr>
          <tr><td>private_score</td><td><code>string</code></td></tr>
          <tr><td>status</td><td>SubmissionStatus</td></tr>
          <tr><td>submitted_by</td><td><code>string</code></td></tr>
          <tr><td>submitted_by_ref</td><td><code>string</code></td></tr>
          <tr><td>team_name</td><td><code>string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ start_competition_submission_upload</h5>
  <p>Get a link to upload a competition submission file.</p>
</div>
<h5>Request: <code>ApiStartSubmissionUploadRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>Competition name.</td></tr>
  <tr><td>content_length</td><td><code>int64</code></td><td>The length of the file in bytes.</td></tr>
  <tr><td>last_modified_epoch_seconds</td><td><code>int64</code></td><td>The last modified time of the file in epoch seconds.</td></tr>
  <tr><td>file_name</td><td><code>string</code></td><td>Comes from form upload.</td></tr>
</tbody></table>
<h5>Response: <code>ApiStartSubmissionUploadResponse</code></h5>
</details>

<details><summary><h3>Datasets</h3></summary>
<div class="tool-header">
  <h5>○ create_dataset</h5>
  <p>Create a new dataset.</p>
</div>
<h5>Request: <code>ApiCreateDatasetRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td>The ID of the dataset.</td></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>title</td><td><code>string</code></td><td>The title of the dataset.</td></tr>
  <tr><td>license_name</td><td><code>string</code></td><td>The name of the license.</td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td>Whether the dataset is private.</td></tr>
  <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiDatasetNewFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>file_name</td><td><code>string</code></td></tr>
          <tr><td>content</td><td>bytes</td></tr>
          <tr><td>content_type</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The files to upload to the dataset.</td>
  </tr>
  <tr><td>subtitle</td><td><code>string</code></td><td>The subtitle of the dataset.</td></tr>
  <tr><td>description</td><td><code>string</code></td><td>The description of the dataset.</td></tr>
  <tr><td>category_ids</td><td><code>repeated string</code></td><td>The category IDs to associate with the dataset.</td></tr>
  <tr>
    <td>directories</td>
    <td>
      <details>
        <summary>repeated ApiUploadDirectoryInfo</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>path</td><td><code>string</code></td></tr>
          <tr><td>files</td><td>repeated ApiDatasetNewFile</td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The directories to upload to the dataset.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiCreateDatasetResponse</code></h5>

<div class="tool-header">
  <h5>○ create_dataset_version</h5>
  <p>Create a new version of a dataset. Identified by the owner and dataset slugs.</p>
</div>
<h5>Request: <code>ApiCreateDatasetVersionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>body</td>
    <td>
      <details>
        <summary>ApiCreateDatasetVersionRequestBody</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>version_notes</td><td><code>string</code></td></tr>
          <tr><td>delete_old_versions</td><td><code>bool</code></td></tr>
          <tr>
            <td>files</td>
            <td>
              <details>
                <summary>repeated ApiDatasetNewFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>file_name</td><td><code>string</code></td></tr>
                  <tr><td>content</td><td>bytes</td></tr>
                  <tr><td>content_type</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>category_ids</td><td><code>repeated string</code></td></tr>
          <tr>
            <td>directories</td>
            <td>
              <details>
                <summary>repeated kaggle.datasets.ApiUploadDirectoryInfo</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>path</td><td><code>string</code></td></tr>
                  <tr><td>files</td><td>repeated ApiDatasetNewFile</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td>The request body.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiCreateDatasetResponse</code></h5>

<div class="tool-header">
  <h5>○ create_dataset_version_by_id</h5>
  <p>Create a new version of a dataset. Identified by the dataset id.</p>
</div>
<h5>Request: <code>ApiCreateDatasetVersionByIdRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td>The ID of the dataset.</td></tr>
  <tr><td>body</td>
    <td>
      <details>
        <summary>ApiCreateDatasetVersionRequestBody</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>version_notes</td><td><code>string</code></td></tr>
          <tr><td>delete_old_versions</td><td><code>bool</code></td></tr>
          <tr>
            <td>files</td>
            <td>
              <details>
                <summary>repeated ApiDatasetNewFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>file_name</td><td><code>string</code></td></tr>
                  <tr><td>content</td><td>bytes</td></tr>
                  <tr><td>content_type</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>category_ids</td><td><code>repeated string</code></td></tr>
          <tr>
            <td>directories</td>
            <td>
              <details>
                <summary>repeated kaggle.datasets.ApiUploadDirectoryInfo</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>path</td><td><code>string</code></td></tr>
                  <tr><td>files</td><td>repeated ApiDatasetNewFile</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td>The request body.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiCreateDatasetResponse</code></h5>

<div class="tool-header">
  <h5>○ download_dataset</h5>
  <p>Download a dataset.</p>
</div>
<h5>Request: <code>ApiDownloadDatasetRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>file_name</td><td><code>string</code></td><td>The name of the file to download.</td></tr>
  <tr><td>dataset_version_number</td><td><code>int32</code></td><td>The version number of the dataset.</td></tr>
  <tr><td>raw</td><td><code>bool</code></td><td>Whether to download the raw version of the dataset.</td></tr>
  <tr><td>hash_link</td><td><code>string</code></td><td>A hash link to the dataset.</td></tr>
</tbody></table>
<h5>Response: <code>HttpRedirect</code></h5>
<p>Returns a URL to download the dataset.</p>

<div class="tool-header">
  <h5>○ get_dataset_info</h5>
  <p>Get information about a dataset.</p>
</div>
<h5>Request: <code>ApiGetDatasetRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
</tbody></table>
<h5>Response: <code>ApiDataset</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td></td></tr>
  <tr><td>ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>subtitle</td><td><code>string</code></td><td></td></tr>
  <tr><td>creator_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>creator_url</td><td><code>string</code></td><td></td></tr>
  <tr><td>total_bytes</td><td><code>int64</code></td><td></td></tr>
  <tr><td>url</td><td><code>string</code></td><td></td></tr>
  <tr><td>last_updated</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>download_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td></td></tr>
  <tr><td>is_featured</td><td><code>bool</code></td><td></td></tr>
  <tr><td>license_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>description</td><td><code>string</code></td><td></td></tr>
  <tr><td>owner_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>owner_ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>kernel_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>title</td><td><code>string</code></td><td></td></tr>
  <tr><td>topic_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>view_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>vote_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>current_version_number</td><td><code>int32</code></td><td></td></tr>
  <tr><td>usability_rating</td><td>float</td><td></td></tr>
  <tr>
    <td>tags</td>
    <td>
      <details>
        <summary>repeated ApiCategory</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>full_path</td><td><code>string</code></td></tr>
          <tr><td>competition_count</td><td><code>int32</code></td></tr>
          <tr><td>dataset_count</td><td><code>int32</code></td></tr>
          <tr><td>script_count</td><td><code>int32</code></td></tr>
          <tr><td>total_count</td><td><code>int32</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiDatasetFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>dataset_ref</td><td><code>string</code></td></tr>
          <tr><td>owner_ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>file_type</td><td><code>string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr>
            <td>columns</td>
            <td>
              <details>
                <summary>repeated ApiDatasetColumn</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>order</td><td><code>int32</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>type</td><td><code>string</code></td></tr>
                  <tr><td>original_type</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr>
    <td>versions</td>
    <td>
      <details>
        <summary>repeated ApiDatasetVersion</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>version_number</td><td><code>int32</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>creator_name</td><td><code>string</code></td></tr>
          <tr><td>creator_ref</td><td><code>string</code></td></tr>
          <tr><td>version_notes</td><td><code>string</code></td></tr>
          <tr><td>status</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>thumbnail_image_url</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_dataset_files_summary</h5>
  <p>Get a summary of the data files in a dataset.</p>
</div>
<h5>Request: <code>ApiGetDatasetFilesSummaryRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>dataset_version_number</td><td><code>int32</code></td><td>The version number of the dataset.</td></tr>
</tbody></table>
<h5>Response: <code>ApiFilesSummary</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>file_summary_info</td>
    <td>
      <details>
        <summary>ApiFileSummaryInfo</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>total_file_count</td><td><code>int64</code></td></tr>
          <tr>
            <td>file_types</td>
            <td>
              <details>
                <summary>repeated ApiFileExtensionSummaryInfo</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>extension</td><td><code>string</code></td></tr>
                  <tr><td>file_count</td><td><code>int64</code></td></tr>
                  <tr><td>total_size</td><td><code>int64</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr>
    <td>column_summary_info</td>
    <td>
      <details>
        <summary>ApiColumnSummaryInfo</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>total_column_count</td><td><code>int64</code></td></tr>
          <tr>
            <td>column_types</td>
            <td>
              <details>
                <summary>repeated ApiColumnTypeSummaryInfo</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>column_type</td><td><code>string</code></td></tr>
                  <tr><td>column_count</td><td><code>int64</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_dataset_metadata</h5>
  <p>Get metadata about a dataset.</p>
</div>
<h5>Request: <code>ApiGetDatasetMetadataRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
</tbody></table>
<h5>Response: <code>ApiGetDatasetMetadataResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>info</td>
    <td>
      <details>
        <summary>DatasetInfo</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>dataset_id</td><td><code>int32</code></td></tr>
          <tr><td>dataset_slug</td><td><code>string</code></td></tr>
          <tr><td>owner_user</td><td><code>string</code></td></tr>
          <tr><td>usability_rating</td><td>double</td></tr>
          <tr><td>total_views</td><td><code>int32</code></td></tr>
          <tr><td>total_votes</td><td><code>int32</code></td></tr>
          <tr><td>total_downloads</td><td><code>int32</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>keywords</td><td><code>repeated string</code></td></tr>
          <tr>
            <td>licenses</td>
            <td>
              <details>
                <summary>repeated SettingsLicense</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>collaborators</td>
            <td>
              <details>
                <summary>repeated DatasetCollaborator</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>username</td><td><code>string</code></td></tr>
                  <tr><td>group_slug</td><td><code>string</code></td></tr>
                  <tr><td>role</td><td>kaggle.users.CollaboratorType</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>data</td>
            <td>
              <details>
                <summary>repeated DatasetSettingsFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>total_bytes</td><td><code>int64</code></td></tr>
                  <tr>
                    <td>columns</td>
                    <td>
                      <details>
                        <summary>repeated DatasetSettingsFileColumn</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>name</td><td><code>string</code></td></tr>
                          <tr><td>description</td><td><code>string</code></td></tr>
                          <tr><td>type</td><td><code>string</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>error_message</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_dataset_status</h5>
  <p>Get the processing status of a dataset.</p>
</div>
<h5>Request: <code>ApiGetDatasetStatusRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
</tbody></table>
<h5>Response: <code>ApiGetDatasetStatusResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>status</td><td><code>DatabundleVersionStatus</code></td><td>The processing status of a dataset. Possible values: DRAFT, PROCESSING, READY, ERROR, DELETED, PROCESSING_ERROR.</td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_dataset_files</h5>
  <p>List the files in a dataset.</p>
</div>
<h5>Request: <code>ApiListDatasetFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>dataset_version_number</td><td><code>int32</code></td><td>The version number of the dataset.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListDatasetFilesResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>dataset_files</td>
    <td>
      <details>
        <summary>repeated ApiDatasetFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>dataset_ref</td><td><code>string</code></td></tr>
          <tr><td>owner_ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>file_type</td><td><code>string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr>
            <td>columns</td>
            <td>
              <details>
                <summary>repeated ApiDatasetColumn</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>order</td><td><code>int32</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>type</td><td><code>string</code></td></tr>
                  <tr><td>original_type</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>error_message</td><td><code>string</code></td><td></td></tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ search_datasets</h5>
  <p>Search for datasets.</p>
</div>
<h5>Request: <code>ApiListDatasetsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>group</td><td>DatasetSelectionGroup</td><td>Possible values: DATASET_SELECTION_GROUP_PUBLIC, DATASET_SELECTION_GROUP_MY, DATASET_SELECTION_GROUP_USER, DATASET_SELECTION_GROUP_USER_SHARED_WITH_ME, DATASET_SELECTION_GROUP_UPVOTED, DATASET_SELECTION_GROUP_MY_PRIVATE, DATASET_SELECTION_GROUP_MY_PUBLIC, DATASET_SELECTION_GROUP_ORGANIZATION, DATASET_SELECTION_GROUP_BOOKMARKED, DATASET_SELECTION_GROUP_COLLABORATION, DATASET_SELECTION_GROUP_SHARED_WITH_USER, DATASET_SELECTION_GROUP_FEATURED, DATASET_SELECTION_GROUP_ALL, DATASET_SELECTION_GROUP_UNFEATURED.</td></tr>
  <tr><td>sort_by</td><td>DatasetSortBy</td><td>Possible values: DATASET_SORT_BY_HOTTEST, DATASET_SORT_BY_VOTES, DATASET_SORT_BY_UPDATED, DATASET_SORT_BY_ACTIVE, DATASET_SORT_BY_PUBLISHED, DATASET_SORT_BY_RELEVANCE, DATASET_SORT_BY_LAST_VIEWED, DATASET_SORT_BY_USABILITY, DATASET_SORT_BY_DOWNLOAD_COUNT, DATASET_SORT_BY_NOTEBOOK_COUNT.</td></tr>
  <tr><td>size</td><td>DatasetSizeGroup</td><td>Possible values: DATASET_SIZE_GROUP_ALL, DATASET_SIZE_GROUP_SMALL, DATASET_SIZE_GROUP_MEDIUM, DATASET_SIZE_GROUP_LARGE.</td></tr>
  <tr><td>file_type</td><td>DatasetFileTypeGroup</td><td>Possible values: DATASET_FILE_TYPE_GROUP_ALL, DATASET_FILE_TYPE_GROUP_CSV, DATASET_FILE_TYPE_GROUP_SQLITE, DATASET_FILE_TYPE_GROUP_JSON, DATASET_FILE_TYPE_GROUP_BIG_QUERY, DATASET_FILE_TYPE_GROUP_PARQUET.</td></tr>
  <tr><td>license</td><td>DatasetLicenseGroup</td><td>Possible values: DATASET_LICENSE_GROUP_ALL, DATASET_LICENSE_GROUP_CC, DATASET_LICENSE_GROUP_GPL, DATASET_LICENSE_GROUP_ODB, DATASET_LICENSE_GROUP_OTHER.</td></tr>
  <tr><td>viewed</td><td>DatasetViewedGroup</td><td>Possible values: DATASET_VIEWED_GROUP_UNSPECIFIED, DATASET_VIEWED_GROUP_VIEWED.</td></tr>
  <tr><td>tag_ids</td><td><code>string</code></td><td>The tag IDs to filter by.</td></tr>
  <tr><td>search</td><td><code>string</code></td><td>The search terms to filter by.</td></tr>
  <tr><td>user</td><td><code>string</code></td><td>The user to filter by.</td></tr>
  <tr><td>min_size</td><td><code>int64</code></td><td>The minimum size of the dataset in bytes.</td></tr>
  <tr><td>max_size</td><td><code>int64</code></td><td>The maximum size of the dataset in bytes.</td></tr>
  <tr><td>page</td><td><code>int32</code></td><td>The page number.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListDatasetsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>datasets</td>
    <td>
      <details>
        <summary>repeated ApiDataset</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>creator_name</td><td><code>string</code></td></tr>
          <tr><td>creator_url</td><td><code>string</code></td></tr>
          <tr><td>total_bytes</td><td><code>int64</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>last_updated</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>download_count</td><td><code>int32</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>is_featured</td><td><code>bool</code></td></tr>
          <tr><td>license_name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>owner_name</td><td><code>string</code></td></tr>
          <tr><td>owner_ref</td><td><code>string</code></td></tr>
          <tr><td>kernel_count</td><td><code>int32</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>topic_count</td><td><code>int32</code></td></tr>
          <tr><td>view_count</td><td><code>int32</code></td></tr>
          <tr><td>vote_count</td><td><code>int32</code></td></tr>
          <tr><td>current_version_number</td><td><code>int32</code></td></tr>
          <tr><td>usability_rating</td><td>float</td></tr>
          <tr>
            <td>tags</td>
            <td>
              <details>
                <summary>repeated ApiCategory</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>ref</td><td><code>string</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>full_path</td><td><code>string</code></td></tr>
                  <tr><td>competition_count</td><td><code>int32</code></td></tr>
                  <tr><td>dataset_count</td><td><code>int32</code></td></tr>
                  <tr><td>script_count</td><td><code>int32</code></td></tr>
                  <tr><td>total_count</td><td><code>int32</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>files</td>
            <td>
              <details>
                <summary>repeated ApiDatasetFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>ref</td><td><code>string</code></td></tr>
                  <tr><td>dataset_ref</td><td><code>string</code></td></tr>
                  <tr><td>owner_ref</td><td><code>string</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>file_type</td><td><code>string</code></td></tr>
                  <tr><td>url</td><td><code>string</code></td></tr>
                  <tr><td>total_bytes</td><td><code>int64</code></td></tr>
                  <tr>
                    <td>columns</td>
                    <td>
                      <details>
                        <summary>repeated ApiDatasetColumn</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>order</td><td><code>int32</code></td></tr>
                          <tr><td>name</td><td><code>string</code></td></tr>
                          <tr><td>type</td><td><code>string</code></td></tr>
                          <tr><td>original_type</td><td><code>string</code></td></tr>
                          <tr><td>description</td><td><code>string</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>versions</td>
            <td>
              <details>
                <summary>repeated ApiDatasetVersion</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>version_number</td><td><code>int32</code></td></tr>
                  <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
                  <tr><td>creator_name</td><td><code>string</code></td></tr>
                  <tr><td>creator_ref</td><td><code>string</code></td></tr>
                  <tr><td>version_notes</td><td><code>string</code></td></tr>
                  <tr><td>status</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>thumbnail_image_url</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_dataset_tree_files</h5>
  <p>List the files in a dataset by directory.</p>
</div>
<h5>Request: <code>ApiListTreeDatasetFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr><td>dataset_version_number</td><td><code>int32</code></td><td>The version number of the dataset.</td></tr>
  <tr><td>path</td><td><code>string</code></td><td>The path of the directory to list files from.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
</tbody></table>
<h5>Response: <code>ApiDirectoryContent</code></h5>

<div class="tool-header">
  <h5>○ update_dataset_metadata</h5>
  <p>Update the metadata for a dataset.</p>
</div>
<h5>Request: <code>ApiUpdateDatasetMetadataRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the dataset.</td></tr>
  <tr><td>dataset_slug</td><td><code>string</code></td><td>The slug of the dataset.</td></tr>
  <tr>
    <td>settings</td>
    <td>
      <details>
        <summary>DatasetSettings</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>keywords</td><td><code>repeated string</code></td></tr>
          <tr>
            <td>licenses</td>
            <td>
              <details>
                <summary>repeated SettingsLicense</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>collaborators</td>
            <td>
              <details>
                <summary>repeated DatasetCollaborator</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>username</td><td><code>string</code></td></tr>
                  <tr><td>group_slug</td><td><code>string</code></td></tr>
                  <tr><td>role</td><td>kaggle.users.CollaboratorType</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>data</td>
            <td>
              <details>
                <summary>repeated DatasetSettingsFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>total_bytes</td><td><code>int64</code></td></tr>
                  <tr>
                    <td>columns</td>
                    <td>
                      <details>
                        <summary>repeated DatasetSettingsFileColumn</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>name</td><td><code>string</code></td></tr>
                          <tr><td>description</td><td><code>string</code></td></tr>
                          <tr><td>type</td><td><code>string</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td>The new settings for the dataset.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiUpdateDatasetMetadataResponse</code></h5>

<div class="tool-header">
  <h5>○ upload_dataset_file</h5>
  <p>Upload a file to a dataset.</p>
</div>
<h5>Request: <code>ApiUploadDatasetFileRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>file_name</td><td><code>string</code></td><td>The name of the file to upload.</td></tr>
  <tr><td>content_length</td><td><code>int64</code></td><td>The length of the file in bytes.</td></tr>
  <tr><td>last_modified_epoch_seconds</td><td><code>int64</code></td><td>The last modified time of the file in epoch seconds.</td></tr>
</tbody></table>
<h5>Response: <code>ApiUploadDatasetFileResponse</code></h5>
</details>

<details><summary><h3>Models</h3></summary>
<div class="tool-header">
  <h5>○ create_model</h5>
  <p>Create a new model.</p>
</div>
<h5>Request: <code>ApiCreateModelRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>title</td><td><code>string</code></td><td>The title of the model.</td></tr>
  <tr><td>subtitle</td><td><code>string</code></td><td>The subtitle of the model.</td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td>Whether the model is private.</td></tr>
  <tr><td>description</td><td><code>string</code></td><td>The description of the model.</td></tr>
  <tr><td>publish_time</td><td><code>google.protobuf.Timestamp</code></td><td>The time to publish the model.</td></tr>
  <tr><td>provenance_sources</td><td><code>string</code></td><td>The provenance sources of the model.</td></tr>
</tbody></table>
<h5>Response: <code>ApiCreateModelResponse</code></h5>

<div class="tool-header">
  <h5>○ create_model_variation</h5>
  <p>Create a new model variation.</p>
</div>
<h5>Request: <code>ApiCreateModelInstanceRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>body</td>
    <td>
      <details>
        <summary>ApiCreateModelInstanceRequestBody</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>instance_slug</td><td><code>string</code></td></tr>
          <tr><td>framework</td><td>ModelFramework</td></tr>
          <tr><td>overview</td><td><code>string</code></td></tr>
          <tr><td>usage</td><td><code>string</code></td></tr>
          <tr><td>fine_tunable</td><td><code>bool</code></td></tr>
          <tr><td>training_data</td><td><code>repeated string</code></td></tr>
          <tr>
            <td>files</td>
            <td>
              <details>
                <summary>repeated kaggle.datasets.ApiDatasetNewFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>file_name</td><td><code>string</code></td></tr>
                  <tr><td>content</td><td>bytes</td></tr>
                  <tr><td>content_type</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>directories</td><td>repeated kaggle.datasets.ApiUploadDirectoryInfo</td></tr>
          <tr><td>license_name</td><td><code>string</code></td></tr>
          <tr><td>model_instance_type</td><td>ModelInstanceType</td></tr>
          <tr><td>base_model_instance</td><td><code>string</code></td></tr>
          <tr><td>external_base_model_url</td><td><code>string</code></td></tr>
          <tr><td>sigstore</td><td><code>bool</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The request body.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiCreateModelResponse</code></h5>

<div class="tool-header">
  <h5>○ create_model_variation_version</h5>
  <p>Create a new version of a model variation.</p>
</div>
<h5>Request: <code>ApiCreateModelInstanceVersionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
  <tr><td>body</td>
    <td>
      <details>
        <summary>ApiCreateModelInstanceVersionRequestBody</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>version_notes</td><td><code>string</code></td></tr>
          <tr>
            <td>files</td>
            <td>
              <details>
                <summary>repeated kaggle.datasets.ApiDatasetNewFile</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>file_name</td><td><code>string</code></td></tr>
                  <tr><td>content</td><td>bytes</td></tr>
                  <tr><td>content_type</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>directories</td><td>repeated kaggle.datasets.ApiUploadDirectoryInfo</td></tr>
          <tr><td>sigstore</td><td><code>bool</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td>The request body.</td>
  </tr>
</tbody></table>
<h5>Response: <code>ApiCreateModelResponse</code></h5>

<div class="tool-header">
  <h5>○ download_model_variation_version</h5>
  <p>Get a url where the files for a model variation version can be downloaded.</p>
</div>
<h5>Request: <code>ApiDownloadModelInstanceVersionRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td>The version number of the model instance.</td></tr>
  <tr><td>path</td><td><code>string</code></td><td>Relative path to a specific file inside the databundle.</td></tr>
</tbody></table>
<h5>Response: <code>HttpRedirect</code></h5>
<p>Returns a URL to download the model instance version.</p>

<div class="tool-header">
  <h5>○ get_model</h5>
  <p>Get a metadata about a model.</p>
</div>
<h5>Request: <code>ApiGetModelRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
</tbody></table>
<h5>Response: <code>ApiModel</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td></td></tr>
  <tr><td>ref</td><td><code>string</code></td><td></td></tr>
  <tr><td>title</td><td><code>string</code></td><td></td></tr>
  <tr><td>subtitle</td><td><code>string</code></td><td></td></tr>
  <tr><td>author</td><td><code>string</code></td><td></td></tr>
  <tr><td>slug</td><td><code>string</code></td><td></td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td></td></tr>
  <tr><td>description</td><td><code>string</code></td><td></td></tr>
  <tr>
    <td>instances</td>
    <td>
      <details>
        <summary>repeated ApiModelInstance</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>framework</td><td>ModelFramework</td></tr>
          <tr><td>fine_tunable</td><td><code>bool</code></td></tr>
          <tr><td>overview</td><td><code>string</code></td></tr>
          <tr><td>usage</td><td><code>string</code></td></tr>
          <tr><td>download_url</td><td><code>string</code></td></tr>
          <tr><td>version_id</td><td><code>int32</code></td></tr>
          <tr><td>version_number</td><td><code>int32</code></td></tr>
          <tr><td>training_data</td><td><code>repeated string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr><td>license_name</td><td><code>string</code></td></tr>
          <tr><td>model_instance_type</td><td>ModelInstanceType</td></tr>
          <tr>
            <td>base_model_instance_information</td>
            <td>
              <details>
                <summary>BaseModelInstanceInformation</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr>
                    <td>owner</td>
                    <td>
                      <details>
                        <summary>Owner</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>id</td><td><code>int32</code></td></tr>
                          <tr><td>image_url</td><td><code>string</code></td></tr>
                          <tr><td>is_organization</td><td><code>bool</code></td></tr>
                          <tr><td>name</td><td><code>string</code></td></tr>
                          <tr><td>profile_url</td><td><code>string</code></td></tr>
                          <tr><td>slug</td><td><code>string</code></td></tr>
                          <tr><td>user_tier</td><td>kaggle.users.UserAchievementTier</td></tr>
                          <tr><td>user_progression_opt_out</td><td><code>bool</code></td></tr>
                          <tr><td>allow_model_gating</td><td><code>bool</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                  <tr><td>model_slug</td><td><code>string</code></td></tr>
                  <tr><td>instance_slug</td><td><code>string</code></td></tr>
                  <tr><td>framework</td><td>ModelFramework</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>external_base_model_url</td><td><code>string</code></td></tr>
          <tr><td>total_uncompressed_bytes</td><td><code>int64</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr>
    <td>tags</td>
    <td>
      <details>
        <summary>repeated kaggle.datasets.ApiCategory</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr><td>full_path</td><td><code>string</code></td></tr>
          <tr><td>competition_count</td><td><code>int32</code></td></tr>
          <tr><td>dataset_count</td><td><code>int32</code></td></tr>
          <tr><td>script_count</td><td><code>int32</code></td></tr>
          <tr><td>total_count</td><td><code>int32</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>publish_time</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
  <tr><td>provenance_sources</td><td><code>string</code></td><td></td></tr>
  <tr><td>url</td><td><code>string</code></td><td></td></tr>
  <tr>
    <td>model_version_links</td>
    <td>
      <details>
        <summary>repeated ModelLink</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>type</td><td>ModelVersionLinkType</td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>vote_count</td><td><code>int32</code></td><td></td></tr>
  <tr><td>author_image_url</td><td><code>string</code></td><td></td></tr>
  <tr><td>update_time</td><td><code>google.protobuf.Timestamp</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ get_model_variation</h5>
  <p>Get metadata about a model variation.</p>
</div>
<h5>Request: <code>ApiGetModelInstanceRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
</tbody></table>
<h5>Response: <code>ApiModelInstance</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td><code>int32</code></td><td></td></tr>
  <tr><td>slug</td><td><code>string</code></td><td></td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td></td></tr>
  <tr><td>fine_tunable</td><td><code>bool</code></td><td></td></tr>
  <tr><td>overview</td><td><code>string</code></td><td></td></tr>
  <tr><td>usage</td><td><code>string</code></td><td></td></tr>
  <tr><td>download_url</td><td><code>string</code></td><td></td></tr>
  <tr><td>version_id</td><td><code>int32</code></td><td></td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td></td></tr>
  <tr><td>training_data</td><td><code>repeated string</code></td><td></td></tr>
  <tr><td>url</td><td><code>string</code></td><td></td></tr>
  <tr><td>license_name</td><td><code>string</code></td><td></td></tr>
  <tr><td>model_instance_type</td><td>ModelInstanceType</td><td></td></tr>
  <tr>
    <td>base_model_instance_information</td>
    <td>
      <details>
        <summary>BaseModelInstanceInformation</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr>
            <td>owner</td>
            <td>
              <details>
                <summary>Owner</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>image_url</td><td><code>string</code></td></tr>
                  <tr><td>is_organization</td><td><code>bool</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>profile_url</td><td><code>string</code></td></tr>
                  <tr><td>slug</td><td><code>string</code></td></tr>
                  <tr><td>user_tier</td><td>kaggle.users.UserAchievementTier</td></tr>
                  <tr><td>user_progression_opt_out</td><td><code>bool</code></td></tr>
                  <tr><td>allow_model_gating</td><td><code>bool</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>model_slug</td><td><code>string</code></td></tr>
          <tr><td>instance_slug</td><td><code>string</code></td></tr>
          <tr><td>framework</td><td>ModelFramework</td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>external_base_model_url</td><td><code>string</code></td><td></td></tr>
  <tr><td>total_uncompressed_bytes</td><td><code>int64</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_models</h5>
  <p>List models.</p>
</div>
<h5>Request: <code>ApiListModelsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>search</td><td><code>string</code></td><td>Display models matching the specified search terms.</td></tr>
  <tr><td>sort_by</td><td>ListModelsOrderBy</td><td>Sort the results. Possible values: LIST_MODELS_ORDER_BY_UNSPECIFIED, LIST_MODELS_ORDER_BY_HOTNESS, LIST_MODELS_ORDER_BY_DOWNLOAD_COUNT, LIST_MODELS_ORDER_BY_VOTE_COUNT, LIST_MODELS_ORDER_BY_NOTEBOOK_COUNT, LIST_MODELS_ORDER_BY_PUBLISH_TIME, LIST_MODELS_ORDER_BY_CREATE_TIME, LIST_MODELS_ORDER_BY_UPDATE_TIME, LIST_MODELS_ORDER_BY_VIEW_TIME_DESC.</td></tr>
  <tr><td>owner</td><td><code>string</code></td><td>Display models by a particular user or organization.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>Page size.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>Page token used for pagination.</td></tr>
  <tr><td>only_vertex_models</td><td><code>bool</code></td><td>Only list models that have Vertex URLs.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListModelsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>models</td>
    <td>
      <details>
        <summary>repeated ApiModel</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>ref</td><td><code>string</code></td></tr>
          <tr><td>title</td><td><code>string</code></td></tr>
          <tr><td>subtitle</td><td><code>string</code></td></tr>
          <tr><td>author</td><td><code>string</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>is_private</td><td><code>bool</code></td></tr>
          <tr><td>description</td><td><code>string</code></td></tr>
          <tr>
            <td>instances</td>
            <td>
              <details>
                <summary>repeated ApiModelInstance</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>slug</td><td><code>string</code></td></tr>
                  <tr><td>framework</td><td>ModelFramework</td></tr>
                  <tr><td>fine_tunable</td><td><code>bool</code></td></tr>
                  <tr><td>overview</td><td><code>string</code></td></tr>
                  <tr><td>usage</td><td><code>string</code></td></tr>
                  <tr><td>download_url</td><td><code>string</code></td></tr>
                  <tr><td>version_id</td><td><code>int32</code></td></tr>
                  <tr><td>version_number</td><td><code>int32</code></td></tr>
                  <tr><td>training_data</td><td><code>repeated string</code></td></tr>
                  <tr><td>url</td><td><code>string</code></td></tr>
                  <tr><td>license_name</td><td><code>string</code></td></tr>
                  <tr><td>model_instance_type</td><td>ModelInstanceType</td></tr>
                  <tr>
                    <td>base_model_instance_information</td>
                    <td>
                      <details>
                        <summary>BaseModelInstanceInformation</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>id</td><td><code>int32</code></td></tr>
                          <tr>
                            <td>owner</td>
                            <td>
                              <details>
                                <summary>Owner</summary>
                                <table style="margin-top: 1em;">
                                  <tbody><tr><th>Field</th><th>Type</th></tr>
                                  <tr><td>id</td><td><code>int32</code></td></tr>
                                  <tr><td>image_url</td><td><code>string</code></td></tr>
                                  <tr><td>is_organization</td><td><code>bool</code></td></tr>
                                  <tr><td>name</td><td><code>string</code></td></tr>
                                  <tr><td>profile_url</td><td><code>string</code></td></tr>
                                  <tr><td>slug</td><td><code>string</code></td></tr>
                                  <tr><td>user_tier</td><td>kaggle.users.UserAchievementTier</td></tr>
                                  <tr><td>user_progression_opt_out</td><td><code>bool</code></td></tr>
                                  <tr><td>allow_model_gating</td><td><code>bool</code></td></tr>
                                </tbody></table>
                              </details>
                            </td>
                          </tr>
                          <tr><td>model_slug</td><td><code>string</code></td></tr>
                          <tr><td>instance_slug</td><td><code>string</code></td></tr>
                          <tr><td>framework</td><td>ModelFramework</td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                  <tr><td>external_base_model_url</td><td><code>string</code></td></tr>
                  <tr><td>total_uncompressed_bytes</td><td><code>int64</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>tags</td>
            <td>
              <details>
                <summary>repeated kaggle.datasets.ApiCategory</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>ref</td><td><code>string</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>description</td><td><code>string</code></td></tr>
                  <tr><td>full_path</td><td><code>string</code></td></tr>
                  <tr><td>competition_count</td><td><code>int32</code></td></tr>
                  <tr><td>dataset_count</td><td><code>int32</code></td></tr>
                  <tr><td>script_count</td><td><code>int32</code></td></tr>
                  <tr><td>total_count</td><td><code>int32</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>publish_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
          <tr><td>provenance_sources</td><td><code>string</code></td></tr>
          <tr><td>url</td><td><code>string</code></td></tr>
          <tr>
            <td>model_version_links</td>
            <td>
              <details>
                <summary>repeated ModelLink</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>type</td><td>ModelVersionLinkType</td></tr>
                  <tr><td>url</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>vote_count</td><td><code>int32</code></td></tr>
          <tr><td>author_image_url</td><td><code>string</code></td></tr>
          <tr><td>update_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
  <tr><td>total_results</td><td><code>int64</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_model_variations</h5>
  <p>List model variations.</p>
</div>
<h5>Request: <code>ApiListModelInstancesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListModelInstancesResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>instances</td>
    <td>
      <details>
        <summary>repeated ModelInstance</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>id</td><td><code>int32</code></td></tr>
          <tr><td>owner_slug</td><td><code>string</code></td></tr>
          <tr><td>model_slug</td><td><code>string</code></td></tr>
          <tr><td>model_id</td><td><code>int32</code></td></tr>
          <tr><td>slug</td><td><code>string</code></td></tr>
          <tr><td>version_id</td><td><code>int32</code></td></tr>
          <tr><td>fine_tunable</td><td><code>bool</code></td></tr>
          <tr><td>overview</td><td><code>string</code></td></tr>
          <tr><td>usage</td><td><code>string</code></td></tr>
          <tr><td>rendered_usage</td><td><code>string</code></td></tr>
          <tr><td>text_representation</td><td><code>string</code></td></tr>
          <tr><td>source_url</td><td><code>string</code></td></tr>
          <tr><td>version_number</td><td><code>int32</code></td></tr>
          <tr><td>framework</td><td>ModelFramework</td></tr>
          <tr><td>version_notes</td><td><code>string</code></td></tr>
          <tr><td>download_url</td><td><code>string</code></td></tr>
          <tr><td>databundle_id</td><td><code>int32</code></td></tr>
          <tr><td>databundle_version_id</td><td><code>int32</code></td></tr>
          <tr><td>databundle_version_type</td><td>kaggle.datasets.DatabundleVersionType</td></tr>
          <tr><td>firestore_path</td><td><code>string</code></td></tr>
          <tr><td>status</td><td>kaggle.datasets.DatabundleVersionStatus</td></tr>
          <tr><td>creation_status</td><td>kaggle.datasets.DatabundleVersionCreationStatus</td></tr>
          <tr><td>error_message</td><td><code>string</code></td></tr>
          <tr><td>last_version_id</td><td><code>int32</code></td></tr>
          <tr>
            <td>source_organization</td>
            <td>
              <details>
                <summary>Owner</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>image_url</td><td><code>string</code></td></tr>
                  <tr><td>is_organization</td><td><code>bool</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>profile_url</td><td><code>string</code></td></tr>
                  <tr><td>slug</td><td><code>string</code></td></tr>
                  <tr><td>user_tier</td><td>kaggle.users.UserAchievementTier</td></tr>
                  <tr><td>user_progression_opt_out</td><td><code>bool</code></td></tr>
                  <tr><td>allow_model_gating</td><td><code>bool</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>training_data</td><td><code>repeated string</code></td></tr>
          <tr><td>metrics</td><td><code>string</code></td></tr>
          <tr>
            <td>license_post</td>
            <td>
              <details>
                <summary>LicensePost</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>content</td><td><code>string</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr>
            <td>license</td>
            <td>
              <details>
                <summary>kaggle.licenses.License</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>name</td><td><code>string</code></td></tr>
                  <tr><td>url</td><td><code>string</code></td></tr>
                  <tr><td>agreement_required</td><td><code>bool</code></td></tr>
                  <tr><td>agreement_status</td><td>UserLicenseAgreementStatus</td></tr>
                  <tr><td>consent_time</td><td><code>google.protobuf.Timestamp</code></td></tr>
                  <tr><td>current_revision_number</td><td><code>int32</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>can_use</td><td><code>bool</code></td></tr>
          <tr><td>uncompressed_storage_uri</td><td><code>string</code></td></tr>
          <tr><td>model_instance_type</td><td>ModelInstanceType</td></tr>
          <tr><td>base_model_instance_id</td><td><code>int32</code></td></tr>
          <tr>
            <td>base_model_instance_information</td>
            <td>
              <details>
                <summary>BaseModelInstanceInformation</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr>
                    <td>owner</td>
                    <td>
                      <details>
                        <summary>Owner</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>id</td><td><code>int32</code></td></tr>
                          <tr><td>image_url</td><td><code>string</code></td></tr>
                          <tr><td>is_organization</td><td><code>bool</code></td></tr>
                          <tr><td>name</td><td><code>string</code></td></tr>
                          <tr><td>profile_url</td><td><code>string</code></td></tr>
                          <tr><td>slug</td><td><code>string</code></td></tr>
                          <tr><td>user_tier</td><td>kaggle.users.UserAchievementTier</td></tr>
                          <tr><td>user_progression_opt_out</td><td><code>bool</code></td></tr>
                          <tr><td>allow_model_gating</td><td><code>bool</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                  <tr><td>model_slug</td><td><code>string</code></td></tr>
                  <tr><td>instance_slug</td><td><code>string</code></td></tr>
                  <tr><td>framework</td><td>ModelFramework</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>external_base_model_url</td><td><code>string</code></td></tr>
          <tr>
            <td>download_summary</td>
            <td>
              <details>
                <summary>ModelInstanceDownloadSummary</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>total_downloads</td><td>double</td></tr>
                  <tr>
                    <td>download_series_points</td>
                    <td>
                      <details>
                        <summary>repeated ModelActivityTimeSeriesPoint</summary>
                        <table style="margin-top: 1em;">
                          <tbody><tr><th>Field</th><th>Type</th></tr>
                          <tr><td>date</td><td><code>google.protobuf.Timestamp</code></td></tr>
                          <tr><td>count</td><td><code>int32</code></td></tr>
                        </tbody></table>
                      </details>
                    </td>
                  </tr>
                  <tr><td>model_instance_id</td><td><code>int32</code></td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
          <tr><td>total_uncompressed_bytes</td><td><code>int64</code></td></tr>
          <tr><td>sigstore_state</td><td>SigstoreState</td></tr>
          <tr><td>created_by_kernel_id</td><td><code>int32</code></td></tr>
          <tr><td>creator_user_id</td><td><code>int32</code></td></tr>
          <tr><td>attestation_kernel_url</td><td><code>string</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_model_variation_versions</h5>
  <p>List model variation versions.</p>
</div>
<h5>Request: <code>ApiListModelInstanceVersionsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListModelInstanceVersionsResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>version_list</td>
    <td>
      <details>
        <summary>ModelInstanceVersionList</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr>
            <td>versions</td>
            <td>
              <details>
                <summary>repeated ModelInstanceVersion</summary>
                <table style="margin-top: 1em;">
                  <tbody><tr><th>Field</th><th>Type</th></tr>
                  <tr><td>id</td><td><code>int32</code></td></tr>
                  <tr><td>framework</td><td>ModelFramework</td></tr>
                  <tr><td>is_tfhub_model</td><td><code>bool</code></td></tr>
                  <tr><td>url</td><td><code>string</code></td></tr>
                  <tr><td>variation_slug</td><td><code>string</code></td></tr>
                  <tr><td>version_number</td><td><code>int32</code></td></tr>
                  <tr><td>model_title</td><td><code>string</code></td></tr>
                  <tr><td>thumbnail_url</td><td><code>string</code></td></tr>
                  <tr><td>is_private</td><td><code>bool</code></td></tr>
                  <tr><td>sigstore_state</td><td>SigstoreState</td></tr>
                </tbody></table>
              </details>
            </td>
          </tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ list_model_variation_version_files</h5>
  <p>List the files of a model variation version.</p>
</div>
<h5>Request: <code>ApiListModelInstanceVersionFilesRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>version_number</td><td><code>int32</code></td><td>The version number of the model instance.</td></tr>
  <tr><td>page_size</td><td><code>int32</code></td><td>The number of items to return.</td></tr>
  <tr><td>page_token</td><td><code>string</code></td><td>The page token to use for pagination.</td></tr>
</tbody></table>
<h5>Response: <code>ApiListModelInstanceVersionFilesResponse</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr>
    <td>files</td>
    <td>
      <details>
        <summary>repeated ApiModelFile</summary>
        <table style="margin-top: 1em;">
          <tbody><tr><th>Field</th><th>Type</th></tr>
          <tr><td>name</td><td><code>string</code></td></tr>
          <tr><td>size</td><td><code>int64</code></td></tr>
          <tr><td>creation_date</td><td><code>google.protobuf.Timestamp</code></td></tr>
        </tbody></table>
      </details>
    </td>
    <td></td>
  </tr>
  <tr><td>next_page_token</td><td><code>string</code></td><td></td></tr>
</tbody></table>

<div class="tool-header">
  <h5>○ update_model</h5>
  <p>Update a model.</p>
</div>
<h5>Request: <code>ApiUpdateModelRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>title</td><td><code>string</code></td><td>The title of the model.</td></tr>
  <tr><td>subtitle</td><td><code>string</code></td><td>The subtitle of the model.</td></tr>
  <tr><td>is_private</td><td><code>bool</code></td><td>Whether the model is private.</td></tr>
  <tr><td>description</td><td><code>string</code></td><td>The description of the model.</td></tr>
  <tr><td>publish_time</td><td><code>google.protobuf.Timestamp</code></td><td>The time to publish the model.</td></tr>
  <tr><td>provenance_sources</td><td><code>string</code></td><td>The provenance sources of the model.</td></tr>
  <tr><td>update_mask</td><td>google.protobuf.FieldMask</td><td>The fields to update.</td></tr>
</tbody></table>
<h5>Response: <code>ApiUpdateModelResponse</code></h5>

<div class="tool-header">
  <h5>○ update_model_variation</h5>
  <p>Update a model variation.</p>
</div>
<h5>Request: <code>ApiUpdateModelInstanceRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>owner_slug</td><td><code>string</code></td><td>The slug of the owner of the model.</td></tr>
  <tr><td>model_slug</td><td><code>string</code></td><td>The slug of the model.</td></tr>
  <tr><td>framework</td><td>ModelFramework</td><td>Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON.</td></tr>
  <tr><td>instance_slug</td><td><code>string</code></td><td>The slug of the model instance.</td></tr>
  <tr><td>overview</td><td><code>string</code></td><td>The overview of the model instance.</td></tr>
  <tr><td>usage</td><td><code>string</code></td><td>The usage of the model instance.</td></tr>
  <tr><td>fine_tunable</td><td><code>bool</code></td><td>Whether the model instance is fine-tunable.</td></tr>
  <tr><td>training_data</td><td><code>repeated string</code></td><td>The training data of the model instance.</td></tr>
  <tr><td>update_mask</td><td>google.protobuf.FieldMask</td><td>The fields to update.</td></tr>
  <tr><td>license_name</td><td><code>string</code></td><td>The name of the license.</td></tr>
  <tr><td>model_instance_type</td><td>ModelInstanceType</td><td>Possible values: MODEL_INSTANCE_TYPE_UNSPECIFIED, MODEL_INSTANCE_TYPE_BASE_MODEL, MODEL_INSTANCE_TYPE_KAGGLE_VARIANT, MODEL_INSTANCE_TYPE_EXTERNAL_VARIANT.</td></tr>
  <tr><td>base_model_instance</td><td><code>string</code></td><td>The base model instance.</td></tr>
  <tr><td>external_base_model_url</td><td><code>string</code></td><td>The external base model URL.</td></tr>
</tbody></table>
<h5>Response: <code>ApiUpdateModelResponse</code></h5>
</details>

<details><summary><h3>Hackathons</h3></summary>
<div class="tool-header">
  <h5>○ download_hackathon_write_ups</h5>
  <p>Return CSV-formatted text of all hackathon submission write-ups.</p>
</div>
<h5>Request: <code>ExportHackathonWriteUpsCsvRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_id</td><td><code>int32</code></td><td>The ID of the hackathon competition.</td></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
</tbody></table>
<h5>Response: <code>ExportHackathonWriteUpsCsvResponse</code></h5>

<div class="tool-header">
  <h5>○ list_hackathon_write_ups</h5>
  <p>Return JSON of all hackathon submission write-ups.</p>
</div>
<h5>Request: <code>ApiListHackathonWriteUpsRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
  <tr><td>hackathon_track_ids</td><td><code>repeated int32</code></td><td>The ID of the hackathon competition.</td></tr>
  <tr><td>page_size</td><td><code>optional int32</code></td><td>Maximum number of returned write-ups per page.</td></tr>
    <tr><td>page_token</td><td><code>optional string</code></td><td>Next page token.</td></tr>


</tbody></table>
<h5>Response: <code>ListHackathonWriteUpsResponse</code></h5>


<div class="tool-header">
  <h5>○ get_hackathon_write_up</h5>
  <p>Return JSON of hackathon write-up</p>
</div>
<h5>Request: <code>ApiGetHackathonWriteUpRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
  <tr><td>hackathon_write_up_id</td><td><code>int32</code></td><td>The ID of the hackathon write-up.</td></tr>
</tbody></table>
<h5>Response: <code>HackathonWriteUp</code></h5>

<div class="tool-header">
  <h5>○ get_hackathon_overview</h5>
  <p>Return JSON list of hackathon overview pages</p>
</div>
<h5>Request: <code>ApiGetHackathonOverviewRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_name</td><td><code>string</code></td><td>The name of the competition.</td></tr>
</tbody></table>
<h5>Response: <code>ListPagesResponse</code></h5>

<div class="tool-header">
  <h5>○ list_hackathon_tracks</h5>
  <p>Return JSON of all hackathon tracks.</p>
</div>
<h5>Request: <code>ListHackathonTracksRequest</code></h5>
<table>
  <tbody><tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>competition_id</td><td><code>int32</code></td><td>The ID of the hackathon competition.</td></tr>
</tbody></table>
<h5>Response: <code>ListHackathonTracksResponse</code></h5>



</details>