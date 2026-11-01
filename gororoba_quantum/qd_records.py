"""Offline reader of a retained Quandela Cloud run directory.

A run directory holds cases.json (the case manifest), the circuit file it
names, job-body.json (the body Perceval sent), submission.json (the receipt
with the operator's approval), results.json (the collection) and
raw/result.json (the service's raw answer, whose sha256 the collection
records). read_run applies the rules every consumer shares: receipt binding,
circuit and body digests, platform admission, a terminal status, the raw
result against the collection's summary and the manifest's budgets, and
returns the parsed records with the facts the registry keeps. The credit
charge is an account fact that scripts/qd_platform.py adds, and that module
re-exports every name here so its callers keep working. The module reads
files only, needs the standard library alone, and never authenticates or
reaches the service.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "results/quandela/runs"


def keys(value: Any) -> set[str]:
    """Every mapping key at any depth of a JSON value."""
    if isinstance(value, dict):
        return set(value) | {k for item in value.values() for k in keys(item)}
    if isinstance(value, list):
        return {k for item in value for k in keys(item)}
    return set()


def _optional_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def _optional_json(data: bytes | None) -> Any:
    return None if data is None else json.loads(data)


@dataclass(frozen=True)
class Records:
    """The files of one run directory as written, before any rule; None marks a file the directory lacks.

    bytes_of and json_of raise RecordError for a missing file, so a loader that needs a file names it."""

    directory: Path
    interrupted: bool
    manifest_bytes: bytes | None
    circuit_bytes: bytes | None
    body_bytes: bytes | None
    submission_bytes: bytes | None
    collected_bytes: bytes | None
    raw: bytes | None

    def bytes_of(self, name: str) -> bytes:
        data = {
            "cases.json": self.manifest_bytes,
            "circuit": self.circuit_bytes,
            "job-body.json": self.body_bytes,
            "submission.json": self.submission_bytes,
            "results.json": self.collected_bytes,
            "raw/result.json": self.raw,
        }[name]
        if data is None:
            raise RecordError(f"Quandela run {self.directory.name}: {name} is missing")
        return data

    def json_of(self, name: str) -> Any:
        return json.loads(self.bytes_of(name))

    @property
    def manifest(self) -> Any:
        return _optional_json(self.manifest_bytes)

    @property
    def submission(self) -> Any:
        return _optional_json(self.submission_bytes)

    @property
    def collected(self) -> Any:
        return _optional_json(self.collected_bytes)

    @property
    def body(self) -> Any:
        return _optional_json(self.body_bytes)


def load_run(directory: Path) -> Records:
    """Read the files of one run directory without judging them; validate_run applies the rules."""
    manifest_bytes = _optional_bytes(directory / "cases.json")
    manifest = _optional_json(manifest_bytes)
    circuit_name = manifest.get("circuit", {}).get("file") if isinstance(manifest, dict) else None
    circuit_bytes = _optional_bytes(directory / circuit_name) if isinstance(circuit_name, str) else None
    return Records(
        directory=directory,
        interrupted=(directory / "submission-state.json").is_file(),
        manifest_bytes=manifest_bytes,
        circuit_bytes=circuit_bytes,
        body_bytes=_optional_bytes(directory / "job-body.json"),
        submission_bytes=_optional_bytes(directory / "submission.json"),
        collected_bytes=_optional_bytes(directory / "results.json"),
        raw=_optional_bytes(directory / "raw" / "result.json"),
    )


FORBIDDEN_KEYS = (
    "token",
    "token_id",
    "token_label",
    "token_value",
    "creator_id",
    "user_id",
    "entity_id",
    "email",
)

CASES_SCHEMAS = ("qd-box-kite-cases-v1", "qd-belenos-mesh-cases-v1", "qd-bdsc-cases-v1", "qd-hypercomplex-cases-v1")

CIRCUIT_SCHEMA = "qd-circuit-v1"

TEMPLATE_CIRCUIT_SCHEMA = "qd-template-circuit-v1"

CIRCUIT_SCHEMAS = (CIRCUIT_SCHEMA, "qd-mesh-circuit-v1", TEMPLATE_CIRCUIT_SCHEMA)

SUBMISSION_SCHEMA = "qd-submission-v1"

COLLECTION_SCHEMA = "qd-collection-v1"

TERMINAL = ("completed", "error", "canceled")

RESULT_LIMIT = 64 << 20

STATE_PATTERN = re.compile(r"\|(\d+(?:,\d+)*)>=(\d+)")


class RecordError(RuntimeError):
    """A Quandela Cloud read failed; the message carries the route and the service's answer."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_case(records: Records) -> tuple[dict[str, Any], dict[str, Any], str]:
    """cases.json, circuit.json and the cases.json sha256 of loaded records; raises when the circuit differs."""
    case_dir = records.directory
    manifest: dict[str, Any] = records.json_of("cases.json")
    if manifest.get("schema") not in CASES_SCHEMAS:
        raise RecordError(f"{case_dir}/cases.json schema {manifest.get('schema')!r} is not a Quandela case")
    circuit_bytes = records.circuit_bytes
    if circuit_bytes is None or sha256_bytes(circuit_bytes) != manifest["circuit"]["sha256"]:
        raise RecordError(f"{case_dir}: circuit.json differs from its cases.json sha256")
    circuit: dict[str, Any] = json.loads(circuit_bytes)
    if circuit.get("schema") not in CIRCUIT_SCHEMAS:
        raise RecordError(f"{case_dir}: circuit schema {circuit.get('schema')!r}")
    return manifest, circuit, sha256_bytes(records.bytes_of("cases.json"))


def load_case(case_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    """cases.json, circuit.json and the cases.json sha256; raises when the circuit differs from its digest."""
    return validate_case(load_run(case_dir))


def seed_value(seed: Any, owner: str) -> int:
    """A compilation seed as the service takes it: a non-negative integer."""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise RecordError(f"{owner}: compilation_seed {seed!r} is not a non-negative integer")
    return seed


def iteration_form(manifest: dict[str, Any]) -> str:
    """How a case's iterations differ: "single" (one computation), "mesh" (each binds its own phases), "seeded"
    (a fixed circuit whose iterations set only their compilation_seed and, optionally, their own budgets) or
    "phase" (phi = k pi/4).

    A one-iteration case is one computation unless its manifest sets "iterator": true, which sends its one
    seeded setting as a ComputationIterator holding one entry, the payload class of every iterated job.

    A non-mesh iterated case with settings is seeded only when every setting names a valid compilation_seed and
    nothing else but its name, and the settings count its iterations. A seeded case names per-iteration
    max_samples and max_shots on every setting or on none; named budgets are positive integers with
    max_shots >= max_samples that sum to the manifest's. Any other settings list raises.
    """
    owner = manifest["job"]
    steps = manifest.get("iterations", 1)
    iterator = manifest.get("iterator", False)
    if iterator is not False and (iterator is not True or steps != 1 or manifest.get("gate_form") == "mesh"):
        raise RecordError(f"{owner}: iterator is true only on a one-iteration seeded case, not {iterator!r}")
    if steps == 1 and not iterator:
        return "single"
    if iterator and manifest.get("settings") is None:
        raise RecordError(f"{owner}: a one-entry iterator names its setting")
    if manifest.get("gate_form") == "mesh":
        return "mesh"
    if manifest.get("gate_form") == "template":
        template_settings = manifest.get("settings")
        if not isinstance(template_settings, list) or len(template_settings) != steps:
            raise RecordError(f"{owner}: {steps} template iterations need {steps} settings")
        for setting in template_settings:
            if not isinstance(setting.get("circuit_params"), dict) or "column" not in setting:
                raise RecordError(f"{owner}/{setting.get('name')}: a template setting binds circuit_params and column")
            seed_value(setting.get("compilation_seed", 0), f"{owner}/{setting.get('name')}")
        return "template"
    settings = manifest.get("settings")
    if settings is None:
        return "phase"
    if not isinstance(settings, list) or len(settings) != steps:
        raise RecordError(f"{owner}: {steps} iterations need {steps} settings")
    plain, budgeted = {"name", "compilation_seed"}, {"name", "compilation_seed", "max_samples", "max_shots"}
    keys = {frozenset(setting) if isinstance(setting, dict) else frozenset() for setting in settings}
    if keys not in ({frozenset(plain)}, {frozenset(budgeted)}):
        raise RecordError(
            f"{owner}: every seeded iteration names its name and compilation_seed, and all or none their budgets"
        )
    for setting in settings:
        seed_value(setting["compilation_seed"], f"{owner}/{setting['name']}")
    if keys == {frozenset(budgeted)}:
        for setting in settings:
            samples, shots = setting["max_samples"], setting["max_shots"]
            if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in (samples, shots)) or shots < samples:
                raise RecordError(f"{owner}/{setting['name']}: budgets {samples!r} samples, {shots!r} shots")
        for key in ("max_samples", "max_shots"):
            if sum(setting[key] for setting in settings) != manifest[key]:
                raise RecordError(f"{owner}: per-iteration {key} do not sum to the manifest's {manifest[key]}")
    return "seeded"


def expected_iterations(manifest: dict[str, Any]) -> int | None:
    """The iterations an iterated case sends, or None for a one-computation case."""
    return None if iteration_form(manifest) == "single" else int(manifest.get("iterations", 1))


# Count-less partial collections retained before results.json carried failed iterations; their job ids are bound to
# submission.json, and every later collection must carry the iterations field.


ITERATIONS_PREDATING_JOBS = frozenset(
    {
        "03dd195b-b429-4ef1-be96-98005617343c",
        "90712931-1b5a-4c14-bdd0-95e01ac02292",
        "c2edef5d-5e6f-4161-83fc-aadd024171fb",
    }
)


def predates(retained: dict[str, Any], summary: dict[str, Any], key: str) -> bool:
    """Whether a retained collection omits summary[key] because it was written before the field existed.

    shots_used is derived from the raw bytes, so a record without it takes it
    from the raw result. Only the count-less partial records of
    ITERATIONS_PREDATING_JOBS may omit their failed iteration entries.
    """
    if key in retained or key not in summary:
        return False
    if key == "shots_used":
        return True
    return (
        key == "iterations"
        and summary.get("partial") is True
        and not summary.get("counts")
        and retained.get("job_id") in ITERATIONS_PREDATING_JOBS
    )


def parse_counts(results: str) -> dict[str, int]:
    """Counts of a serialized Perceval BSCount, ':PCVL:BSCount:{|..>=n;...}', optionally zipped.

    Only plain Fock states with integer counts are accepted; any other tag or
    annotation raises, because perceval.serialization.deserialize evaluates
    parameter expressions through sympy and never sees service data here.
    """
    text = results
    if text.startswith(":PCVL:zip:"):
        stream = zlib.decompressobj()
        raw = stream.decompress(base64.b64decode(text[len(":PCVL:zip:") :], validate=True), RESULT_LIMIT)
        if stream.unconsumed_tail:
            raise RecordError(f"a zipped result exceeds {RESULT_LIMIT} bytes")
        if not stream.eof or stream.unused_data:
            raise RecordError("a zipped result must contain exactly one complete compressed stream")
        text = raw.decode("ascii")
    prefix = ":PCVL:BSCount:"
    if not text.startswith(prefix) or not (text.endswith("}") and text[len(prefix)] == "{"):
        raise RecordError(f"result is not a BSCount: {text[:80]!r}")
    body = text[len(prefix) + 1 : -1]
    counts: dict[str, int] = {}
    for item in body.split(";") if body else []:
        match = STATE_PATTERN.fullmatch(item)
        if match is None or match[1] in counts:
            raise RecordError(f"result entry {item[:80]!r} is not a unique Fock state count")
        counts[match[1]] = int(match[2])
    return counts


def scalar_tree(value: Any) -> Any:
    """JSON scalars and nested dicts and lists of them; anything else becomes its type name."""
    if isinstance(value, dict):
        return {str(k): scalar_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scalar_tree(v) for v in value]
    if value is None or isinstance(value, bool | int | float | str):
        return value
    return type(value).__name__


def result_summary(
    result_bytes: bytes, job: str, status: dict[str, Any], complete: bool = True, expected: int | None = None
) -> dict[str, Any]:
    """The counts and scalar fields of a raw /result answer, parsed without Perceval and bound to its job.

    The answer's job_id must be the submitted job and its shots must agree
    with any non-null status shots. A partial result (error or canceled job)
    without serialized counts is summarized as partial with no counts. A
    partial iterated result keeps every entry at its position: a counted
    iteration as a completed job would, an iteration answered with the
    worker's error text as "error", and an unreadable entry as "malformed".
    When the case expects more iterations than the answer holds, one "missing"
    entry per absent iteration follows the answered ones; the answer names no
    position, so a missing entry carries no attribution. None of these carries
    counts, so a failed iteration never reads as a counted one.
    """
    answer = json.loads(result_bytes)
    if not isinstance(answer, dict) or answer.get("job_id") != job:
        raise RecordError(
            f"the result answers job {answer.get('job_id') if isinstance(answer, dict) else None}, not {job}"
        )
    shots = answer.get("shots")
    # A job that ended without completing (error, canceled) may answer shots null: no count, kept as null.
    if not (shots is None and not complete) and (not isinstance(shots, int) or shots < 0):
        raise RecordError(f"the result of job {job} carries shots {shots!r}")
    if status.get("shots") is not None and status["shots"] != shots:
        raise RecordError(f"job {job}: status shots {status['shots']} differ from the result's {shots}")
    serialized = answer.get("results")
    inner = json.loads(serialized) if isinstance(serialized, str) and serialized else None
    iterations: list[dict[str, Any]] | None = None
    if isinstance(inner, dict) and isinstance(inner.get("results_list"), list):
        # An iterated job answers one entry per iteration; counts add up, and
        # each entry keeps its own counts and its iteration's scalar fields.
        iterations = []
        merged: dict[str, int] = {}
        for entry in inner["results_list"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("results"), str):
                if complete:
                    raise RecordError(f"job {job}: an iteration result carries no serialized counts")
                malformed = {"malformed": type(entry.get("results") if isinstance(entry, dict) else entry).__name__}
                if isinstance(entry, dict) and isinstance(entry.get("iteration"), dict):
                    malformed["iteration"] = scalar_tree(entry["iteration"])
                iterations.append(malformed)
                continue
            iteration = entry.get("iteration") if isinstance(entry.get("iteration"), dict) else {}
            fields = {k: v for k, v in entry.items() if k not in ("results", "iteration")}
            # A job that ended without completing can answer an iteration with the worker's error text.
            if not complete and not entry["results"].startswith(":PCVL:"):
                iterations.append(
                    {
                        "iteration": scalar_tree(iteration),
                        "error": entry["results"][:2000],
                        "result_fields": scalar_tree(fields),
                    }
                )
                continue
            part = parse_counts(entry["results"])
            for state, n in part.items():
                merged[state] = merged.get(state, 0) + n
            iterations.append(
                {
                    "iteration": scalar_tree(iteration),
                    "counts": part,
                    "samples": sum(part.values()),
                    "result_fields": scalar_tree(fields),
                }
            )
        if expected is not None and complete and len(iterations) != expected:
            raise RecordError(f"job {job}: a completed job answers {len(iterations)} iterations of {expected}")
        if expected is not None and not complete:
            if len(iterations) > expected:
                raise RecordError(f"job {job}: {len(iterations)} iterations answer a case of {expected}")
            iterations.extend({"missing": True} for _ in range(expected - len(iterations)))
        inner = {**{k: v for k, v in inner.items() if k != "results_list"}, "results": None}
        counts = merged
    elif not isinstance(inner, dict) or not isinstance(inner.get("results"), str):
        if complete:
            raise RecordError("the result carries no serialized counts")
        return {"shots": shots, "partial": True, "counts": {}, "samples": 0, "result_fields": {}}
    else:
        if not complete and not inner["results"].startswith(":PCVL:"):
            return {
                "shots": shots,
                "partial": True,
                "counts": {},
                "samples": 0,
                "error": inner["results"][:2000],
                "result_fields": scalar_tree({key: value for key, value in inner.items() if key != "results"}),
            }
        counts = parse_counts(inner["results"])
    # An iterated answer's top-level shots is one iteration's max_shots; each
    # entry reports the shots it used, and their sum is what the job consumed.
    used = shots
    failed = False
    if iterations is not None:
        counted = [entry for entry in iterations if "counts" in entry]
        per = [entry["result_fields"].get("nb_shots_used") for entry in counted]
        if not all(isinstance(n, int) and n >= 0 for n in per):
            raise RecordError(f"job {job}: an iteration reports no nb_shots_used")
        used = sum(per)
        for entry, n in zip(counted, per, strict=True):
            if entry["samples"] > n:
                raise RecordError(f"job {job}: an iteration counts {entry['samples']} samples from {n} shots")
        # The shots a failed iteration consumed are unknown unless it reports them,
        # so shots_used is left out and the top-level shots stand in for the charge.
        failed = len(counted) < len(iterations)
        spent = [entry.get("result_fields", {}).get("nb_shots_used") for entry in iterations]
        if failed and all(isinstance(n, int) and n >= 0 for n in spent):
            used, failed = sum(spent), False
    # A partial job may answer shots null, which bounds nothing.
    if used is not None and sum(counts.values()) > used:
        raise RecordError(f"job {job}: {sum(counts.values())} samples exceed its {used} shots")
    scalars = {k: v for k, v in inner.items() if k != "results" and isinstance(v, int | float | str | None)}
    summary: dict[str, Any] = {
        "shots": shots,
        **({} if failed else {"shots_used": used}),
        "partial": not complete,
        "counts": counts,
        "samples": sum(counts.values()),
        "result_fields": scalars,
    }
    if iterations is not None:
        summary["iterations"] = iterations
    return summary


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []


@dataclass(frozen=True)
class Run:
    """One validated run: its records, the raw result summary, the shots consumed and the registry facts."""

    submission: dict[str, Any]
    manifest: dict[str, Any]
    circuit: dict[str, Any]
    collected: dict[str, Any]
    summary: dict[str, Any] | None
    shots: int
    facts: dict[str, Any]
    cases_sha256: str
    body: dict[str, Any]


def validate_run(records: Records) -> Run:
    """Offline rules of one retained run: receipt, digests, approval, collection and raw result bytes.

    Every rejection names the run. The returned Run carries the parsed receipt, manifest, circuit and collection,
    the raw result summary (None for a result-less terminal job), the shots the job consumed, the facts the
    registry records, the cases.json digest and the sent body; the credit charge is an account fact that
    qd_platform.run_facts adds.
    """
    directory = records.directory
    owner = f"Quandela run {directory.name}"
    if records.submission_bytes is None:
        hint = "; submission-state.json records an interrupted submit" if records.interrupted else ""
        raise RecordError(f"{owner}: no submission.json{hint}")
    submission = records.json_of("submission.json")
    manifest, circuit, cases_sha256 = validate_case(records)
    if submission.get("schema") != SUBMISSION_SCHEMA or submission.get("cases_sha256") != cases_sha256:
        raise RecordError(f"{owner}: cases.json differs from submission.json")
    if not isinstance(submission.get("approval"), str) or not submission["approval"].strip():
        raise RecordError(f"{owner}: submission.json records no approval")
    body = records.json_of("job-body.json")
    if sha256_bytes(json.dumps(body, sort_keys=True).encode()) != submission["body_sha256"]:
        raise RecordError(f"{owner}: job-body.json differs from the body the receipt sent")
    if submission["platform"] not in manifest["platforms"]:
        raise RecordError(f"{owner}: platform {submission['platform']} is outside cases.json")
    if records.collected_bytes is None:
        raise RecordError(f"{owner}: results.json is missing; collect the run")
    collected = records.json_of("results.json")
    if collected.get("schema") != COLLECTION_SCHEMA or collected.get("job_id") != submission["job_id"]:
        raise RecordError(f"{owner}: results.json names another job or schema")
    if carried := sorted(set(FORBIDDEN_KEYS) & keys(collected)):
        raise RecordError(f"{owner}: results.json carries {carried}")
    returned = collected.get("data", {}).get("payload")
    if (
        manifest.get("schema") == "qd-hypercomplex-cases-v1"
        and "logical_modes" in manifest
        and collected.get("status", {}).get("status") == "completed"
        and not isinstance(returned, dict)
    ):
        raise RecordError(f"{owner}: completed full-output acquisition lacks its returned payload")
    if isinstance(returned, dict):
        echoed = dict(returned)
        # The worker adds its version to the payload; the sent fields retain
        # their exact JSON structures, including compilation parameters.
        if "pcvl_version" not in body["payload"]:
            echoed.pop("pcvl_version", None)
        if echoed != body["payload"]:
            raise RecordError(f"{owner}: returned payload differs from job-body.json")
    status = collected["status"]["status"]
    if status not in TERMINAL:
        raise RecordError(f"{owner}: job status {status} is not terminal")
    raw = records.raw
    shots = 0
    summary: dict[str, Any] | None = None
    if status == "completed" or raw is not None:
        if raw is None or sha256_bytes(raw) != collected.get("result_sha256"):
            raise RecordError(f"{owner}: raw/result.json differs from its recorded sha256")
        summary = result_summary(
            raw,
            submission["job_id"],
            collected["status"],
            status == "completed",
            expected_iterations(manifest),
        )

        if any(collected.get(key) != value for key, value in summary.items() if not predates(collected, summary, key)):
            raise RecordError(f"{owner}: results.json differs from the raw result")
        modes = circuit["modes"]
        if any(len(state.split(",")) != modes for state in summary["counts"]):
            raise RecordError(f"{owner}: a counted state has a mode count other than {modes}")
        if summary["samples"] > manifest["max_samples"]:
            raise RecordError(f"{owner}: {summary['samples']} samples exceed max_samples {manifest['max_samples']}")
        # A count-less partial result carries no per-iteration shots; its top-level shots stand in.
        shots = summary.get("shots_used", summary.get("shots") or 0)
    elif not isinstance(collected.get("result_absent"), str):
        raise RecordError(f"{owner}: a {status} job records neither a raw result nor its absence")
    else:
        # A result-less terminal job still consumed the shots its status reports.
        reported = collected["status"].get("shots")
        if reported is not None and (not isinstance(reported, int) or reported < 0):
            raise RecordError(f"{owner}: status shots {reported!r} are not a shot count")
        shots = reported or 0
    facts = {
        "created_at": submission["submitted_utc"],
        "backends": [submission["platform"]],
        "jobs": 1,
        # A box-kite case counts its blocks and a mesh case its phase settings.
        "circuits": len(manifest["blocks"] if "blocks" in manifest else manifest["settings"]),
        "statuses": {status: 1},
        "detail": f"job {submission['job_id']}, {collected.get('samples', 0)} samples, {shots} shots",
    }
    return Run(submission, manifest, circuit, collected, summary, shots, facts, cases_sha256, body)


def read_run(directory: Path) -> Run:
    """load_run then validate_run: the one call a consumer of a retained run makes."""
    return validate_run(load_run(directory))


PlatformError = RecordError
