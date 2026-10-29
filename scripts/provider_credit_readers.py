"""Read-only balance readers for scripts/provider_credits.py, one per provider.

Each SDK lives in its own interpreter, so provider_credits.py starts

    INTERPRETER -I scripts/provider_credit_readers.py NAME

and reads one line prefixed with SENTINEL from stdout: a JSON object with
``rows`` (the table rows of that provider) or ``error`` (one-line reason). A
reader reads credentials inside this process from the key file its provider
guide names and writes none of them, no account, organization or instance
identifier, and no email address. Every call is a GET or a listing; nothing
creates, submits, cancels or books.

Row keys: provider, allotment, used, remaining, unit, instant, instant_kind
(reset, expiry or return), source, note. Numbers are floats or None; instant
is an ISO 8601 UTC string or None.
"""

from __future__ import annotations

import calendar
import datetime as dt
import importlib
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

SENTINEL = "CREDITS-JSON "
SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
HOME = Path.home()
Row = dict[str, Any]

# docs/notes/iqm/README.md: the free tier grants up to 30 credits per month.
IQM_GRANT = 30.0
# scripts/anu_qrng.py: the ANU QRNG key allows 100 requests per calendar month.
ANU_MONTHLY_REQUESTS = 100
ANU_KEYED_HOST = "api.quantumnumbers.anu.edu.au"
# docs/notes/quandela/README.md: the Explorer offer grants 200 free credits a month.
QUANDELA_MONTHLY_CREDITS = 200.0
IBM_WINDOW_DAYS = 28
USER_AGENT = "gororoba-credits/1"


def stamp(value: dt.datetime) -> str:
    return value.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_instant(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(dt.UTC)


def number(value: Any) -> float | None:
    return None if value is None else float(value)


def row(provider: str, source: str, **fields: Any) -> Row:
    out: Row = {
        "provider": provider,
        "allotment": None,
        "used": None,
        "remaining": None,
        "unit": "",
        "instant": None,
        "instant_kind": None,
        "source": source,
        "note": "",
    }
    out.update(fields)
    return out


def next_month_start(now: dt.datetime) -> dt.datetime:
    last = calendar.monthrange(now.year, now.month)[1]
    return dt.datetime(now.year, now.month, last, tzinfo=dt.UTC) + dt.timedelta(days=1)


def http_get(url: str, headers: dict[str, str]) -> Any:
    request = urllib.request.Request(url, headers={**headers, "User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read())


def key_text(path: Path) -> str:
    value = path.expanduser().read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"key file {path.name} is empty")
    return value


def sibling(name: str) -> Any:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return importlib.import_module(name)


def ibm_returns(service: Any, now: dt.datetime) -> tuple[dt.datetime | None, float | None, float]:
    """Earliest future return of charged seconds, its size, and the charges summed over the window.

    A job's charge returns IBM_WINDOW_DAYS after the job finished (its creation when it never ran).
    """
    after = now - dt.timedelta(days=IBM_WINDOW_DAYS)
    jobs = service.jobs(limit=200, created_after=after, descending=False)

    def charge(job: Any) -> tuple[dt.datetime, float]:
        metrics = job.metrics()
        stamps = metrics.get("timestamps") or {}
        when = parse_instant(str(stamps.get("finished") or stamps.get("created")))
        seconds = float((metrics.get("usage") or {}).get("qpu_charge_time_seconds") or 0)
        return when, seconds

    with ThreadPoolExecutor(max_workers=8) as pool:
        charges = [c for c in pool.map(charge, jobs) if c[1] > 0]
    total = sum(seconds for _, seconds in charges)
    future = sorted((when + dt.timedelta(days=IBM_WINDOW_DAYS), seconds) for when, seconds in charges)
    future = [entry for entry in future if entry[0] > now]
    if not future:
        return None, None, total
    return future[0][0], future[0][1], total


def read_ibm() -> list[Row]:
    account = os.environ.get("GOROROBA_IBM_ACCOUNT", "")
    label = "IBM Quantum (backup)" if account else "IBM Quantum (primary)"
    source = "QiskitRuntimeService.usage()"
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    service = importlib.import_module("ibm_account").open_service()
    usage = service.usage()
    now = dt.datetime.now(dt.UTC)
    consumed = float(usage["usage_consumed_seconds"])
    notes = ["rolling 28-day window; no reset date"]
    instant: str | None = None
    if consumed > 0:
        try:
            when, seconds, total = ibm_returns(service, now)
            if when is not None and seconds is not None:
                instant = stamp(when)
                notes.append(f"{seconds:g} s return at that instant (job charges sum to {total:g} s of {consumed:g} s)")
            else:
                notes.append("no job charge returns inside the window")
        except Exception as error:
            notes.append(f"next return unavailable: {type(error).__name__}")
    return [
        row(
            label,
            source + " + job metrics",
            allotment=number(usage["usage_limit_seconds"]),
            used=consumed,
            remaining=number(usage["usage_remaining_seconds"]),
            unit="s",
            instant=instant,
            instant_kind="return" if instant else None,
            note="; ".join(notes),
        )
    ]


def read_kaggle() -> list[Row]:
    quota = sibling("kaggle_sessions").quota()
    refresh = quota.get("refresh")
    rows = []
    for kind, label in (("gpu_quota", "Kaggle GPU"), ("tpu_quota", "Kaggle TPU")):
        entry = quota[kind]
        used, reserved, total = entry["time_used"], entry["time_reserved"], entry["total_time_allowed"]
        rows.append(
            row(
                label,
                "kaggle_sessions.quota() (Kaggle MCP get_accelerator_quota)",
                allotment=total,
                used=used,
                remaining=round(total - used - reserved, 2),
                unit="h/week",
                instant=refresh,
                instant_kind="reset" if refresh else None,
                note=f"reserved {reserved:g} h by queued sessions" if reserved else "",
            )
        )
    return rows + kaggle_model_spend()


def kaggle_model_spend() -> list[Row]:
    # `kaggle benchmarks quota` reports Model Proxy (AI inference) spend in USD, separate from accelerator hours.
    done = subprocess.run(
        ["kaggle", "benchmarks", "quota", "--format", "json"], capture_output=True, text=True, timeout=25, check=False
    )
    if done.returncode != 0:
        first = (done.stderr.strip().splitlines() or ["kaggle benchmarks quota failed"])[-1]
        raise RuntimeError(f"kaggle benchmarks quota: {first[:160]}")

    def dollars(text: str) -> float:
        return float(text.replace("$", "").replace(",", ""))

    return [
        row(
            f"Kaggle AI models ({entry['period'].lower()})",
            "kaggle benchmarks quota (Model Proxy spend)",
            allotment=dollars(entry["total"]),
            used=dollars(entry["used"]),
            remaining=dollars(entry["remaining"]),
            unit="USD",
            instant=entry.get("refillAt") or None,
            instant_kind="reset" if entry.get("refillAt") else None,
        )
        for entry in json.loads(done.stdout)
    ]


def read_iqm() -> list[Row]:
    platform = sibling("iqm_platform")
    path = Path(os.environ.get("IQM_TOKENS_FILE") or HOME / ".config/iqm/tokens.json").expanduser()
    api = platform.Client(platform.read_tokens(path)["access_token"])
    account = api.graphql("{ me { currentAccount { id type } } }")["me"]["currentAccount"]
    credit = api.graphql(
        "query($a: UUID!){ credit(accountId: $a) { currentBalance expiresAt } }", {"a": account["id"]}
    )["credit"]
    return [
        row(
            "IQM Resonance",
            "GraphQL credit(accountId) via iqm_platform.Client",
            allotment=IQM_GRANT,
            remaining=float(credit["currentBalance"]),
            unit="credits",
            instant=stamp(parse_instant(credit["expiresAt"])) if credit.get("expiresAt") else None,
            instant_kind="expiry" if credit.get("expiresAt") else None,
            note=f"{account['type']} account; allotment is the documented monthly grant, used is not reported",
        )
    ]


def read_openquantum() -> list[Row]:
    key = Path(os.environ.get("OPENQUANTUM_SDK_KEY") or HOME / ".config/openquantum/sdk-key.json").expanduser()
    if not key.is_file():
        raise RuntimeError("Open Quantum SDK key file not found")
    os.environ["OPENQUANTUM_SDK_KEY"] = str(key)
    auth = importlib.import_module("openquantum_mcp.auth")
    management = auth.build_clients().management
    organizations = sibling("oq_platform").pages(management.list_user_organizations, "organizations")
    configured = os.environ.get("OPENQUANTUM_ORGANIZATION_ID")
    chosen = [o for o in organizations if o.id == configured] if configured else organizations[:1]
    if not chosen:
        raise RuntimeError("the SDK key reaches no organization")
    balance = management.get_credit_balance(chosen[0].id)
    grant = float(sibling("oq_platform").SPARK_GRANT_CREDITS)
    source = "management.get_credit_balance"
    return [
        row(
            "Open Quantum Spark",
            source,
            allotment=grant,
            remaining=float(balance.spark_credits),
            unit="credits",
            note="allotment is one 90-day Spark batch; expiry and used are not reported",
        ),
        row("Open Quantum Full", source, remaining=float(balance.full_credits), unit="credits"),
    ]


def read_quandela() -> list[Row]:
    named = os.environ.get("QUANDELA_TOKEN_FILE") or str(HOME / ".config/quandela/cloud-token")
    os.environ["QUANDELA_TOKEN_FILE"] = named
    platform = sibling("qd_platform")
    report = platform.usage_rows(platform.get("/api/tokens/usage/report"))
    free = sum(float(u.get("free_credits") or 0) for entry in report for u in entry.get("usage", []))
    paid = sum(float(u.get("credits") or 0) for entry in report for u in entry.get("usage", []))
    jobs = sum(int(entry.get("total_jobs") or 0) for entry in report)
    return [
        row(
            "Quandela Cloud",
            "GET /api/tokens/usage/report",
            allotment=QUANDELA_MONTHLY_CREDITS,
            used=round(free, 4),
            unit="free credits",
            instant=stamp(next_month_start(dt.datetime.now(dt.UTC))),
            instant_kind="reset",
            note=(
                f"used is cumulative over {jobs} jobs on this token, not the month's draw; "
                f"the remaining balance is not readable by token; paid credits used {paid:g}"
            ),
        )
    ]


LOGIN_DEAD = re.compile(r"login|401|expired|unauthor", re.IGNORECASE)


def read_quantum_inspire() -> list[Row]:
    platform = sibling("qi_platform")
    try:
        client = platform.Client()
        transactions = client.pages("/transactions/")
    except Exception as error:
        if LOGIN_DEAD.search(f"{type(error).__name__} {error}"):
            raise RuntimeError("login (run qi login --force)") from None
        raise
    change = sum(int(t["change"]) for t in transactions)
    return [
        row(
            "Quantum Inspire",
            "qi_platform.Client GET /transactions/",
            used=float(abs(change)),
            unit="credits",
            note=f"unmetered free tier; ledger change over {len(transactions)} transactions; hardware status not read",
        )
    ]


def read_qbraid() -> list[Row]:
    headers = {"X-API-KEY": key_text(HOME / ".config/qbraid/api-key")}
    base = "https://api-v2.qbraid.com/api/v1"
    balance = http_get(f"{base}/billing/credits/balance", headers)["data"]
    sims = http_get(f"{base}/usage/simulator", headers)["data"]
    rows = [
        row(
            "qBraid credits",
            "GET /billing/credits/balance",
            remaining=float(balance.get("qbraidCredits") or 0),
            unit="credits",
            note=(
                f"AWS-funded credits {float(balance.get('awsCredits') or 0):g}; "
                f"auto-recharge {balance.get('autoRecharge')}"
            ),
        )
    ]
    groups: dict[tuple[Any, ...], list[str]] = {}
    for sim in sims:
        shape = (sim.get("quota"), sim.get("usage"), sim.get("remaining"), sim.get("resetsAt"), sim.get("unlimited"))
        groups.setdefault(shape, []).append(str(sim.get("deviceName")))
    for (quota, usage, remaining, resets, unlimited), names in groups.items():
        shown = ", ".join(names[:4]) + (f", +{len(names) - 4} more" if len(names) > 4 else "")
        rows.append(
            row(
                f"qBraid simulators x{len(names)}",
                "GET /usage/simulator",
                allotment=None if unlimited else number(quota),
                used=number(usage),
                remaining=None if unlimited else number(remaining),
                unit="units (unnamed by the API)",
                instant=stamp(parse_instant(resets)) if resets else None,
                instant_kind="reset" if resets else None,
                note=("unlimited; " if unlimited else "") + shown,
            )
        )
    return rows


def read_bluequbit() -> list[Row]:
    headers = {"Authorization": f"SDK {key_text(HOME / '.config/bluequbit/api-key')}"}
    base = "https://app.bluequbit.io/api/v1"
    balance = http_get(f"{base}/balance", headers)["data"]
    months = http_get(f"{base}/usage", headers)["data"]["data"]
    latest = max(months) if months else None
    costs = months[latest] if latest else {}
    return [
        row(
            "BlueQubit",
            "GET /balance, GET /usage",
            remaining=float(balance.get("balance") or 0),
            unit="balance (unit unnamed by the API)",
            note=(
                f"promo {'active' if balance.get('has_promo') else 'none'}; "
                f"{latest}: costs {costs.get('costs', 0):g}, payments {costs.get('payments', 0):g}"
            ),
        )
    ]


def aws(*args: str) -> Any:
    done = subprocess.run(
        ["aws", *args, "--profile", "gororoba", "--region", "us-east-1", "--output", "json"],
        capture_output=True,
        text=True,
        timeout=25,
        check=False,
    )
    if done.returncode != 0:
        first = (done.stderr.strip().splitlines() or ["aws failed"])[-1]
        raise RuntimeError(f"aws {args[0]} {args[1]}: {first[:160]}")
    return json.loads(done.stdout)


def read_aws() -> list[Row]:
    now = dt.datetime.now(dt.UTC)
    with ThreadPoolExecutor(max_workers=2) as pool:
        plan_job = pool.submit(aws, "freetier", "get-account-plan-state")
        cost_job = pool.submit(
            aws,
            "ce",
            "get-cost-and-usage",
            "--time-period",
            f"Start={now:%Y-%m-01},End={(now + dt.timedelta(days=1)):%Y-%m-%d}",
            "--granularity",
            "MONTHLY",
            "--metrics",
            "UnblendedCost",
        )
        plan = plan_job.result()
        cost = cost_job.result()
    remaining = plan.get("accountPlanRemainingCredits") or {}
    spend = sum(float(r["Total"]["UnblendedCost"]["Amount"]) for r in cost["ResultsByTime"])
    expiry = plan.get("accountPlanExpirationDate")
    return [
        row(
            "AWS Free plan",
            "freetier get-account-plan-state, ce get-cost-and-usage",
            used=spend,
            remaining=number(remaining.get("amount")),
            unit=remaining.get("unit", "USD"),
            instant=stamp(parse_instant(expiry)) if expiry else None,
            instant_kind="expiry" if expiry else None,
            note=(
                f"{plan.get('accountPlanType')} plan {plan.get('accountPlanStatus')}; "
                "used is the month-to-date UnblendedCost, an estimate; allotment is not reported"
            ),
        )
    ]


AZURE_WORKSPACE = ("gororoba-quantum", "gororoba-quantum")


def az(*args: str) -> Any:
    done = subprocess.run(
        ["az", *args, "--only-show-errors", "--output", "json"],
        capture_output=True,
        text=True,
        timeout=25,
        check=False,
    )
    if done.returncode != 0:
        first = (done.stderr.strip().splitlines() or ["az failed"])[-1]
        raise RuntimeError(f"az {' '.join(args[:3])}: {first[:160]}")
    return json.loads(done.stdout)


def read_azure() -> list[Row]:
    group, workspace = AZURE_WORKSPACE
    now = dt.datetime.now(dt.UTC)
    with ThreadPoolExecutor(max_workers=2) as pool:
        quotas_job = pool.submit(az, "quantum", "workspace", "quotas", "-g", group, "-w", workspace)
        policy_job = pool.submit(az, "account", "show", "--query", "{id:id}")
        quotas = quotas_job.result()
        subscription = policy_job.result()["id"]
    policies = az(
        "rest",
        "--method",
        "get",
        "--url",
        f"https://management.azure.com/subscriptions/{subscription}?api-version=2022-12-01",
        "--query",
        "subscriptionPolicies",
    )
    plan = f"{policies.get('quotaId')} subscription, spending limit {policies.get('spendingLimit')}"
    rows: list[Row] = []
    for quota in quotas:
        limit = number(quota.get("limit"))
        used = number(quota.get("utilization"))
        monthly = quota.get("period") == "Monthly"
        rows.append(
            row(
                f"Azure Quantum {quota.get('providerId')} {quota.get('dimension')}",
                "az quantum workspace quotas",
                allotment=limit,
                used=used,
                remaining=None if limit is None or used is None else limit - used,
                unit=str(quota.get("dimension")),
                instant=stamp(next_month_start(now)) if monthly else None,
                instant_kind="reset" if monthly else None,
                note=f"{quota.get('period')} quota; {plan}",
            )
        )
    return rows


def read_anu() -> list[Row]:
    now = dt.datetime.now(dt.UTC)
    prefix = f"draw-{now:%Y-%m}-"
    # The keyed aqn service holds the 100-request month; the keyless legacy endpoint has its own
    # per-minute limit, so only draws whose recorded source is the keyed host count.
    count = sum(
        1
        for path in (ROOT / "docs/evidence/anu_qrng").glob(f"{prefix}*.json")
        if urllib.parse.urlsplit(json.loads(path.read_text(encoding="utf-8")).get("source", "")).hostname
        == ANU_KEYED_HOST
    )
    return [
        row(
            "ANU QRNG",
            "docs/evidence/anu_qrng/draw-*.json from the keyed host this UTC month",
            allotment=float(ANU_MONTHLY_REQUESTS),
            used=float(count),
            remaining=float(ANU_MONTHLY_REQUESTS - count),
            unit="requests/month",
            instant=stamp(next_month_start(now)),
            instant_kind="reset",
            note="used is a lower bound: it counts the draws retained in this checkout, so remaining is an upper bound",
        )
    ]


READERS: dict[str, Callable[[], list[Row]]] = {
    "ibm": read_ibm,
    "kaggle": read_kaggle,
    "iqm": read_iqm,
    "openquantum": read_openquantum,
    "quandela": read_quandela,
    "quantum-inspire": read_quantum_inspire,
    "qbraid": read_qbraid,
    "bluequbit": read_bluequbit,
    "aws": read_aws,
    "azure": read_azure,
    "anu": read_anu,
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in READERS:
        raise SystemExit(f"usage: provider_credit_readers.py {{{'|'.join(READERS)}}}")
    try:
        payload: dict[str, Any] = {"rows": READERS[argv[1]]()}
    except Exception as error:
        reason = str(error)
        payload = {"error": reason if type(error) is RuntimeError and reason else f"{type(error).__name__}: {reason}"}
    print(SENTINEL + json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
