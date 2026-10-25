"""kaggle_run collect keeps every attempt: no capture rewrites or removes an earlier one."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

import kaggle_run
import pytest

Files = dict[str, bytes]


def _run_dir(results: Path) -> Path:
    run_dir = results / "2026-01-01T000000Z-owner-slug"
    run_dir.mkdir(parents=True)
    (run_dir / "submission.json").write_text(json.dumps({"kernel": "owner/slug", "kernel_version": 3}))
    return run_dir


def _serve(monkeypatch: pytest.MonkeyPatch, results: Path, returns: list[Files | Exception]) -> None:
    """Point kaggle_run at RESULTS and answer each download with the next entry of RETURNS."""
    monkeypatch.setattr(kaggle_run, "ROOT", results.parent)
    monkeypatch.setattr(kaggle_run, "RESULTS", results)
    monkeypatch.setattr(kaggle_run, "kaggle", lambda *args: 'owner/slug has status "KernelWorkerStatus.COMPLETE"')

    def download(owner: str, slug: str, version: int, target: Path) -> list[str]:
        if (owner, slug, version) != ("owner", "slug", 3):
            raise RuntimeError(f"collect asked for {owner}/{slug}/{version}")
        served = returns.pop(0)
        if isinstance(served, Exception):
            (target / "slug.log").write_bytes(b"partial log")
            raise served
        for name, data in served.items():
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            (target / name).write_bytes(data)
        return sorted(served)

    monkeypatch.setattr(kaggle_run, "download_version", download)


def _collect(run_dir: Path) -> int:
    return kaggle_run.collect(argparse.Namespace(run_dir=str(run_dir)))


def _receipt(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _complete(result: bytes) -> Files:
    return {
        "output/exit.json": b'{"returncode": 0}',
        "output/result.json": result,
        "slug.log": b"log",
        "repo/scripts/entry.py": b"bundle echo",
    }


def _expect_exit(action: Callable[[], object], fragment: str) -> None:
    try:
        action()
    except SystemExit as reason:
        if fragment not in str(reason):
            raise RuntimeError(f"{reason} lacks {fragment!r}") from None
        return
    raise RuntimeError(f"expected a failure naming {fragment!r}")


def test_partial_then_complete_then_recollect_keeps_every_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results = tmp_path / "results"
    run_dir = _run_dir(results)
    _serve(monkeypatch, results, [{"slug.log": b"running"}, _complete(b"first"), _complete(b"second")])

    _expect_exit(lambda: _collect(run_dir), "returned no exit.json")
    (partial,) = sorted((run_dir / "captures").iterdir())
    partial_receipt = _receipt(partial / "collect.json")
    if partial_receipt["state"] != "PARTIAL" or partial_receipt["predecessor_sha256"] is not None:
        raise RuntimeError(f"partial receipt: {partial_receipt}")
    if (run_dir / "collect.json").exists() or (run_dir / "output").exists():
        raise RuntimeError("a partial capture must not become the primary output")

    _collect(run_dir)
    primary = _receipt(run_dir / "collect.json")
    if primary["state"] != "COMPLETE" or (run_dir / "output/output/result.json").read_bytes() != b"first":
        raise RuntimeError(f"the first complete capture is the primary output: {primary}")
    if primary["predecessor_sha256"] != kaggle_run.sha256((partial / "collect.json").read_bytes()):
        raise RuntimeError("the primary receipt must bind the partial receipt before it")
    if primary["discarded"] != {"repo/scripts/entry.py": kaggle_run.sha256(b"bundle echo")}:
        raise RuntimeError(f"discarded bundle echo: {primary['discarded']}")
    if (partial / "output/slug.log").read_bytes() != b"running":
        raise RuntimeError("the partial capture keeps its bytes")

    before = (run_dir / "collect.json").read_bytes()
    _collect(run_dir)
    if (run_dir / "collect.json").read_bytes() != before:
        raise RuntimeError("a recollection rewrote the primary receipt")
    if (run_dir / "output/output/result.json").read_bytes() != b"first":
        raise RuntimeError("a recollection rewrote the primary output")
    later = sorted((run_dir / "captures").iterdir())[-1]
    if (later / "output/output/result.json").read_bytes() != b"second":
        raise RuntimeError("the recollection keeps its own bytes in its own capture")
    if _receipt(later / "collect.json")["predecessor_sha256"] != kaggle_run.sha256(before):
        raise RuntimeError("the recollection receipt must bind the primary receipt")
    if [path.parent.name for path in kaggle_run.receipt_chain(run_dir)][1] != run_dir.name:
        raise RuntimeError("the chain orders receipts by capture id")
    kaggle_run.verify(argparse.Namespace())


def test_unreceipted_output_and_failed_download_are_retained(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    results = tmp_path / "results"
    run_dir = _run_dir(results)
    (run_dir / "output/output").mkdir(parents=True)
    (run_dir / "output/output/environment.json").write_bytes(b"{}")
    _serve(monkeypatch, results, [ConnectionError("reset by peer"), _complete(b"done")])

    with pytest.raises(ConnectionError):
        _collect(run_dir)
    unreceipted, failed = sorted((run_dir / "captures").iterdir())
    if _receipt(unreceipted / "collect.json")["state"] != "UNRECEIPTED":
        raise RuntimeError("an output/ without collect.json moves into its own capture")
    if (unreceipted / "output/output/environment.json").read_bytes() != b"{}":
        raise RuntimeError("the unreceipted tree keeps its bytes")
    failed_receipt = _receipt(failed / "collect.json")
    if failed_receipt["state"] != "FAILED" or "reset by peer" not in str(failed_receipt["error"]):
        raise RuntimeError(f"failed download receipt: {failed_receipt}")
    if failed_receipt["files"] != {"slug.log": kaggle_run.sha256(b"partial log")}:
        raise RuntimeError("a failed download records the files it received")

    _collect(run_dir)
    kaggle_run.verify(argparse.Namespace())


def test_killed_attempts_are_adopted_in_chain_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    results = tmp_path / "results"
    run_dir = _run_dir(results)
    _serve(monkeypatch, results, [_complete(b"done")])
    # One attempt killed after promoting output/, before writing collect.json,
    # left its emptied capture; another was killed mid-download.
    (run_dir / "output/output").mkdir(parents=True)
    (run_dir / "output/output/exit.json").write_bytes(b'{"returncode": 0}')
    (run_dir / "captures/2000-01-01T000000.000000Z").mkdir(parents=True)
    (run_dir / "captures/2000-01-02T000000.000000Z/output").mkdir(parents=True)
    (run_dir / "captures/2000-01-02T000000.000000Z/output/slug.log").write_bytes(b"cut")

    _collect(run_dir)
    states = [_receipt(path)["state"] for path in kaggle_run.receipt_chain(run_dir)]
    if states != ["UNRECEIPTED", "UNRECEIPTED", "COMPLETE"]:
        raise RuntimeError(f"adopted chain: {states}")
    if any(d.name.startswith("2000-") for d in (run_dir / "captures").iterdir()):
        raise RuntimeError("an adopted tree moves to a new capture id")
    kaggle_run.verify(argparse.Namespace())


def test_verify_rejects_broken_chain_and_orphan_capture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    results = tmp_path / "results"
    run_dir = _run_dir(results)
    _serve(monkeypatch, results, [_complete(b"first"), _complete(b"second")])
    _collect(run_dir)
    _collect(run_dir)
    (later,) = sorted((run_dir / "captures").iterdir())
    receipt = later / "collect.json"
    original = receipt.read_bytes()

    record = json.loads(original)
    record["predecessor_sha256"] = "0" * 64
    receipt.write_text(json.dumps(record))
    _expect_exit(lambda: kaggle_run.verify(argparse.Namespace()), "predecessor differs")
    receipt.write_bytes(original)

    (run_dir / "submission.json").write_text(json.dumps({"kernel": "owner/slug", "kernel_version": 3, "x": 1}))
    _expect_exit(lambda: kaggle_run.verify(argparse.Namespace()), "submission.json differs")
    (run_dir / "submission.json").write_text(json.dumps({"kernel": "owner/slug", "kernel_version": 3}))

    (later / "output/output/result.json").write_bytes(b"edited")
    _expect_exit(lambda: kaggle_run.verify(argparse.Namespace()), "differs from its sha256")
    (later / "output/output/result.json").write_bytes(b"second")

    (run_dir / "captures/2099-01-01T000000.000000Z").mkdir()
    _expect_exit(lambda: kaggle_run.verify(argparse.Namespace()), "has no receipt")
