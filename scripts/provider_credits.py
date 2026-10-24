"""Read-only monitor of the free quantum and compute allotments of every provider.

    "$PYTHON" scripts/provider_credits.py snapshot [--out DIR]
    "$PYTHON" scripts/provider_credits.py check-alerts [--dir DIR] [--min-remaining-fraction F]
        [--expiry-days N] [--max-age-hours H]
    "$PYTHON" scripts/provider_credits.py --self-test

snapshot runs one reader per provider (scripts/provider_credit_readers.py) in
that provider's own interpreter, concurrently, each under a timeout. A reader
that times out or fails becomes a row reading ``read failed: <reason>`` and
the other readers continue. It writes ``DIR/<UTC stamp>.json``,
``DIR/latest.json`` and ``DIR/latest.md``. DIR defaults to
``${XDG_STATE_HOME:-$HOME/.local/state}/gororoba-quantum/credits``: the files
describe live account state and stay out of every checkout. Every reader
issues reads only; no job, upload, booking or cancellation leaves this tool.

check-alerts reads DIR/latest.json and prints one ``ALERT`` line per row whose
remaining allotment is below the fraction of its allotment, whose expiry falls
within the horizon with allotment still unspent, whose read failed, or whose
snapshot is older than the age limit. It exits 1 when any line printed, 0
otherwise. A reset or a return of seconds never alerts on its horizon: the
allotment refills, so only a low balance matters there.

Interpreters (environment overrides): repo readers run under the interpreter
that runs this script; QI_PYTHON (default ~/.local/share/quantuminspire/venv)
and OQ_PYTHON (default ~/.local/share/openquantum/venv) serve their SDKs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SENTINEL = "CREDITS-JSON "
SCRIPTS = Path(__file__).resolve().parent
READERS_FILE = SCRIPTS / "provider_credit_readers.py"
SCHEMA = "provider-credits-v1"
READ_TIMEOUT_SECONDS = 30
IBM_READ_TIMEOUT_SECONDS = 90
DEFAULT_MIN_REMAINING_FRACTION = 0.20
DEFAULT_EXPIRY_DAYS = 7.0
DEFAULT_MAX_AGE_HOURS = 36.0
GLIBC_TUNABLE = "glibc.rtld.optional_static_tls=4096"
HOME = Path.home()

Row = dict[str, Any]
Reader = Callable[[], list[Row]]

NOT_READABLE = (
    ("IonQ", "organization usage needs the full organization id and credit is admin-only (docs/notes/ionq)"),
    ("Quafu", "the token API exposes no quota; it sits behind the web session (docs/notes/quafu)"),
    (
        "Origin Quantum",
        "pyqpanda3 has no balance call; free machine seconds show in the console (docs/notes/originquantum)",
    ),
)

# Strings from error text pass through this filter before they reach a file: it drops identifiers
# the hard rules keep out of every record (CRNs, 12-digit account ids, hex and UUID ids, emails).
SCRUBS = (
    (re.compile(r"crn:[^\s,;\"']+"), "<crn>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}\b"), "<id>"),
    (re.compile(r"\b[0-9a-fA-F]{24,}\b"), "<id>"),
    (re.compile(r"\b\d{12}\b"), "<id>"),
)


def scrub(text: str, limit: int = 220) -> str:
    for pattern, replacement in SCRUBS:
        text = pattern.sub(replacement, text)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def stamp(value: dt.datetime) -> str:
    return value.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_instant(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(dt.UTC)


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(HOME / ".local/state")
    return Path(base) / "gororoba-quantum" / "credits"


@dataclass
class ReaderSpec:
    """One provider read: its table label, the reader callable and the timeout that bounds it."""

    label: str
    read: Reader
    timeout: float = READ_TIMEOUT_SECONDS


def subprocess_reader(
    name: str, interpreter: str, extra_env: dict[str, str] | None = None, timeout: float = READ_TIMEOUT_SECONDS
) -> Reader:
    """A Reader that runs provider_credit_readers.py NAME under INTERPRETER and decodes its sentinel line."""

    def read() -> list[Row]:
        env = {**os.environ, "GLIBC_TUNABLES": GLIBC_TUNABLE, **(extra_env or {})}
        try:
            done = subprocess.run(
                [interpreter, "-I", str(READERS_FILE), name],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"timed out after {timeout:g} s") from None
        except OSError as error:
            raise RuntimeError(f"interpreter unavailable ({type(error).__name__})") from None
        lines = [line for line in done.stdout.splitlines() if line.startswith(SENTINEL)]
        if not lines:
            tail = (done.stderr.strip().splitlines() or ["no output"])[-1]
            raise RuntimeError(f"reader exited {done.returncode} without a result: {tail}")
        payload = json.loads(lines[-1][len(SENTINEL) :])
        if "error" in payload:
            raise RuntimeError(str(payload["error"]))
        rows: list[Row] = payload["rows"]
        return rows

    return read


def venv_python(env_name: str, default_venv: str) -> str:
    return os.environ.get(env_name) or str(HOME / ".local/share" / default_venv / "bin/python")


def real_specs() -> list[ReaderSpec]:
    here = sys.executable
    return [
        ReaderSpec(
            "IBM Quantum (primary)",
            subprocess_reader("ibm", here, {"GOROROBA_IBM_ACCOUNT": ""}, IBM_READ_TIMEOUT_SECONDS),
            IBM_READ_TIMEOUT_SECONDS,
        ),
        ReaderSpec(
            "IBM Quantum (backup)",
            subprocess_reader(
                "ibm", here, {"GOROROBA_IBM_ACCOUNT": "backup-ibm-quantum-platform"}, IBM_READ_TIMEOUT_SECONDS
            ),
            IBM_READ_TIMEOUT_SECONDS,
        ),
        ReaderSpec("Kaggle", subprocess_reader("kaggle", here)),
        ReaderSpec("IQM Resonance", subprocess_reader("iqm", here)),
        ReaderSpec(
            "Open Quantum",
            subprocess_reader("openquantum", venv_python("OQ_PYTHON", "openquantum/venv")),
        ),
        ReaderSpec("Quandela Cloud", subprocess_reader("quandela", here)),
        ReaderSpec(
            "Quantum Inspire",
            subprocess_reader("quantum-inspire", venv_python("QI_PYTHON", "quantuminspire/venv")),
        ),
        ReaderSpec("qBraid", subprocess_reader("qbraid", here)),
        ReaderSpec("BlueQubit", subprocess_reader("bluequbit", here)),
        ReaderSpec("AWS Free plan", subprocess_reader("aws", here)),
        ReaderSpec("ANU QRNG", subprocess_reader("anu", here)),
    ]


def failed_row(label: str, reason: str) -> Row:
    return {
        "provider": label,
        "allotment": None,
        "used": None,
        "remaining": None,
        "unit": "",
        "instant": None,
        "instant_kind": None,
        "source": "",
        "note": "",
        "status": f"read failed: {scrub(reason)}",
    }


def clean_row(raw: Row) -> Row:
    out = dict(raw)
    for key in ("provider", "unit", "source", "note"):
        out[key] = scrub(str(out.get(key) or ""), 400)
    out["status"] = "ok"
    return out


def collect(specs: Sequence[ReaderSpec]) -> list[Row]:
    """Run every reader concurrently (subprocess waits are I/O-bound); a failure becomes one failed row."""

    def one(spec: ReaderSpec) -> list[Row]:
        try:
            return [clean_row(r) for r in spec.read()]
        except Exception as error:
            reason = str(error) or type(error).__name__
            if not isinstance(error, (RuntimeError, TimeoutError)):
                reason = f"{type(error).__name__}: {reason}"
            return [failed_row(spec.label, reason)]

    with ThreadPoolExecutor(max_workers=max(1, len(specs))) as pool:
        groups = list(pool.map(one, specs))
    rows = [r for group in groups for r in group]
    for provider, reason in NOT_READABLE:
        rows.append({**failed_row(provider, ""), "status": f"not readable: {reason}"})
    return rows


def cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def render_table(rows: Sequence[Row], taken: str) -> str:
    head = "| provider | allotment | used | remaining | unit | reset or expiry (UTC) | source call | read status |"
    lines = [
        "# Provider credits",
        "",
        f"Snapshot taken {taken}. Read-only; see docs/runbooks/provider-credits.md.",
        "",
        head,
        "|---|---:|---:|---:|---|---|---|---|",
    ]
    notes = []
    for r in rows:
        when = "-" if not r.get("instant") else f"{r['instant_kind']} {r['instant']}"
        cells = [
            r["provider"],
            cell(r["allotment"]),
            cell(r["used"]),
            cell(r["remaining"]),
            r["unit"] or "-",
            when,
            r["source"] or "-",
            r["status"],
        ]
        lines.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
        if r.get("note"):
            notes.append(f"- {r['provider']}: {r['note']}")
    if notes:
        lines += ["", "Notes", "", *notes]
    return "\n".join(lines) + "\n"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def snapshot(out: Path, specs: Sequence[ReaderSpec] | None = None, now: dt.datetime | None = None) -> dict[str, Any]:
    taken = now or utc_now()
    rows = collect(specs if specs is not None else real_specs())
    taken_utc = stamp(taken)
    document: dict[str, Any] = {"schema": SCHEMA, "taken_utc": taken_utc, "rows": rows}
    text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    write_atomic(out / f"{taken:%Y%m%dT%H%M%SZ}.json", text)
    write_atomic(out / "latest.json", text)
    write_atomic(out / "latest.md", render_table(rows, taken_utc))
    return document


def alerts(
    document: dict[str, Any],
    now: dt.datetime,
    min_fraction: float = DEFAULT_MIN_REMAINING_FRACTION,
    expiry_days: float = DEFAULT_EXPIRY_DAYS,
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
) -> list[str]:
    lines = []
    age = now - parse_instant(document["taken_utc"])
    if age > dt.timedelta(hours=max_age_hours):
        lines.append(f"ALERT snapshot: taken {age.total_seconds() / 3600:.1f} h ago, limit {max_age_hours:g} h")
    for r in document["rows"]:
        name, status = r["provider"], r["status"]
        if status.startswith("read failed"):
            lines.append(f"ALERT {name}: {status}")
            continue
        if status != "ok":
            continue
        allotment, remaining = r.get("allotment"), r.get("remaining")
        if allotment and remaining is not None and remaining / allotment < min_fraction:
            lines.append(
                f"ALERT {name}: {remaining:g} of {allotment:g} {r['unit']} remain "
                f"({remaining / allotment:.1%}, threshold {min_fraction:.0%})"
            )
        if r.get("instant_kind") == "expiry" and r.get("instant") and (remaining or 0) > 0:
            left = parse_instant(r["instant"]) - now
            if left <= dt.timedelta(days=expiry_days):
                lines.append(
                    f"ALERT {name}: {remaining:g} {r['unit']} expire {r['instant']} "
                    f"in {left.total_seconds() / 86400:.1f} d (horizon {expiry_days:g} d)"
                )
    return lines


def check_alerts(directory: Path, now: dt.datetime | None = None, **limits: float) -> list[str]:
    path = directory / "latest.json"
    if not path.is_file():
        return [f"ALERT snapshot: {path.name} missing; run snapshot first"]
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != SCHEMA:
        return [f"ALERT snapshot: {path.name} has schema {document.get('schema')!r}"]
    return alerts(document, now or utc_now(), **limits)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"self-test: {message}")


def self_test() -> None:
    """Offline: fake readers prove the table, failure isolation, thresholds and the scrub filter."""
    now = dt.datetime(2026, 10, 24, 12, 0, tzinfo=dt.UTC)

    def ok() -> list[Row]:
        return [
            {
                "provider": "Fake low",
                "allotment": 600.0,
                "used": 540.0,
                "remaining": 60.0,
                "unit": "s",
                "instant": "2026-10-30T00:00:00Z",
                "instant_kind": "return",
                "source": "fake.call",
                "note": "n",
            },
            {
                "provider": "Fake expiring",
                "allotment": 30.0,
                "used": 13.0,
                "remaining": 17.0,
                "unit": "credits",
                "instant": "2026-10-28T00:00:00Z",
                "instant_kind": "expiry",
                "source": "fake.call",
                "note": "",
            },
            {
                "provider": "Fake resetting",
                "allotment": 30.0,
                "used": 0.0,
                "remaining": 30.0,
                "unit": "h",
                "instant": "2026-10-25T00:00:00Z",
                "instant_kind": "reset",
                "source": "fake.call",
                "note": "",
            },
        ]

    def boom() -> list[Row]:
        raise RuntimeError("login (run qi login --force)")

    def hang() -> list[Row]:
        raise TimeoutError("timed out after 30 s")

    def leaky() -> list[Row]:
        raise ValueError("denied for a@b.example in crn:v1:bluemix:public:x:y 123456789012")

    specs = [
        ReaderSpec("Fake ok", ok),
        ReaderSpec("Fake dead", boom),
        ReaderSpec("Fake slow", hang),
        ReaderSpec("Fake leaky", leaky),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "credits"
        document = snapshot(out, specs, now)
        by = {r["provider"]: r for r in document["rows"]}
        require(by["Fake dead"]["status"] == "read failed: login (run qi login --force)", "failed reader text")
        require(by["Fake slow"]["status"] == "read failed: timed out after 30 s", "timeout text")
        require(by["Fake low"]["status"] == "ok", "a failed reader aborted the others")
        require(
            all(r["status"].startswith("not readable") for r in document["rows"] if r["provider"] == "IonQ"), "IonQ"
        )
        leak = by["Fake leaky"]["status"]
        require("a@b.example" not in leak and "crn:" not in leak and "123456789012" not in leak, "scrub")
        table = (out / "latest.md").read_text(encoding="utf-8")
        require(
            "| Fake low | 600 | 540 | 60 | s | return 2026-10-30T00:00:00Z | fake.call | ok |" in table, "table row"
        )
        require("read failed: login" in table and "not readable:" in table, "table statuses")
        require(len(list(out.glob("2026*.json"))) == 1 and (out / "latest.json").is_file(), "snapshot files")
        found = check_alerts(out, now)
        require(any(line.startswith("ALERT Fake low") and "10.0%" in line for line in found), "low-balance alert")
        require(any(line.startswith("ALERT Fake expiring") for line in found), "expiry alert")
        require(any(line.startswith("ALERT Fake dead") for line in found), "failed-read alert")
        require(not any("Fake resetting" in line for line in found), "a reset must not alert on its horizon")
        require(not any("IonQ" in line for line in found), "not-readable rows do not alert")
        quiet = check_alerts(out, now, min_fraction=0.05, expiry_days=1)
        require(not any("Fake low" in line or "Fake expiring" in line for line in quiet), "overridable thresholds")
        stale = check_alerts(out, now + dt.timedelta(hours=48))
        require(stale[0].startswith("ALERT snapshot"), "stale snapshot alert")
        require(check_alerts(Path(tmp) / "none")[0].startswith("ALERT snapshot"), "missing snapshot alert")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="offline check with fake readers")
    sub = parser.add_subparsers(dest="command")
    snap = sub.add_parser("snapshot", help="read every provider and write the snapshot files")
    snap.add_argument("--out", type=Path, default=None, help="output directory (default: XDG state directory)")
    check = sub.add_parser("check-alerts", help="exit 1 and print a line per alert")
    check.add_argument("--dir", type=Path, default=None, help="snapshot directory (default: XDG state directory)")
    check.add_argument("--min-remaining-fraction", type=float, default=DEFAULT_MIN_REMAINING_FRACTION)
    check.add_argument("--expiry-days", type=float, default=DEFAULT_EXPIRY_DAYS)
    check.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print("provider_credits self-test passed")
        return 0
    if args.command == "snapshot":
        out = args.out or state_dir()
        document = snapshot(out)
        failed = sum(1 for r in document["rows"] if r["status"].startswith("read failed"))
        print(f"wrote {out}/latest.md ({len(document['rows'])} rows, {failed} read failed)")
        return 0
    if args.command == "check-alerts":
        lines = check_alerts(
            args.dir or state_dir(),
            min_fraction=args.min_remaining_fraction,
            expiry_days=args.expiry_days,
            max_age_hours=args.max_age_hours,
        )
        for line in lines:
            print(line)
        return 1 if lines else 0
    parser.error("a command or --self-test is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
