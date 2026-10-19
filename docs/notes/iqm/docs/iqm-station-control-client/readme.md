> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/readme.html](https://docs.iqm.tech/4.7/iqm-station-control-client/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 734e09b59a5fb599708d9918db499b3a53a5a987c692f55c6279c6a5d797bd3e.

# iqm-station-control-client

Client library for accessing IQM Station Control.

## Developer-run tools

### Old-vs-New Sweep Results Benchmark

A standalone script is available in this package’s `scripts/` directory to verify and benchmark sweep results performance between the legacy and streaming-v2 formats:

``` bash
python scripts/run_sweep_results_benchmark.py
```

It supports automated job submission, polling, retrieval, equivalence validation, and performance timings.

#### Options

- `--legacy-job-id`: Explicit legacy format job UUID (omitting will auto-submit a new test job).

- `--streaming-job-id`: Explicit streaming-v2 format job UUID (omitting will auto-submit a new test job).

- `--core-url`: Base URL of the Core API service.

- `--station-url`: Base URL of the Station Control service.

- `--iterations`: Number of retrieval GET repetitions to measure median timing (default: 5).

#### Configuration

Configuration is read from standard environment variables, specifically:

- `IQM_SERVER_URL`

- `IQM_TOKEN` or `IQM_ADMIN_TOKEN`

- `CORE_API_SERVICE_URL` / `STATION_CONTROL_SERVICE_URL` (optional overrides)

Examples:

``` bash
# Auto-submit and compare a degenerate mock/real run of both formats
export IQM_SERVER_URL="https://your-station-control-host"
export IQM_TOKEN="<my-token>"
python scripts/run_sweep_results_benchmark.py
```

``` bash
# Compare retrieval times of two sweeps already completed on a real station
python scripts/run_sweep_results_benchmark.py \
  --legacy-job-id "fa360df4-ec73-455b-80df-8eeb3b38421c" \
  --streaming-job-id "7769e5d4-48cb-4679-b1d5-8664161f5c6b"
```

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-station-control-client
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

For example:

``` bash
uv pip install "iqm-station-control-client[pin-all]"
```

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
