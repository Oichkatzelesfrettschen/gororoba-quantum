"""Regenerate w8-n16-acceptance.json from the three records of the W8 N = 16 acceptance run and the retained v11 run.

The summary (schema v4) takes every number from `w8-n16-acceptance/` (the engine's stdout record, its stderr and the
runner's resource file) and from the retained v11 receipt run (`w8-n16-azure/receipt-bound/`). The launcher settings
that no record holds (worker count, BLAS and OpenMP threads, the memory scope) are the constants `LAUNCHER` below.

    acceptance_summary.py            write w8-n16-acceptance.json beside this script
    acceptance_summary.py --check    compare the tracked file with a fresh summary; exit 1 on a difference

The summary states that the resource record's `engine_sha256` equals the digest of the engine file at the commit that
retains it. Both modes verify the six launch inputs against the immutable manifest copied from the prelaunch case;
`--skip-engine-digest` omits only the current engine-byte check, retaining every imported-dependency check.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "a5-fiber-rank-v14-memory-acceptance-v4"
FIBER = "docs/evidence/a5-exceptional-fibers"
ENGINE = f"{FIBER}/replay/engine/fiber_rank_v14.py"
RECORD_DIRECTORY = f"{FIBER}/memory-bounded/w8-n16-acceptance"
RECORD_STEM = "w8-nm-d5-n16-p32009"
COMPARATOR_DIRECTORY = f"{FIBER}/w8-n16-azure/receipt-bound"
COMPARATOR_STEM = "w8d5-n16-rcpt"
SUMMARY = "w8-n16-acceptance.json"
LAUNCH_INPUTS = f"{FIBER}/memory-bounded/w8-n16-launch-inputs.json"
LAUNCH_INPUTS_SHA256 = "21b7b7dbaa0a3f0ff8a4276a986389e9372c127ebd2f35bf42569e8eb1048797"
IMPORTED_IMPLEMENTATIONS = (
    f"{FIBER}/replay/engine/rank_cell.py",
    "gororoba_quantum/modular_echelon_compact.py",
    "gororoba_quantum/parallel.py",
)

LAUNCHER: dict[str, Any] = {
    "workers": 4,
    "openblas_threads": 2,
    "omp_threads": 1,
    "memory_scope": "systemd user scope, MemoryMax=16G, MemorySwapMax=0",
    "host": "the build host",
    "source": "launch settings of the rerun; the resource file records the engine arguments, not the environment or "
    "the scope",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_root() -> Path:
    """The nearest ancestor of this file that holds gororoba_quantum/parallel.py."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            return parent
    raise SystemExit("acceptance_summary: gororoba_quantum/parallel.py not found above this file")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"acceptance_summary: {message}")


def engine_options(command: list[str]) -> dict[str, str | None]:
    """The engine's `--flag [VALUE]` options from the runner's command (python, engine, header, degree, order, then
    options); the last of a repeated option wins, as in the engine's parser."""
    options: dict[str, str | None] = {}
    flag: str | None = None
    for token in command[5:]:
        if token.startswith("--"):
            flag = token
            options[flag] = None
        elif flag is not None:
            options[flag] = token
    return options


def option_number(options: dict[str, str | None], flag: str) -> int | float:
    text = options.get(flag)
    if text is None:
        raise SystemExit(f"acceptance_summary: the recorded command has no value for {flag}")
    value = float(text)
    return int(value) if value == int(value) else value


def log_match(text: str, pattern: str) -> re.Match[str]:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise SystemExit(f"acceptance_summary: no line matches {pattern!r}")
    return match


def verify_launch_inputs(
    root: Path, resources_path: Path, header: str, receipt: str, check_engine: bool
) -> dict[str, Any]:
    """Verify recorded launch identities without deriving replacement identities from the checkout."""
    path = root / LAUNCH_INPUTS
    require(path.is_file(), "the retained launch-input manifest is missing")
    require(sha256(path) == LAUNCH_INPUTS_SHA256, "the retained launch-input manifest bytes differ")
    manifest = json.loads(path.read_text())
    require(
        isinstance(manifest, dict) and manifest.get("schema") == "a5-fiber-rank-v14-launch-inputs-v1",
        "the launch-input manifest is withheld or has an unsupported schema",
    )
    inputs = manifest.get("input_sha256")
    require(isinstance(inputs, dict), "the launch-input manifest withholds its input digests")
    require(
        set(inputs) == {ENGINE, *IMPORTED_IMPLEMENTATIONS, header, receipt},
        "the launch-input manifest must name the six recorded files",
    )
    require(
        all(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) for digest in inputs.values()),
        "the launch-input manifest contains a withheld or malformed input digest",
    )
    resource = manifest.get("resource_record")
    require(
        isinstance(resource, dict) and resource.get("path") == str(resources_path.relative_to(root)),
        "the launch-input manifest names another resource record",
    )
    require(
        resource.get("sha256") == sha256(resources_path),
        "the launch-input manifest resource digest differs from the retained run",
    )
    for filename, expected in inputs.items():
        if check_engine or filename != ENGINE:
            require(sha256(root / filename) == expected, f"{filename}: current bytes differ from the launch manifest")
    return manifest


def build_summary(root: Path, check_engine: bool) -> dict[str, Any]:
    records = root / RECORD_DIRECTORY
    record_path, err_path = records / f"{RECORD_STEM}.json", records / f"{RECORD_STEM}.err"
    resources_path = records / f"{RECORD_STEM}.resources.json"
    record = json.loads(record_path.read_text())
    resources = json.loads(resources_path.read_text())
    err = err_path.read_text()
    comparator_path = root / COMPARATOR_DIRECTORY / f"{COMPARATOR_STEM}.out"
    comparator_err_path = root / COMPARATOR_DIRECTORY / f"{COMPARATOR_STEM}.err"
    v11 = json.loads(comparator_path.read_text())

    command = resources["command"]
    options = engine_options(command)
    require(command[1] == ENGINE, f"the recorded engine is {command[1]}, not {ENGINE}")
    require(resources["runner_exit"] == 0 and resources["engine_exit"] == 0, "the recorded run did not succeed")
    require(resources["termination"] == "exited" and resources["validation_error"] is None, "the run was cut short")
    require(resources["stdout_part_sha256"] == sha256(record_path), "stdout record differs from the resource file")
    require(resources["stderr_sha256"] == sha256(err_path), "stderr differs from the resource file")
    require(record["engine_sha256_16"] == resources["engine_sha256"][:16], "record and resources name two engines")
    require(record["header_sha256_16"] == resources["header_sha256"][:16], "record and resources name two headers")
    require(v11["header_sha256_16"] == record["header_sha256_16"], "the v11 comparator ran on another header")
    require([command[3], command[4]] == [str(record["d"]), str(record["N"])], "command and record differ in d, N")
    if check_engine:
        engine_digest = sha256(root / ENGINE)
        require(
            engine_digest == resources["engine_sha256"],
            f"{ENGINE} has sha256 {engine_digest}, the resource record names {resources['engine_sha256']}; "
            "repeat the acceptance run and retain its records",
        )
    require(sha256(root / command[2]) == resources["header_sha256"], "the current header bytes differ from the run")
    receipt = options.get("--k2-receipt")
    if receipt is None:
        raise SystemExit("acceptance_summary: the recorded command has no degree-two receipt")
    require(
        sha256(root / receipt) == record["representatives"]["receipt_sha256"],
        "the current degree-two receipt bytes differ from the run",
    )
    launch_inputs = verify_launch_inputs(root, resources_path, command[2], receipt, check_engine)
    require(launch_inputs["input_sha256"][ENGINE] == resources["engine_sha256"], "the launch engine digest differs")
    require(launch_inputs["input_sha256"][command[2]] == resources["header_sha256"], "the launch header digest differs")
    require(
        launch_inputs["input_sha256"][receipt] == record["representatives"]["receipt_sha256"],
        "the launch receipt digest differs",
    )

    retained = int(log_match(err, r"^products built in [0-9.]+ s: (\d+) retained rows$").group(1))
    insert_seconds = float(log_match(err, r"^echelon insert seconds in the closure: ([0-9.]+)$").group(1))
    require(retained == record["representatives"]["built_rows"][str(record["d"])], "retained rows differ")
    require(record["product_operator"] == "uint16-cached", "the summary's route statement assumes the cached operator")
    stages = record["preflight_stages"]
    max_gb = option_number(options, "--max-gb")

    for field in ("r_N", "dim_quotient", "products"):
        require(type(record.get(field)) is int and record[field] >= 0, f"the recorded {field} result is withheld")
    require(
        isinstance(record.get("checks"), dict)
        and type(record["checks"].get("count")) is int
        and record["checks"]["count"] > 0,
        "the nonstandard control results are empty or withheld",
    )
    per_block = record.get("per_block")
    require(isinstance(per_block, dict) and bool(per_block), "the per-block results are empty or withheld")
    for block, result in per_block.items():
        require(isinstance(result, dict), f"block {block}: the result is withheld")
        for field in ("r_N", "rank_W", "cols"):
            require(
                type(result.get(field)) is int and result[field] >= 0,
                f"block {block}: the {field} result is withheld",
            )
    order = sorted(per_block, key=int)
    v11_blocks = v11["per_block"]
    require(sorted(v11_blocks, key=int) == order, "v11 and v14 differ in their blocks")
    for block in order:
        require(per_block[block]["r_N"] == v11_blocks[block]["r_N"], f"block {block}: r_N differs from v11")
        require(per_block[block]["rank_W"] == v11_blocks[block]["rank_W"], f"block {block}: rank_W differs from v11")
    require(record["r_N"] == v11["r_N"], "r_N differs from v11")
    require(record["checks"]["rank_growth"] == {} == v11["checks"]["rank_growth"], "a control grew the rank")
    require(record["checks"]["count"] == v11["checks"]["count"], "v11 ran other nonstandard controls")

    comparator_err = comparator_err_path.read_text()
    v11_rss_kib = int(log_match(comparator_err, r"^\s*Maximum resident set size \(kbytes\): (\d+)$").group(1))
    require(
        type(resources.get("max_sampled_process_group_rss_bytes")) is int
        and resources["max_sampled_process_group_rss_bytes"] > 0,
        "the sampled process-group RSS result is empty or withheld",
    )
    v14_gib, v11_gib = resources["max_sampled_process_group_rss_bytes"] / 2**30, v11_rss_kib / 2**20
    require(resources["rss_poll_seconds"] > 0, "the RSS sample interval must be positive")

    def entry(role: str, path: Path) -> dict[str, str]:
        return {"role": role, "path": str(path.relative_to(root)), "sha256": sha256(path)}

    return {
        "schema": SCHEMA,
        "launch_inputs": {
            **entry("immutable prelaunch input manifest", root / LAUNCH_INPUTS),
            "launch_head": launch_inputs["launch_head"],
            "input_sha256": launch_inputs["input_sha256"],
        },
        "case": {
            "fiber": "W8 -> N-",
            "prime": record["prime"],
            "degree": record["d"],
            "order": record["N"],
            "header_sha256": resources["header_sha256"],
            "engine": ENGINE,
            "engine_sha256": resources["engine_sha256"],
            "engine_bytes": "the file at the commit that retains this summary; its sha256 equals the resource "
            "record's engine_sha256",
        },
        "configuration": {
            "from_records": {
                "mode": record["mode"],
                "stream_products": record["stream_products"],
                "product_operator": record["product_operator"],
                "operator_cache_gib": option_number(options, "--operator-cache-gb"),
                "echelon": record["echelon"],
                "chunk": option_number(options, "--chunk"),
                "max_gib": max_gb,
                "dense_tables_gib": option_number(options, "--dense-tables-gb"),
                "closure_tables": record["closure_tables"],
                "timeout_seconds": resources["timeout_seconds"],
                "receipt_sha256": record["representatives"]["receipt_sha256"],
                "engine_args_sha256_16": resources["engine_args_sha256_16"],
            },
            "streamed_uncached_route": "not exercised at this size",
            "from_launcher_not_recorded": LAUNCHER,
        },
        "result": {
            "r_N": record["r_N"],
            "dim_quotient": record["dim_quotient"],
            "products": record["products"],
            "retained_rows": retained,
            "nonstandard_checks": record["checks"]["count"],
            "nonstandard_rank_growth": record["checks"]["rank_growth"],
            "closure_rounds": record["closure_rounds"],
            "per_block": {block: per_block[block] for block in order},
        },
        "resources": {
            "elapsed_seconds": resources["elapsed_seconds"],
            "max_sampled_process_group_rss_bytes": resources["max_sampled_process_group_rss_bytes"],
            "max_sampled_processes": resources["max_sampled_processes"],
            "rss_poll_seconds": resources["rss_poll_seconds"],
            "rss_unavailable_samples": resources["rss_unavailable_samples"],
            "rss_statistic": "maximum observed sum of process-group RSS at polling times; allocations between "
            "samples are unobserved, so this statistic is not a process-group high-water mark",
            "seconds": {
                "singular_and_export": record["seconds"]["singular"],
                "products": record["seconds"]["products"],
                "closure": record["seconds"]["closure"],
                "total": record["seconds"]["total"],
                "echelon_insert_within_closure": insert_seconds,
            },
            "preflight_stage_maximum_bytes": max(stages.values()),
            "preflight_stage_bytes": stages,
            "preflight_stage_maximum_basis": "the larger of the products and closure stage totals (the admission "
            f"rule of the engine at the head), against --max-gb {max_gb}",
        },
        "retention": {
            "this_file": "summary of the rerun; every number comes from the three files below and the comparator",
            "files": [
                entry("engine stdout record", record_path),
                entry("engine stderr", err_path),
                entry("runner resource file", resources_path),
            ],
            "cross_check": "the resource file's stdout_part_sha256 and stderr_sha256 equal the sha256 of the first "
            "two files",
        },
        "retained_v11_comparator": {
            "path": str(comparator_path.relative_to(root)),
            "sha256": sha256(comparator_path),
            "max_rss_path": str(comparator_err_path.relative_to(root)),
            "max_rss_sha256": sha256(comparator_err_path),
            "r_N": v11["r_N"],
            "closure_rounds": v11["closure_rounds"],
            "per_block_r_N": [v11_blocks[block]["r_N"] for block in order],
            "per_block_rank_W": [v11_blocks[block]["rank_W"] for block in order],
            "elapsed_seconds": v11["seconds"]["total"],
            "max_rss_kib": v11_rss_kib,
        },
        "verdict": "r_N, every block rank and every nonstandard control agree with the retained v11 receipt run; the "
        f"v14 maximum sampled process-group RSS is {v14_gib:.2f} GiB at a "
        f"{resources['rss_poll_seconds']}-second interval, while the v11 single-process high-water mark is "
        f"{v11_gib:.1f} GiB on another machine; these distinct statistics establish no true-peak ratio",
    }


def render(summary: dict[str, Any]) -> str:
    return json.dumps(summary, indent=1) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate or check w8-n16-acceptance.json from its records.")
    parser.add_argument("--check", action="store_true", help="compare the tracked summary with a fresh one")
    parser.add_argument(
        "--skip-engine-digest",
        action="store_true",
        help="omit the check that the engine file's sha256 equals the resource record's engine_sha256",
    )
    args = parser.parse_args(argv)
    root = repository_root()
    target = Path(__file__).resolve().parent / SUMMARY
    fresh = render(build_summary(root, not args.skip_engine_digest))
    if not args.check:
        target.write_text(fresh)
        print(f"wrote {target.relative_to(root)}")
        return 0
    tracked = target.read_text()
    if tracked == fresh:
        print(f"{target.relative_to(root)} matches its records")
        return 0
    sys.stdout.writelines(
        difflib.unified_diff(tracked.splitlines(True), fresh.splitlines(True), "tracked", "fresh", n=1)
    )
    print(f"{target.relative_to(root)} differs from a fresh summary", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
