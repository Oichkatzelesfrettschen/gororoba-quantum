> Full piece: [https://www.kaggle.com/docs/benchmarks](https://www.kaggle.com/docs/benchmarks)
> Retrieved 2026-10-16T03:13Z by scripts/capture_kaggle_docs.py --site (headless Chromium, pandoc);
> rendered HTML sha256 83ccb8ceada187bdc4e4d1c5716b90ceb5e2823075f36daba426dc6a5efa43c4.

Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.

[](https://www.kaggle.com/cookies)

Learn more

OK, Got it.

# How to Use Kaggle

keyboard_arrow_right[Competitions](https://www.kaggle.com/docs/competitions)

keyboard_arrow_right[Datasets](https://www.kaggle.com/docs/datasets)

[Efficient GPU Usage Tips](https://www.kaggle.com/docs/efficient-gpu-usage)

keyboard_arrow_right[Tensor Processing Units (TPUs)](https://www.kaggle.com/docs/tpu)

keyboard_arrow_right[Models](https://www.kaggle.com/docs/models)

keyboard_arrow_right[Competitions Setup](https://www.kaggle.com/docs/competitions-setup)

keyboard_arrow_right[Organizations](https://www.kaggle.com/docs/organizations)

keyboard_arrow_right[Groups](https://www.kaggle.com/docs/groups)

keyboard_arrow_right[Kaggle Packages](https://www.kaggle.com/docs/packages)

keyboard_arrow_right[Notebooks](https://www.kaggle.com/docs/notebooks)

keyboard_arrow_right[MCP Server](https://www.kaggle.com/docs/mcp)

keyboard_arrow_down

Benchmarks

[Overview](#benchmarks-overview)

keyboard_arrow_right

[Creating Tasks and Benchmarks](#intro)

keyboard_arrow_right

[Downloading Benchmark Leaderboards](#downloading-leaderboards)

keyboard_arrow_right

[Models](#benchmark-models)

[Learning resources](#Learning%20resources)

keyboard_arrow_right[Public API](https://www.kaggle.com/docs/api)

## Benchmarks

How to use Kaggle Benchmarks as your home for trustworthy AI benchmarking

content_copyCopy as Markdown

------------------------------------------------------------------------

### Overview

Kaggle seeks to be the home of a diverse ecosystem of high quality benchmarks assessing model capabilities on tasks of significant importance to the industry to help developers reliably understand and trust what works well on ML tasks. Building on Kaggle's decade-plus of experience as the home for hosting ML Competitions, which are a type of benchmark, for the industry and our partners, we will adhere to the following principles:

- Kaggle believes in the importance of **robustness**: enduring, high-value benchmarks that truly help the industry measure progress in AI are ones that can’t be easily hacked, saturated, or leaked
- Kaggle believes in the importance of **reproducibility and transparency** for ensuring the industry can trust benchmarks and evaluations. We also take in extremely high regard the trust publishers place in us as a platform.
- **Kaggle doesn’t develop benchmarks**. Our role is to independently reproduce and publicly release results, provide a model-agnostic platform that streamlines evaluation of new models on new benchmarks over time, and drive community engagement and stress testing.

[Kaggle Benchmarks](https://www.kaggle.com/benchmarks) comprises two main types of benchmarks: 1) **Research Benchmarks**, which are evals created by researchers working in AI labs, and 2) **Community Benchmarks**, which are evals created by the Kaggle community.

Both are technically identical, with the only difference being that Research Benchmarks tend to require a lot more compute. If you're a researcher who wants to host your benchmarks with us, email kaggle-benchmarks@google.com to discuss how you can get a higher quota.

------------------------------------------------------------------------

### Creating Tasks and Benchmarks

First, some key concepts about Kaggle Benchmarks:

- **Task:** A Python function defining the problem (e.g., "Solve this riddle").
- **Benchmark:** A collection of tasks that you can put together. There is no code implementation for this. This is a feature that Kaggle supports on the graphical user interface so that users can put together their own benchmarks based on the tasks that they care about

#### Creating a Task

📺 **Video Guide**: [How to create a task](https://www.youtube.com/watch?v=brIF5xGPkcM)

- 1\. Go to [Kaggle Benchmarks](https://www.kaggle.com/benchmarks) and click "Create task"
  ![Create a task](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/create_task_new.png)
- 2\. Create a new task - you can either write the code from scratch or prompt an AI to generate the code for you
  - ⚠️ Access Requirements: Please ensure your account is phone-verified to access resources such as LLM API quotas. Furthermore, accounts registered after December 15, 2025, must complete additional identity verification to execute task notebooks.

  ![Generate a task](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/generate_task.png) ![Generate a task](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/generate_task2.png)
- 3\. Once the task notebook has been created, you can make edits to it. Once it's done, you can run it in the notebook or "Save Task", which will create a Task Detail page
  ![Task notebook](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/task_notebook.png)
- 4\. The Task Detail page is where you can add a description, new models to be evaluated, compare outputs across different models, and even share it with others
  ![Task detail page](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/task_detail_page.png)

To get started creating your first task, check out the [Getting Started Notebook](https://www.kaggle.com/code/nicholaskanggoog/kaggle-benchmarks-getting-started-notebook?scriptVersionId=290215074).

#### Creating a Benchmark

Remember that a benchmark is simply multiple tasks put together into a collection.

📺 **Video Guide**: [How to create a benchmark](https://www.youtube.com/watch?v=V5tkw8zZJJc)

- 1\. Go to [Kaggle Benchmarks](https://www.kaggle.com/benchmarks) and click "Create benchmark"
  ![Create a benchmark](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/benchmark%20creation/benchmark-creation.png)
- 2\. Fill in the information in the panel. You can always change names and descriptions later!
  ![Generate a benchmark](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/benchmark%20creation/benchmark-gen.png)
- 3\. You should be brought to the Benchmark Detail page, where you will need to add tasks to your benchmark. You can add your own tasks or public tasks that others have created.
  ![Add tasks](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/benchmark%20creation/benchmark-add-task.png)
- 4\. Next, you will need to add a list of models that you want to display on the benchmark page.
  ![Add models](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/benchmark%20creation/benchmark-add-model2.png)
- 5\. Once that's done, you will see your completed Benchmark detail page. You can edit, share, and add new models and tasks!
  ![Benchmark detail page](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/benchmark%20creation/benchmark-final.png)

------------------------------------------------------------------------

### Downloading Benchmark Leaderboards

You can download the benchmark leaderboard data for your own analysis. There are two ways to access the download options:

- From the three-dot menu ("︙") in the top right of the benchmark page.
- Using the "Download" button located directly above the leaderboard table.

Both actions open a download popup that provides methods to retrieve the data.

#### Download via API

The popup provides a cURL command to download the leaderboard data as a JSON object. If the Benchmark is not public, you will need to authenticate using your Kaggle credentials.

\# Unauthenticated example\
curl -L -o ~/Downloads/open-benchmarks_scicode_leaderboard.json \\\
  https://www.kaggle.com/api/v1/benchmarks/open-benchmarks/scicode/leaderboard\
\
\# Authenticated example\
\# Export your Kaggle username and API key\
\# export KAGGLE_USERNAME=\
\# export KAGGLE_KEY=\
\
curl -L -u \$KAGGLE_USERNAME:\$KAGGLE_KEY \\\
  -o ~/Downloads/myusername_my-benchmark_leaderboard.json \\\
  https://www.kaggle.com/api/v1/benchmarks/myusername/my-benchmark/leaderboard\

#### Download as CSV

At the bottom of the download popup, you can click "Download leaderboard as csv" to directly download the data as a CSV file.

------------------------------------------------------------------------

### Models

#### Supported Models in Community Benchmarks

We continue to update the list of available models in Community Benchmarks as new models are released and old models are deprecated. We currently do not support some models (e.g. OpenAI models), but are working on growing our list over time. To query the current list of supported models, run the following command in the task notebook:

import kaggle_benchmarks as kbench\
\# returns the current list of available models to test against\
list(kbench.llms.keys())\

![Query list of available models](https://storage.googleapis.com/kaggle-media/cms/page-images/kaggle-benchmarks/available_models/query_models.png)

#### Supported Models in Research Benchmarks

Model selection within Research Benchmarks is determined by the specific evaluation and the researchers involved. Consequently, these may include supplemental models not currently supported in Community Benchmarks.

------------------------------------------------------------------------

### Learning resources

[Getting started notebook](https://www.kaggle.com/code/nicholaskanggoog/kaggle-benchmarks-getting-started-notebook?scriptVersionId=290215074)

[Kaggle Benchmarks GitHub repo](https://github.com/Kaggle/kaggle-benchmarks)

[Kaggle Community Benchmarks NotebookLM](https://notebooklm.google.com/notebook/56661d72-a74b-48cc-a2d0-08a6f7a595e8)
