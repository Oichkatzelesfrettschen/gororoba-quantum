# Provider credits monitor

`scripts/provider_credits.py` reads the balance, quota and reset or expiry of every provider's free allotment with
read-only calls and writes one table. It submits, uploads, books and cancels nothing. Every job on every provider
still waits for the user's approved written case ([AGENTS.md, "Hardware services"](../../AGENTS.md#hardware-services));
a row with remaining credits is a fact about the account and grants no authority to spend.

## Commands

```sh
export PYTHON="${PYTHON:-python3}"   # the interpreter that holds qiskit-ibm-runtime
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/provider_credits.py snapshot [--out DIR]
"$PYTHON" scripts/provider_credits.py check-alerts [--dir DIR] [--min-remaining-fraction 0.20] \
    [--expiry-days 7] [--max-age-hours 36]
"$PYTHON" scripts/provider_credits.py --self-test
```

`snapshot` runs one reader per provider concurrently, each in its own interpreter
(`scripts/provider_credit_readers.py NAME`): the running interpreter for IBM, Kaggle, IQM, Quandela, qBraid,
BlueQubit, AWS, Azure and ANU, `QI_PYTHON` for Quantum Inspire and `OQ_PYTHON` for Open Quantum (defaults
`~/.local/share/quantuminspire/venv` and `~/.local/share/openquantum/venv`). A reader that exceeds its timeout (30 s,
90 s for IBM, whose job-metrics walk reads one record per job) or fails becomes a row reading
`read failed: <reason>`; the other readers finish. It writes `DIR/<UTC stamp>.json`, `DIR/latest.json` and
`DIR/latest.md`. DIR defaults to `${XDG_STATE_HOME:-$HOME/.local/state}/gororoba-quantum/credits`, outside the
checkout, because the files describe live account state. Error text passes a filter that drops CRNs, account ids,
UUIDs and email addresses, and no reader prints a credential.

`--self-test` is offline: fake readers prove that the table renders, that a failed reader is reported without aborting
the others, and that every threshold fires. `tests/scripts/test_provider_credits.py` runs the same logic in the pull
request suite.

## Rows

| Row | Source | Meaning |
|---|---|---|
| IBM Quantum (primary, backup) | `QiskitRuntimeService.usage()` for each saved account (`GOROROBA_IBM_ACCOUNT` unset, then `backup-ibm-quantum-platform`) | 600 s on a rolling 28-day window. No reset date exists; the instant column shows the next return of seconds, computed as the earliest future finish time of a charged job plus 28 days. |
| Kaggle GPU, TPU | `scripts/kaggle_sessions.py quota` | weekly hours, reset at the refresh time |
| IQM Resonance | GraphQL `credit(accountId)` | balance and expiry; the allotment is the documented monthly grant, used is not reported |
| Open Quantum Spark, Full | `get_credit_balance` | credit balances; the API reports no expiry, and the Spark allotment is one 90-day grant |
| Quandela Cloud | `/api/tokens/usage/report` | cumulative free credits used by the token; the remaining balance is not readable by token, so the row states usage only. The 200 free credits a month reset on the first of the month (UTC). |
| Quantum Inspire | transaction ledger | unmetered free tier; used is the ledger change (0 when nothing is charged). A dead login reads `read failed: login (run qi login --force)`. |
| qBraid credits, simulators | `/billing/credits/balance`, `/usage/simulator` | credit balance; per-simulator quota with the same figures grouped into one row, reset at `resetsAt` |
| BlueQubit | `/balance`, `/usage` | balance and the latest month's costs |
| AWS Free plan | `aws freetier get-account-plan-state`, `aws ce get-cost-and-usage` (profile `gororoba`) | remaining plan credits and expiry; used is the month-to-date UnblendedCost estimate |
| Azure Quantum | `az quantum workspace quotas` on workspace `gororoba-quantum`, subscription policies | one row per free-plan quota (Quantinuum eHQC one-time, Pasqal emulator hours monthly); the note carries the trial and spending-limit state; the trial credit balance is portal-only ([azure/README.md](../notes/azure/README.md)) |
| ANU QRNG | `docs/evidence/anu_qrng/draw-*.json` | draws of this UTC month against 100 requests; a lower bound of use, since draws retained in other checkouts or never retained do not count |
| IonQ, Quafu, Origin Quantum | none | `not readable`: the provider offers no balance route to an API key |

## Alerts

`check-alerts` prints one `ALERT <provider>: <reason>` line per finding and exits 1; no output and exit 0 means none.

- Low balance: `remaining / allotment` below `--min-remaining-fraction` (default 0.20). An IBM row at 117 of 600 s
  fires; ask whether the next case fits the seconds, and read the instant column for when seconds return.
- Expiry: a row of kind `expiry` with remaining credits that expires within `--expiry-days` (default 7). Credits
  that lapse unused are the cost of waiting; draft the case that spends them, or let them lapse. Resets and IBM
  returns never alert on their horizon, since the allotment refills.
- Read failure: any `read failed` row. Fix the named cause (`qi login --force`, a missing key file, a changed API).
- Stale snapshot: `latest.json` older than `--max-age-hours` (default 36), which means the timer stopped.

## systemd user units

Templates live in `docs/runbooks/provider-credits/`: `gororoba-credits.timer` (daily 14:00 UTC,
`Persistent=true`, `RandomizedDelaySec=10min`), `gororoba-credits.service` and `credits-run.sh`, which runs
`snapshot`, then `check-alerts`, and calls `notify-send` when it prints alerts. The unit exits nonzero while an alert
stands, so `systemctl --user status gororoba-credits.service` reads `failed` until the cause clears. `PYTHON` in the
unit is `/usr/bin/python3` (Python 3.14 with qiskit-ibm-runtime 0.50), and `GLIBC_TUNABLES` is set because the
Qiskit extensions need it. The unit's `REPO` placeholder is the absolute path of the checkout that holds the script:

```sh
repo=/home/eirikr/Projects/IBMQuantum
mkdir -p ~/.config/systemd/user
for u in gororoba-credits.service gororoba-credits.timer; do
  sed "s|REPO|$repo|g" "$repo/docs/runbooks/provider-credits/$u" > ~/.config/systemd/user/$u
done
systemctl --user daemon-reload
systemctl --user enable --now gororoba-credits.timer
systemctl --user start gororoba-credits.service
journalctl --user -u gororoba-credits.service -n 50 --no-pager
```

Read the newest table with `cat "${XDG_STATE_HOME:-$HOME/.local/state}/gororoba-quantum/credits/latest.md"`.
