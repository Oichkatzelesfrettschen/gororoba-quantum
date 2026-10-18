"""Selection of the saved IBM Quantum account that serves a run.

GOROROBA_IBM_ACCOUNT names an entry of the qiskit account store
(QiskitRuntimeService(name=...)); unset or empty selects the default saved
account with a zero-argument constructor call. Each account resolves its own
IBM Cloud instance and its own 600 s rolling quota, and a record binds the
instance through instance_sha256_12. An account name is a label, never a
credential: this module reads and logs no token.

    "$PYTHON" ibm_account.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ACCOUNT_ENV = "GOROROBA_IBM_ACCOUNT"
BACKUP_ACCOUNT = "backup-ibm-quantum-platform"


def account_name() -> str:
    """The selected saved-account name, empty for the default account."""
    return os.environ.get(ACCOUNT_ENV, "")


def open_service(constructor: Callable[..., Any] | None = None) -> Any:
    """QiskitRuntimeService for the selected account.

    A caller passes its own module's QiskitRuntimeService global so a
    contract that patches that global intercepts the construction. The unset
    path calls the constructor with no arguments.
    """
    if constructor is None:
        from qiskit_ibm_runtime import QiskitRuntimeService

        constructor = QiskitRuntimeService
    name = account_name()
    return constructor(name=name) if name else constructor()


def require_instance(recorded: str | None, active: str, context: str, error: type[Exception] = RuntimeError) -> None:
    """Refuse a job lookup when the service resolves another instance than the record names.

    A record without instance_sha256_12 (a retrospective archive) binds the
    default account, so it passes only while no named account is selected.
    """
    if recorded is None:
        if account_name():
            raise error(
                f"{context}: the record names no instance and binds the default account; unset {ACCOUNT_ENV} to read it"
            )
        return
    if recorded != active:
        raise error(
            f"{context}: the record names instance {recorded} but the service resolves instance {active}; "
            f"set {ACCOUNT_ENV} to the saved account that owns the run"
        )


def recorded_instance(run_dir: Path) -> str | None:
    """instance_sha256_12 of a run directory's record.json, None when absent."""
    path = run_dir / "record.json"
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8")).get("instance_sha256_12")
    return value if isinstance(value, str) else None


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def self_test() -> None:
    calls: list[dict[str, Any]] = []

    def constructor(**kwargs: Any) -> str:
        calls.append(kwargs)
        return "service"

    saved = os.environ.pop(ACCOUNT_ENV, None)
    try:
        _require(open_service(lambda: "service") == "service", "unset env must call the constructor with no arguments")
        os.environ[ACCOUNT_ENV] = ""
        _require(open_service(lambda: "service") == "service", "empty env must select the default account")
        _require(not calls, "constructor called before the named account was selected")
        os.environ[ACCOUNT_ENV] = BACKUP_ACCOUNT
        _require(open_service(constructor) == "service", "named account must construct")
        _require(calls == [{"name": BACKUP_ACCOUNT}], f"named account must pass name=: {calls}")

        import live_run

        service = SimpleNamespace(active_instance=lambda: "crn:fixture")
        active = live_run._instance_hash(service)
        foreign = "a" * 12
        _require(active != foreign, "fixture hash collision")
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            (run_dir / "record.json").write_text(
                json.dumps({"instance_sha256_12": foreign, "submission": {"jobs": [{"job_id": "fixture-job"}]}}),
                encoding="utf-8",
            )
            (run_dir / "isa.qpy").write_bytes(b"")
            _require(recorded_instance(run_dir) == foreign, "recorded_instance must read the record")
            for action in (live_run.collect, live_run.preserve_raw):
                try:
                    action(service, run_dir)
                except live_run.LiveRunError as error:
                    text = str(error)
                    _require(
                        foreign in text and active in text and ACCOUNT_ENV in text,
                        f"{action.__name__}: mismatch text lacks the hashes or the variable: {text}",
                    )
                else:
                    raise RuntimeError(f"{action.__name__} accepted a mismatched instance")
            (run_dir / "record.json").write_text(json.dumps({"instance_sha256_12": active}), encoding="utf-8")
            try:
                live_run.collect(service, run_dir)
            except live_run.LiveRunError as error:
                _require(ACCOUNT_ENV not in str(error), "a matching instance must pass the account check")
            else:
                raise RuntimeError("collect accepted a record without an experiment digest")
        os.environ.pop(ACCOUNT_ENV, None)
        require_instance(None, active, "retrospective archive")
        os.environ[ACCOUNT_ENV] = "backup"
        try:
            require_instance(None, active, "retrospective archive")
        except RuntimeError as error:
            _require(ACCOUNT_ENV in str(error), "the default-account refusal must name the variable")
        else:
            raise RuntimeError("a named account read a retrospective archive")
    finally:
        if saved is None:
            os.environ.pop(ACCOUNT_ENV, None)
        else:
            os.environ[ACCOUNT_ENV] = saved
    print("ibm_account self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", required=True)
    parser.parse_args()
    self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
