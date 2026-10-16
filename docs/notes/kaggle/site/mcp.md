> Full piece: [https://www.kaggle.com/docs/mcp](https://www.kaggle.com/docs/mcp)
> Retrieved 2026-10-16T03:04Z by scripts/capture_kaggle_docs.py --site (headless Chromium, pandoc);
> rendered HTML sha256 431de5dd1b3669560c40cd0d27ff9ccacb43e5c16d7f705cbbf4909836982466.

Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.

[](/cookies)

Learn more

OK, Got it.

# How to Use Kaggle

keyboard_arrow_right[Competitions](/docs/competitions)

keyboard_arrow_right[Datasets](/docs/datasets)

[Efficient GPU Usage Tips](/docs/efficient-gpu-usage)

keyboard_arrow_right[Tensor Processing Units (TPUs)](/docs/tpu)

keyboard_arrow_right[Models](/docs/models)

keyboard_arrow_right[Competitions Setup](/docs/competitions-setup)

keyboard_arrow_right[Organizations](/docs/organizations)

keyboard_arrow_right[Groups](/docs/groups)

keyboard_arrow_right[Kaggle Packages](/docs/packages)

keyboard_arrow_right[Notebooks](/docs/notebooks)

keyboard_arrow_down

MCP Server

keyboard_arrow_right

[Configuration Examples](#)

keyboard_arrow_right

[Token Authentication](#)

[Notebooks](#)

[Benchmarks](#)

[Competitions](#)

[Datasets](#)

[Models](#)

[Hackathons](#)

keyboard_arrow_right[Benchmarks](/docs/benchmarks)

keyboard_arrow_right[Public API](/docs/api)

## MCP Server

Power up your Agents and streamline development workflows using Kaggle's resources.

content_copyCopy as Markdown

------------------------------------------------------------------------

## Getting Started

To run the remote server, you need to paste the following code block into your client's configuration. The remote server URL is `https://www.kaggle.com/mcp`.

### Configuration Examples

#### Gemini CLI

     gemini mcp add --transport http kaggle https://www.kaggle.com/mcp

Alternatively, you can add the following to your `~/.gemini/settings.json` file:

     {
          "mcpServers": {
            "kaggle": {
              "httpUrl": "https://www.kaggle.com/mcp"
            }
          }
        }

#### Claude Desktop

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

#### VS Code (settings.json)

    {
      "servers": {
         "kaggle": {
         "url": "https://www.kaggle.com/mcp",
         "type": "http"
            }
        },
    }]
    }

#### Windsurf

Add the following to your ~/.codeium/mcp_config.json:

    {
      "mcpServers": {
        "kaggle": {
          "serverUrl" : "https://www.kaggle.com/mcp"
        }
      }
    }

------------------------------------------------------------------------

## Authorization

Some resources, or endpoints require authorization. To unlock full access you can authorize using OAuth 2.0

#### Gemini CLI

Simply run the following command: `/mcp auth kaggle`

#### Other Clients/IDEs

For other clients that do not have a command to initiate auth discovery you can call the `authorize` tool

### Token Authentication

If your client is not OAuth 2.0 compliant, you can also use token authentication.

If you don't already have a token navigate to [Settings](/settings) \> Generate New Token \> "Copy". The token should begin with "KGAT"

#### Gemini CLI

    "mcpServers": {
        "kaggle": {
          "transport": "http",
          "httpUrl": "https://www.kaggle.com/mcp",
          "headers": {
            "Authorization": "Bearer YOUR_TOKEN"
          }
        }
      },

#### Claude Desktop

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

#### Vscode

    "servers": {
      "kaggle": {
        "url": "https://www.kaggle.com/mcp",
        "type": "http",
          "headers" : {
          "authorization": "Bearer YOUR_TOKEN"
            }
        }
    }

#### Windsurf

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

------------------------------------------------------------------------

## Tool Definitions

### Notebooks

##### ○ cancel_notebook_session

Cancel a notebook session.

##### Request: `ApiCancelKernelSessionRequest`

|                   |         |                                         |
|-------------------|---------|-----------------------------------------|
| Field             | Type    | Description                             |
| kernel_session_id | `int32` | The ID of the kernel session to cancel. |

##### Response: `ApiCancelKernelSessionResponse`

|               |          |                                                    |
|---------------|----------|----------------------------------------------------|
| Field         | Type     | Description                                        |
| error_message | `string` | Optional error message if the cancellation failed. |

##### ○ create_notebook_session

Create a new notebook session.

##### Request: `ApiCreateKernelSessionRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| slug | `string` | The full slug of the kernel to create an interactive session for, in the format \`{username}/{kernel-slug}\`. |
| language | `string` | The language that the kernel is written in. One of "python", "r" and "rmarkdown". |
| kernel_type | `string` | The type of kernel. Options are 'notebook' or 'script'. |
| docker_image | `string` | Which docker image to run with. |
| machine_shape | `string` | The machine shape to use for this session. |
| enable_internet | `bool` | Whether or not the kernel should be able to access the internet in this session. |

##### Response: `Operation`

This method returns a long-running operation.

##### ○ download_notebook_output

Download the output of a notebook.

##### Request: `ApiDownloadKernelOutputRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the kernel. |
| kernel_slug | `string` | The slug of the kernel. |
| file_path | `string` | Relative path to a specific file inside the databundle. |
| version_number | `int32` | The version number of the kernel. |

##### Response: `HttpRedirect`

Returns a URL to download the output.

##### ○ download_notebook_output_zip

Download the zipped output of a notebook.

##### Request: `ApiDownloadKernelOutputZipRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| kernel_session_id | `int32` | The ID of the kernel session to download the output from. |

##### Response: `FileDownload`

Returns a file download object.

##### ○ get_notebook_info

Get information about a notebook.

##### Request: `ApiGetKernelRequest`

|             |          |                                          |
|-------------|----------|------------------------------------------|
| Field       | Type     | Description                              |
| user_name   | `string` | The username of the owner of the kernel. |
| kernel_slug | `string` | The slug of the kernel.                  |

##### Response: `ApiGetKernelResponse`

[TABLE]

##### ○ get_notebook_session_status

Get the status of a notebook session.

##### Request: `ApiGetKernelSessionStatusRequest`

|             |          |                                          |
|-------------|----------|------------------------------------------|
| Field       | Type     | Description                              |
| user_name   | `string` | The username of the owner of the kernel. |
| kernel_slug | `string` | The slug of the kernel.                  |

##### Response: `ApiGetKernelSessionStatusResponse`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| status | `KernelWorkerStatus` | The status of the session. Possible values: `QUEUED`, `RUNNING`, `COMPLETE`, `ERROR`, `CANCEL_REQUESTED`, `CANCEL_ACKNOWLEDGED`, `NEW_SCRIPT`. |
| failure_message | `string` | Optional failure message. |

##### ○ list_notebook_files

List the files in a notebook.

##### Request: `ApiListKernelFilesRequest`

|             |          |                                          |
|-------------|----------|------------------------------------------|
| Field       | Type     | Description                              |
| user_name   | `string` | The username of the owner of the kernel. |
| kernel_slug | `string` | The slug of the kernel.                  |
| page_size   | `int32`  | The number of items to return.           |
| page_token  | `string` | The page token to use for pagination.    |

##### Response: `ApiListKernelFilesResponse`

[TABLE]

##### ○ list_notebook_session_output

List the output files of a notebook session.

##### Request: `ApiListKernelSessionOutputRequest`

|             |          |                                          |
|-------------|----------|------------------------------------------|
| Field       | Type     | Description                              |
| user_name   | `string` | The username of the owner of the kernel. |
| kernel_slug | `string` | The slug of the kernel.                  |
| page_size   | `int32`  | The number of items to return.           |
| page_token  | `string` | The page token to use for pagination.    |

##### Response: `ApiListKernelSessionOutputResponse`

[TABLE]

##### ○ save_notebook

Save a notebook and run it from top to bottom.

##### Request: `ApiSaveKernelRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| id | `int32` | The kernel's unique ID number. |
| slug | `string` | The full slug of the kernel to push to. |
| new_title | `string` | The title to be set on the kernel. |
| text | `string` | The kernel's source code. |
| language | `string` | The language that the kernel is written in. One of "python", "r" and "rmarkdown". |
| kernel_type | `string` | The type of kernel. Cannot be changed once the kernel has been created. |
| dataset_data_sources | `repeated string` | A list of dataset data sources that the kernel should use. |
| kernel_data_sources | `repeated string` | A list of kernel data sources that the kernel should use. |
| competition_data_sources | `repeated string` | A list of competition data sources that the kernel should use. |
| category_ids | `repeated string` | A list of tag IDs to associated with the kernel. |
| is_private | `bool` | Whether or not the kernel should be private. |
| enable_gpu | `bool` | Whether or not the kernel should run on a GPU. DEPRECATED: use \`machine_shape\` instead. |
| enable_tpu | `bool` | Whether or not the kernel should run on a TPU. DEPRECATED: use \`machine_shape\` instead. |
| enable_internet | `bool` | Whether or not the kernel should be able to access the internet. |
| docker_image_pinning_type | `string` | Which docker image to use for executing new versions going forward. |
| model_data_sources | `repeated string` | A list of model data sources that the kernel should use. |

##### Response: `ApiSaveKernelResponse`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| ref | `string` | The reference of the kernel. |
| url | `string` | The URL of the kernel. |
| version_number | `int32` | The new version number of the kernel. |
| error | `string` | An error message if the save failed. |
| invalid_tags | `repeated string` | A list of invalid tags. |
| invalid_dataset_sources | `repeated string` | A list of invalid dataset sources. |
| invalid_competition_sources | `repeated string` | A list of invalid competition sources. |
| invalid_kernel_sources | `repeated string` | A list of invalid kernel sources. |
| invalid_model_sources | `repeated string` | A list of invalid model sources. |
| kernel_id | `int32` | The ID of the kernel. |

##### ○ search_notebooks

Search for notebooks.

##### Request: `ApiListKernelsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition | `string` | Display kernels using the specified competition. |
| dataset | `string` | Display kernels using the specified dataset. |
| parent_kernel | `string` | Display kernels that have forked the specified kernel. |
| group | `KernelsListViewType` | Display your kernels, collaborated, bookmarked or upvoted kernels. Possible values: `PROFILE`, `UPVOTED`, `EVERYONE`, `COLLABORATION`, `FORK`, `BOOKMARKED`, `RECENTLY_VIEWED`, `PUBLIC_AND_USERS_PRIVATE`. |
| kernel_type | `string` | Display kernels of a specific type. |
| language | `string` | Display kernels in a specific language. One of "all", "python", "r", "sqlite" and "julia". |
| output_type | `string` | Display kernels with a specific output type. One of "all", "visualization" and "notebook". |
| search | `string` | Display kernels matching the specified search terms. |
| sort_by | `KernelsListSortType` | Sort the results. Possible values: `HOTNESS`, `COMMENT_COUNT`, `DATE_CREATED`, `DATE_RUN`, RELEVANCE, `SCORE_ASCENDING`, `SCORE_DESCENDING`, `VIEW_COUNT`, `VOTE_COUNT`. |
| user | `string` | Display kernels by a particular user or group. |
| page | `int32` | Page number. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |
| page_token | `string` | The page token to use for pagination. |

##### Response: `ApiListKernelsResponse`

[TABLE]

### Benchmarks

##### ○ create_benchmark_task_from_prompt

Create a new benchmark task from a prompt.

##### Request: `CreateBenchmarkTaskFromPromptRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| prompt | `string` | A natural language prompt describing the benchmark task to be created. |

##### Response: `CreateBenchmarkTaskFromPromptResponse`

[TABLE]

##### ○ get_benchmark_leaderboard

Get the leaderboard for a benchmark.

##### Request: `ApiGetBenchmarkLeaderboardRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the user or organization that owns the benchmark. |
| benchmark_slug | `string` | The slug of the benchmark. |
| version_number | `int32` | The version number of the benchmark to get the leaderboard for. If not provided, the latest version is used. |

##### Response: `ApiBenchmarkLeaderboard`

[TABLE]

### Competitions

##### ○ create_code_competition_submission

Submit a kernel to a competition.

##### Request: `ApiCreateCodeSubmissionRequest`

|                        |          |                                          |
|------------------------|----------|------------------------------------------|
| Field                  | Type     | Description                              |
| competition_name       | `string` | The name of the competition.             |
| kernel_owner           | `string` | The username of the owner of the kernel. |
| kernel_slug            | `string` | The slug of the kernel.                  |
| kernel_version         | `int32`  | The version number of the kernel.        |
| file_name              | `string` | The name of the file to submit.          |
| submission_description | `string` | A description for the submission.        |

##### Response: `ApiCreateCodeSubmissionResponse`

|         |          |                                            |
|---------|----------|--------------------------------------------|
| Field   | Type     | Description                                |
| message | `string` | An error message if the submission failed. |
| ref     | `int32`  | The ID of the submission.                  |

##### ○ submit_to_competition

Submit a new competition submission.

##### Request: `ApiCreateSubmissionRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| blob_file_tokens | `string` | Token identifying location of uploaded submission file. |
| submission_description | `string` | Description of competition submission. |

##### Response: `ApiCreateSubmissionResponse`

|         |          |                                     |
|---------|----------|-------------------------------------|
| Field   | Type     | Description                         |
| message | `string` | Error message from InvalidArgument. |
| ref     | `int32`  | The ID of the submission.           |

##### ○ download_competition_data_file

Download a single data file for a competition.

##### Request: `ApiDownloadDataFileRequest`

|                  |          |                               |
|------------------|----------|-------------------------------|
| Field            | Type     | Description                   |
| competition_name | `string` | Competition name.             |
| file_name        | `string` | Name of the file to download. |

##### Response: `HttpRedirect`

Returns a URL to download the file.

##### ○ download_competition_data_files

Download all data files for a competition.

##### Request: `ApiDownloadDataFilesRequest`

|                  |          |                   |
|------------------|----------|-------------------|
| Field            | Type     | Description       |
| competition_name | `string` | Competition name. |

##### Response: `HttpRedirect`

Returns a URL to download the files.

##### ○ download_competition_leaderboard

Download the leaderboard for a competition.

##### Request: `ApiDownloadLeaderboardRequest`

|                  |          |                              |
|------------------|----------|------------------------------|
| Field            | Type     | Description                  |
| competition_name | `string` | The name of the competition. |

##### Response: `FileDownload`

Returns a file download object.

##### ○ get_competition

Get competition metadata.

##### Request: `ApiGetCompetitionRequest`

|                  |          |                              |
|------------------|----------|------------------------------|
| Field            | Type     | Description                  |
| competition_name | `string` | The name of the competition. |

##### Response: `ApiCompetition`

[TABLE]

##### ○ get_competition_data_files_summary

Get a summary of the data files for a competition.

##### Request: `ApiGetCompetitionDataFilesSummaryRequest`

|                  |          |                              |
|------------------|----------|------------------------------|
| Field            | Type     | Description                  |
| competition_name | `string` | The name of the competition. |

##### Response: `ApiFilesSummary`

##### ○ get_competition_leaderboard

Get the leaderboard for a competition.

##### Request: `ApiGetLeaderboardRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| override_public | `bool` | By default we return the private leaderboard if it's available, otherwise the public LB. This flag lets you override to get public even if private is available. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |
| page_token | `string` | Page token. |

##### Response: `ApiGetLeaderboardResponse`

[TABLE]

##### ○ get_competition_submission

Get metadata about a competition submission.

##### Request: `ApiGetSubmissionRequest`

|       |         |               |
|-------|---------|---------------|
| Field | Type    | Description   |
| ref   | `int32` | SubmissionId. |

##### Response: `ApiSubmission`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| ref | `int32` |  |
| total_bytes | `int64` |  |
| date | `google.protobuf.Timestamp` |  |
| description | `string` |  |
| error_description | `string` |  |
| file_name | `string` |  |
| public_score | `string` |  |
| private_score | `string` |  |
| status | `SubmissionStatus` | Possible values: PUBLIC, PRIVATE, CANCELLED, ERROR, STUCK, COMPLETE, NONE. |
| submitted_by | `string` |  |
| submitted_by_ref | `string` |  |
| team_name | `string` |  |
| url | `string` |  |

##### ○ search_competitions

Search for competitions.

##### Request: `ApiListCompetitionsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| group | CompetitionListTab | Filter competitions by a particular group. Possible values: `COMPETITION_LIST_TAB_GENERAL`, `COMPETITION_LIST_TAB_ENTERED`, `COMPETITION_LIST_TAB_COMMUNITY`, `COMPETITION_LIST_TAB_HOSTED`, `COMPETITION_LIST_TAB_UNLAUNCHED`, `COMPETITION_LIST_TAB_UNLAUNCHED_COMMUNITY`, `COMPETITION_LIST_TAB_EVERYTHING`. |
| category | HostSegment | Filter competitions by a particular category. Possible values: `HOST_SEGMENT_UNSPECIFIED, ``HOST_SEGMENT_FEATURED``, ``HOST_SEGMENT_GETTING_STARTED``, ``HOST_SEGMENT_MASTERS``, ``HOST_SEGMENT_PLAYGROUND``, ``HOST_SEGMENT_RECRUITMENT``, ``HOST_SEGMENT_RESEARCH``, ``HOST_SEGMENT_COMMUNITY``, ``HOST_SEGMENT_ANALYTICS``.` |
| sort_by | CompetitionSortBy | Sort the results. Possible values: `COMPETITION_SORT_BY_GROUPED`, `COMPETITION_SORT_BY_BEST`, `COMPETITION_SORT_BY_PRIZE`, `COMPETITION_SORT_BY_EARLIEST_DEADLINE`, `COMPETITION_SORT_BY_LATEST_DEADLINE`, `COMPETITION_SORT_BY_NUMBER_OF_TEAMS`, `COMPETITION_SORT_BY_RELEVANCE`, `COMPETITION_SORT_BY_RECENTLY_CREATED`. |
| search | `string` | Filter competitions by search terms. |
| page | `int32` | Page number. |
| page_token | `string` | Page token. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |

##### Response: `ApiListCompetitionsResponse`

[TABLE]

##### ○ list_competition_data_files

List the data files for a competition.

##### Request: `ApiListDataFilesRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |
| page_token | `string` | Page token. |

##### Response: `ApiListDataFilesResponse`

[TABLE]

##### ○ list_competition_data_tree_files

List the data files by directory for a competition.

##### Request: `ApiListDataTreeFilesRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| path | `string` | The path of the directory to list files from. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |
| page_token | `string` | Page token. |

##### Response: `ApiDirectoryContent`

[TABLE]

##### ○ search_competition_submissions

Search for competition submissions.

##### Request: `ApiListSubmissionsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| sort_by | `SubmissionSortBy` | Possible values: `SUBMISSION_SORT_BY_DATE`, `SUBMISSION_SORT_BY_NAME`, `SUBMISSION_SORT_BY_PRIVATE_SCORE`, `SUBMISSION_SORT_BY_PUBLIC_SCORE`. |
| group | `SubmissionGroup` | Possible values: `SUBMISSION_GROUP_ALL`, `SUBMISSION_GROUP_SUCCESSFUL`, `SUBMISSION_GROUP_SELECTED`. |
| page | `int32` | Page number. |
| page_token | `string` | Page token. |
| page_size | `int32` | Page size, i.e., maximum number of results to return. |

##### Response: `ApiListSubmissionsResponse`

[TABLE]

##### ○ start_competition_submission_upload

Get a link to upload a competition submission file.

##### Request: `ApiStartSubmissionUploadRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | Competition name. |
| content_length | `int64` | The length of the file in bytes. |
| last_modified_epoch_seconds | `int64` | The last modified time of the file in epoch seconds. |
| file_name | `string` | Comes from form upload. |

##### Response: `ApiStartSubmissionUploadResponse`

### Datasets

##### ○ create_dataset

Create a new dataset.

##### Request: `ApiCreateDatasetRequest`

[TABLE]

##### Response: `ApiCreateDatasetResponse`

##### ○ create_dataset_version

Create a new version of a dataset. Identified by the owner and dataset slugs.

##### Request: `ApiCreateDatasetVersionRequest`

[TABLE]

##### Response: `ApiCreateDatasetResponse`

##### ○ create_dataset_version_by_id

Create a new version of a dataset. Identified by the dataset id.

##### Request: `ApiCreateDatasetVersionByIdRequest`

[TABLE]

##### Response: `ApiCreateDatasetResponse`

##### ○ download_dataset

Download a dataset.

##### Request: `ApiDownloadDatasetRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the dataset. |
| dataset_slug | `string` | The slug of the dataset. |
| file_name | `string` | The name of the file to download. |
| dataset_version_number | `int32` | The version number of the dataset. |
| raw | `bool` | Whether to download the raw version of the dataset. |
| hash_link | `string` | A hash link to the dataset. |

##### Response: `HttpRedirect`

Returns a URL to download the dataset.

##### ○ get_dataset_info

Get information about a dataset.

##### Request: `ApiGetDatasetRequest`

|              |          |                                       |
|--------------|----------|---------------------------------------|
| Field        | Type     | Description                           |
| owner_slug   | `string` | The slug of the owner of the dataset. |
| dataset_slug | `string` | The slug of the dataset.              |

##### Response: `ApiDataset`

[TABLE]

##### ○ get_dataset_files_summary

Get a summary of the data files in a dataset.

##### Request: `ApiGetDatasetFilesSummaryRequest`

|                        |          |                                       |
|------------------------|----------|---------------------------------------|
| Field                  | Type     | Description                           |
| owner_slug             | `string` | The slug of the owner of the dataset. |
| dataset_slug           | `string` | The slug of the dataset.              |
| dataset_version_number | `int32`  | The version number of the dataset.    |

##### Response: `ApiFilesSummary`

[TABLE]

##### ○ get_dataset_metadata

Get metadata about a dataset.

##### Request: `ApiGetDatasetMetadataRequest`

|              |          |                                       |
|--------------|----------|---------------------------------------|
| Field        | Type     | Description                           |
| owner_slug   | `string` | The slug of the owner of the dataset. |
| dataset_slug | `string` | The slug of the dataset.              |

##### Response: `ApiGetDatasetMetadataResponse`

[TABLE]

##### ○ get_dataset_status

Get the processing status of a dataset.

##### Request: `ApiGetDatasetStatusRequest`

|              |          |                                       |
|--------------|----------|---------------------------------------|
| Field        | Type     | Description                           |
| owner_slug   | `string` | The slug of the owner of the dataset. |
| dataset_slug | `string` | The slug of the dataset.              |

##### Response: `ApiGetDatasetStatusResponse`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| status | `DatabundleVersionStatus` | The processing status of a dataset. Possible values: DRAFT, PROCESSING, READY, ERROR, DELETED, PROCESSING_ERROR. |

##### ○ list_dataset_files

List the files in a dataset.

##### Request: `ApiListDatasetFilesRequest`

|                        |          |                                       |
|------------------------|----------|---------------------------------------|
| Field                  | Type     | Description                           |
| owner_slug             | `string` | The slug of the owner of the dataset. |
| dataset_slug           | `string` | The slug of the dataset.              |
| dataset_version_number | `int32`  | The version number of the dataset.    |
| page_token             | `string` | The page token to use for pagination. |
| page_size              | `int32`  | The number of items to return.        |

##### Response: `ApiListDatasetFilesResponse`

[TABLE]

##### ○ search_datasets

Search for datasets.

##### Request: `ApiListDatasetsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| group | DatasetSelectionGroup | Possible values: DATASET_SELECTION_GROUP_PUBLIC, DATASET_SELECTION_GROUP_MY, DATASET_SELECTION_GROUP_USER, DATASET_SELECTION_GROUP_USER_SHARED_WITH_ME, DATASET_SELECTION_GROUP_UPVOTED, DATASET_SELECTION_GROUP_MY_PRIVATE, DATASET_SELECTION_GROUP_MY_PUBLIC, DATASET_SELECTION_GROUP_ORGANIZATION, DATASET_SELECTION_GROUP_BOOKMARKED, DATASET_SELECTION_GROUP_COLLABORATION, DATASET_SELECTION_GROUP_SHARED_WITH_USER, DATASET_SELECTION_GROUP_FEATURED, DATASET_SELECTION_GROUP_ALL, DATASET_SELECTION_GROUP_UNFEATURED. |
| sort_by | DatasetSortBy | Possible values: DATASET_SORT_BY_HOTTEST, DATASET_SORT_BY_VOTES, DATASET_SORT_BY_UPDATED, DATASET_SORT_BY_ACTIVE, DATASET_SORT_BY_PUBLISHED, DATASET_SORT_BY_RELEVANCE, DATASET_SORT_BY_LAST_VIEWED, DATASET_SORT_BY_USABILITY, DATASET_SORT_BY_DOWNLOAD_COUNT, DATASET_SORT_BY_NOTEBOOK_COUNT. |
| size | DatasetSizeGroup | Possible values: DATASET_SIZE_GROUP_ALL, DATASET_SIZE_GROUP_SMALL, DATASET_SIZE_GROUP_MEDIUM, DATASET_SIZE_GROUP_LARGE. |
| file_type | DatasetFileTypeGroup | Possible values: DATASET_FILE_TYPE_GROUP_ALL, DATASET_FILE_TYPE_GROUP_CSV, DATASET_FILE_TYPE_GROUP_SQLITE, DATASET_FILE_TYPE_GROUP_JSON, DATASET_FILE_TYPE_GROUP_BIG_QUERY, DATASET_FILE_TYPE_GROUP_PARQUET. |
| license | DatasetLicenseGroup | Possible values: DATASET_LICENSE_GROUP_ALL, DATASET_LICENSE_GROUP_CC, DATASET_LICENSE_GROUP_GPL, DATASET_LICENSE_GROUP_ODB, DATASET_LICENSE_GROUP_OTHER. |
| viewed | DatasetViewedGroup | Possible values: DATASET_VIEWED_GROUP_UNSPECIFIED, DATASET_VIEWED_GROUP_VIEWED. |
| tag_ids | `string` | The tag IDs to filter by. |
| search | `string` | The search terms to filter by. |
| user | `string` | The user to filter by. |
| min_size | `int64` | The minimum size of the dataset in bytes. |
| max_size | `int64` | The maximum size of the dataset in bytes. |
| page | `int32` | The page number. |
| page_token | `string` | The page token to use for pagination. |
| page_size | `int32` | The number of items to return. |

##### Response: `ApiListDatasetsResponse`

[TABLE]

##### ○ list_dataset_tree_files

List the files in a dataset by directory.

##### Request: `ApiListTreeDatasetFilesRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the dataset. |
| dataset_slug | `string` | The slug of the dataset. |
| dataset_version_number | `int32` | The version number of the dataset. |
| path | `string` | The path of the directory to list files from. |
| page_token | `string` | The page token to use for pagination. |
| page_size | `int32` | The number of items to return. |

##### Response: `ApiDirectoryContent`

##### ○ update_dataset_metadata

Update the metadata for a dataset.

##### Request: `ApiUpdateDatasetMetadataRequest`

[TABLE]

##### Response: `ApiUpdateDatasetMetadataResponse`

##### ○ upload_dataset_file

Upload a file to a dataset.

##### Request: `ApiUploadDatasetFileRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| file_name | `string` | The name of the file to upload. |
| content_length | `int64` | The length of the file in bytes. |
| last_modified_epoch_seconds | `int64` | The last modified time of the file in epoch seconds. |

##### Response: `ApiUploadDatasetFileResponse`

### Models

##### ○ create_model

Create a new model.

##### Request: `ApiCreateModelRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| slug | `string` | The slug of the model. |
| title | `string` | The title of the model. |
| subtitle | `string` | The subtitle of the model. |
| is_private | `bool` | Whether the model is private. |
| description | `string` | The description of the model. |
| publish_time | `google.protobuf.Timestamp` | The time to publish the model. |
| provenance_sources | `string` | The provenance sources of the model. |

##### Response: `ApiCreateModelResponse`

##### ○ create_model_variation

Create a new model variation.

##### Request: `ApiCreateModelInstanceRequest`

[TABLE]

##### Response: `ApiCreateModelResponse`

##### ○ create_model_variation_version

Create a new version of a model variation.

##### Request: `ApiCreateModelInstanceVersionRequest`

[TABLE]

##### Response: `ApiCreateModelResponse`

##### ○ download_model_variation_version

Get a url where the files for a model variation version can be downloaded.

##### Request: `ApiDownloadModelInstanceVersionRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| framework | ModelFramework | Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON. |
| instance_slug | `string` | The slug of the model instance. |
| version_number | `int32` | The version number of the model instance. |
| path | `string` | Relative path to a specific file inside the databundle. |

##### Response: `HttpRedirect`

Returns a URL to download the model instance version.

##### ○ get_model

Get a metadata about a model.

##### Request: `ApiGetModelRequest`

|            |          |                                     |
|------------|----------|-------------------------------------|
| Field      | Type     | Description                         |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model.              |

##### Response: `ApiModel`

[TABLE]

##### ○ get_model_variation

Get metadata about a model variation.

##### Request: `ApiGetModelInstanceRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| framework | ModelFramework | Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON. |
| instance_slug | `string` | The slug of the model instance. |

##### Response: `ApiModelInstance`

[TABLE]

##### ○ list_models

List models.

##### Request: `ApiListModelsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| search | `string` | Display models matching the specified search terms. |
| sort_by | ListModelsOrderBy | Sort the results. Possible values: LIST_MODELS_ORDER_BY_UNSPECIFIED, LIST_MODELS_ORDER_BY_HOTNESS, LIST_MODELS_ORDER_BY_DOWNLOAD_COUNT, LIST_MODELS_ORDER_BY_VOTE_COUNT, LIST_MODELS_ORDER_BY_NOTEBOOK_COUNT, LIST_MODELS_ORDER_BY_PUBLISH_TIME, LIST_MODELS_ORDER_BY_CREATE_TIME, LIST_MODELS_ORDER_BY_UPDATE_TIME, LIST_MODELS_ORDER_BY_VIEW_TIME_DESC. |
| owner | `string` | Display models by a particular user or organization. |
| page_size | `int32` | Page size. |
| page_token | `string` | Page token used for pagination. |
| only_vertex_models | `bool` | Only list models that have Vertex URLs. |

##### Response: `ApiListModelsResponse`

[TABLE]

##### ○ list_model_variations

List model variations.

##### Request: `ApiListModelInstancesRequest`

|            |          |                                       |
|------------|----------|---------------------------------------|
| Field      | Type     | Description                           |
| owner_slug | `string` | The slug of the owner of the model.   |
| model_slug | `string` | The slug of the model.                |
| page_size  | `int32`  | The number of items to return.        |
| page_token | `string` | The page token to use for pagination. |

##### Response: `ApiListModelInstancesResponse`

[TABLE]

##### ○ list_model_variation_versions

List model variation versions.

##### Request: `ApiListModelInstanceVersionsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| instance_slug | `string` | The slug of the model instance. |
| framework | ModelFramework | Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON. |
| page_size | `int32` | The number of items to return. |
| page_token | `string` | The page token to use for pagination. |

##### Response: `ApiListModelInstanceVersionsResponse`

[TABLE]

##### ○ list_model_variation_version_files

List the files of a model variation version.

##### Request: `ApiListModelInstanceVersionFilesRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| instance_slug | `string` | The slug of the model instance. |
| framework | ModelFramework | Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON. |
| version_number | `int32` | The version number of the model instance. |
| page_size | `int32` | The number of items to return. |
| page_token | `string` | The page token to use for pagination. |

##### Response: `ApiListModelInstanceVersionFilesResponse`

[TABLE]

##### ○ update_model

Update a model.

##### Request: `ApiUpdateModelRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| title | `string` | The title of the model. |
| subtitle | `string` | The subtitle of the model. |
| is_private | `bool` | Whether the model is private. |
| description | `string` | The description of the model. |
| publish_time | `google.protobuf.Timestamp` | The time to publish the model. |
| provenance_sources | `string` | The provenance sources of the model. |
| update_mask | google.protobuf.FieldMask | The fields to update. |

##### Response: `ApiUpdateModelResponse`

##### ○ update_model_variation

Update a model variation.

##### Request: `ApiUpdateModelInstanceRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| owner_slug | `string` | The slug of the owner of the model. |
| model_slug | `string` | The slug of the model. |
| framework | ModelFramework | Possible values: MODEL_FRAMEWORK_UNSPECIFIED, MODEL_FRAMEWORK_TENSOR_FLOW_1, MODEL_FRAMEWORK_TENSOR_FLOW_2, MODEL_FRAMEWORK_TF_LITE, MODEL_FRAMEWORK_TF_JS, MODEL_FRAMEWORK_PY_TORCH, MODEL_FRAMEWORK_JAX, MODEL_FRAMEWORK_FLAX, MODEL_FRAMEWORK_PAX, MODEL_FRAMEWORK_MAX_TEXT, MODEL_FRAMEWORK_GEMMA_CPP, MODEL_FRAMEWORK_GGML, MODEL_FRAMEWORK_GGUF, MODEL_FRAMEWORK_CORAL, MODEL_FRAMEWORK_SCIKIT_LEARN, MODEL_FRAMEWORK_MXNET, MODEL_FRAMEWORK_ONNX, MODEL_FRAMEWORK_KERAS, MODEL_FRAMEWORK_TRANSFORMERS, MODEL_FRAMEWORK_API, MODEL_FRAMEWORK_OTHER, MODEL_FRAMEWORK_TENSOR_RT_LLM, MODEL_FRAMEWORK_TRITON. |
| instance_slug | `string` | The slug of the model instance. |
| overview | `string` | The overview of the model instance. |
| usage | `string` | The usage of the model instance. |
| fine_tunable | `bool` | Whether the model instance is fine-tunable. |
| training_data | `repeated string` | The training data of the model instance. |
| update_mask | google.protobuf.FieldMask | The fields to update. |
| license_name | `string` | The name of the license. |
| model_instance_type | ModelInstanceType | Possible values: MODEL_INSTANCE_TYPE_UNSPECIFIED, MODEL_INSTANCE_TYPE_BASE_MODEL, MODEL_INSTANCE_TYPE_KAGGLE_VARIANT, MODEL_INSTANCE_TYPE_EXTERNAL_VARIANT. |
| base_model_instance | `string` | The base model instance. |
| external_base_model_url | `string` | The external base model URL. |

##### Response: `ApiUpdateModelResponse`

### Hackathons

##### ○ download_hackathon_write_ups

Return CSV-formatted text of all hackathon submission write-ups.

##### Request: `ExportHackathonWriteUpsCsvRequest`

|                  |          |                                      |
|------------------|----------|--------------------------------------|
| Field            | Type     | Description                          |
| competition_id   | `int32`  | The ID of the hackathon competition. |
| competition_name | `string` | The name of the competition.         |

##### Response: `ExportHackathonWriteUpsCsvResponse`

##### ○ list_hackathon_write_ups

Return JSON of all hackathon submission write-ups.

##### Request: `ApiListHackathonWriteUpsRequest`

|  |  |  |
|----|----|----|
| Field | Type | Description |
| competition_name | `string` | The name of the competition. |
| hackathon_track_ids | `repeated int32` | The ID of the hackathon competition. |
| page_size | `optional int32` | Maximum number of returned write-ups per page. |
| page_token | `optional string` | Next page token. |

##### Response: `ListHackathonWriteUpsResponse`

##### ○ get_hackathon_write_up

Return JSON of hackathon write-up

##### Request: `ApiGetHackathonWriteUpRequest`

|                       |          |                                   |
|-----------------------|----------|-----------------------------------|
| Field                 | Type     | Description                       |
| competition_name      | `string` | The name of the competition.      |
| hackathon_write_up_id | `int32`  | The ID of the hackathon write-up. |

##### Response: `HackathonWriteUp`

##### ○ get_hackathon_overview

Return JSON list of hackathon overview pages

##### Request: `ApiGetHackathonOverviewRequest`

|                  |          |                              |
|------------------|----------|------------------------------|
| Field            | Type     | Description                  |
| competition_name | `string` | The name of the competition. |

##### Response: `ListPagesResponse`

##### ○ list_hackathon_tracks

Return JSON of all hackathon tracks.

##### Request: `ListHackathonTracksRequest`

|                |         |                                      |
|----------------|---------|--------------------------------------|
| Field          | Type    | Description                          |
| competition_id | `int32` | The ID of the hackathon competition. |

##### Response: `ListHackathonTracksResponse`
