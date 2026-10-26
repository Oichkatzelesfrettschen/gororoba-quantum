# Quandela scheduled runs

`.github/workflows/quandela-schedule.yml` submits approved Quandela jobs at
their scheduled times from a GitHub-hosted runner, so a case whose jobs are
spaced hours apart runs without a workstation online. The approval stays a
user decision on a written case: a schedule file merged to main carries the
approval text, and the workflow submits only the jobs it lists, once each,
in order. `scripts/qd_schedule.py` holds the logic and
`scripts/qd_schedule_tick.sh` the git plumbing; gate core-676 runs the
schedule check, the unit tests and shellcheck.

## One-time setup

1. The `quandela` environment holds the token and admits only main. Create it
   and its branch policy through REST:

   ```sh
   R=repos/Oichkatzelesfrettschen/gororoba-quantum
   gh api -X PUT "$R/environments/quandela" --input - <<'EOF'
   {"deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}
   EOF
   gh api -X POST "$R/environments/quandela/deployment-branch-policies" -f name=main -f type=branch
   ```

2. The user stores the job token as the environment secret, reading the token
   file named by `QUANDELA_TOKEN_FILE` so the token never appears on a
   command line:

   ```sh
   gh secret set QUANDELA_TOKEN --env quandela --repo Oichkatzelesfrettschen/gororoba-quantum < "$QUANDELA_TOKEN_FILE"
   ```

   A required reviewer on the environment gates every tick that enters it,
   about 96 a day, which makes unattended running impractical; the merged
   schedule is the approval, so the environment carries no reviewer.

3. The repository variable `QUANDELA_SCHEDULE_ENABLED=true` arms submitting
   ticks; any other value stops them, and a plan-only dispatch still runs.
   A tick disables the workflow once no schedule has work left, so arming a
   new schedule also enables the workflow again:

   ```sh
   R=Oichkatzelesfrettschen/gororoba-quantum
   gh api -X PUT "repos/$R/actions/workflows/quandela-schedule.yml/enable"
   gh variable set QUANDELA_SCHEDULE_ENABLED --body true --repo "$R"
   ```

4. Settings > Actions > General > "Allow GitHub Actions to create and approve
   pull requests" lets a tick open the results pull request; without it the
   tick pushes the branch and prints a warning.

## Writing a schedule

A schedule is `results/quandela/schedules/NAME.json` (schema
`qd-schedule-v1`, NAME in lowercase with hyphens) built from a written case
whose jobs exist as frozen case directories under `results/quandela/cases/`:

| field | meaning |
| --- | --- |
| `enabled` | `false` until the user approves; a disabled schedule only plans |
| `approval` | the user's approval, quoted; it reaches every `submission.json` |
| `case` | the written case document |
| `platform`, `max_total_credits` | the platform and the case's total ceiling, at least the sum of the job ceilings |
| `on_stop` | optional, `halt` (the default) or `skip`: under `skip`, for a series of independent jobs, a held or failed job keeps its record and the next job runs; a `skip` schedule names no `after` |
| `jobs[].key`, `run_name` | the job's key and the run directory suffix, `STAMP-RUN_NAME`; an enabled schedule's run names are new, since a run directory carrying one without an intent stops the job |
| `jobs[].case_dir`, `inputs_sha256` | the frozen case and the sha256 of its `cases.json` and `circuit.json` |
| `jobs[].body_sha256` | the planned request body's sha256 without `process_id`, written by `pin` |
| `jobs[].not_before`, `after` | the earliest UTC start, and an earlier job's key with `min_gap_seconds` after its provider execution end (`start_time + duration` in its `results.json`) |
| `jobs[].latest_start` | optional UTC time after which an unstarted job holds instead of waiting |
| `jobs[].max_credits`, `expected_seconds`, `per_job_credits`, `admit_statuses` | the arguments of `qd_platform.py plan` and `submit` |
| `jobs[].plan_check`, `matched_check` | the case's stop conditions as argv under `scripts/`, with `{plan}` or `{run}` |
| `jobs[].snapshot_out` | an optional after-job catalogue directory under `results/quandela/` |

The order of work:

1. Write the schedule with `enabled: false` and `body_sha256: null`, then pin
   it from a host holding the token; `pin` plans every job read-only and runs
   its plan check:
   `QUANDELA_TOKEN_FILE=... "$PYTHON" scripts/qd_schedule.py pin results/quandela/schedules/NAME.json --work DIR`.
2. Open a pull request with the schedule and the written case, and dispatch
   the workflow with `mode=plan-only` and `schedule=results/quandela/schedules/NAME.json`
   on main once the workflow file is there. The runner's `body_sha256` must
   equal the pinned one: the digest proves the runner's Perceval builds the
   request the planning host built. A difference holds the job at stage
   `body`.
3. Merging a schedule with `enabled: true` is the same act as `submit
   --approval`: it happens only after the user approves the written case in
   their own words, which the `approval` field quotes. Merge through the
   Codex loop; the next tick starts the first due job.

## What a tick does

Every 15 minutes (and on dispatch) the workflow checks out main, reads each
enabled schedule, checks out its results branch `quandela-runs/NAME` as data
and steps the first unfinished job until it waits or stops, pushing after
every step:

| state | step |
| --- | --- |
| pending, due within an hour | sleep on the runner until `not_before` when the job's `expected_seconds` and the 10-minute collection margin still fit before the tick's deadline, then step on |
| pending, due, platform or token not ready | wait: the platform reads a status outside `available` and `admit_statuses` (a calibration), or the token has a running or queued job; nothing is staged |
| pending, due, ready | stage the run directory, plan, compare `body_sha256`, run the plan check, write `KEY.intent.json` (outcome `prepared`, pushed before submit) |
| prepared by this workflow run | `qd_platform.py submit` with the schedule's approval |
| posted | `recover` writes `submission.json` |
| submitted | `collect` until 10 minutes before the tick's deadline; an unfinished job waits for the next tick |
| collected | run the matched check and the snapshot, write `KEY.receipt.json` |
| passed | the next job |
| every enabled schedule done or stopped | a full run tick (no schedule argument) whose schedules all end `done` or `stop`, or that finds no enabled schedule, disables `quandela-schedule.yml` through REST (`actions: write`) when its state reads `active`, so a tick queued behind the one that ended the series exits 0; a disabled or cancelled schedule therefore stops the timer at the next tick |

Scheduler state lives in `results/quandela/schedules/NAME/`. A tick
publishes a checkpoint even when its step fails, through the exit trap of
`qd_schedule_tick.sh`, and rebases once onto the branch tip when a commit
pushed meanwhile rejects its push. Only main's code runs: the tick copies
the data branch's state directory, the run directories its intents name and
the snapshot directories into the checkout, and refuses an intent naming
any other directory and any symbolic link. The first push of a results branch opens a pull
request; before it merges, register each run as an acquisition and claim in
`docs/state/research_state.json`, since the Quandela adapter requires every
retained run directory to appear there.

## Stops and the operator's step

| state | meaning | step |
| --- | --- | --- |
| held | a stop condition before anything was sent; `KEY.hold.json` names the stage (`plan`, `body`, `plan_check`, `submit`, `latest_start`) | under `halt`, the case's own stop rule decides; a resubmission is a schedule amendment with a new key, reviewed and merged like the first; under `skip`, the next job runs |
| interrupted | an intent from an earlier workflow run with no checkpoint, an interrupted checkpoint, or a missing run directory | read the provider's job list (MCP `qd_job_status`) for a job posted at the intent's time; the request may or may not have been posted |
| failed | the matched check or the snapshot failed; the receipt holds the output | analyze the run; under `halt` later jobs stay unsent, under `skip` the next job runs |
| foreign | a run directory with the job's run_name exists without an intent | a job ran outside the scheduler; amend the schedule |

## Limits

- GitHub starts scheduled workflows late, by tens of minutes under load, and
  drops some: the first twelve ticks of the workflow fired 9 to 55 minutes
  apart against a 15-minute cron. A tick that finds a job due within an
  hour sleeps until it, so a start window (`latest_start` after
  `not_before`) of about 90 minutes or more survives one dropped tick.
  `not_before` and `min_gap_seconds` stay lower bounds, so an analysis
  reads the provider's recorded times, never the schedule's.
- GitHub disables a scheduled workflow after 60 days without repository
  activity; a dispatch or a push re-enables it.
- `workflow_dispatch` reaches a workflow only once its file is on main.
- Local sessions and Codex share the token and see neither the concurrency
  group nor the runner's submit lock; `plan` refuses while the token has a
  running or queued job, which is the only guard between them.
- The provider's credit balance is read nowhere before a submit; the per-job
  and total ceilings bound what a schedule can spend.

## Record watch

`.github/workflows/quandela-record-watch.yml` reads the `qpu:belenos` processor
record every two hours at minute 41, in the `quandela` environment and on main
only, and submits, stages and plans nothing. `scripts/qd_record_watch.py check`
hashes the record's `perfs` object (sorted, compact JSON) and compares it with
`results/quandela/watch/qpu-belenos-held.json`, which names the held state of
2026-10-25 18:47 UTC that every later retained read reproduces. A read in the
held state, or one missing a figure the rehearsal model reads, ends the run
quietly. A changed record runs `qd_teleportation_rehearsal.live_model` at the
live figures, opens the issue "qpu:belenos performance record changed" (or
comments on an open one) with both sets of figures and the model's pooled
fidelity against F* = 0.86, and disables the workflow. A run on the recovered
chip stays plan step `recovered-chip-rehearsal` (job-01), with its own written
case and the owner's approval.

Re-arm the watch for a later held state by writing a new held file from a
retained catalogue and enabling the workflow:

```sh
"$PYTHON" scripts/qd_record_watch.py held RUN/platform-after/catalogue.json qpu:belenos \
  --out results/quandela/watch/qpu-belenos-held.json
gh api -X PUT repos/Oichkatzelesfrettschen/gororoba-quantum/actions/workflows/quandela-record-watch.yml/enable
```
