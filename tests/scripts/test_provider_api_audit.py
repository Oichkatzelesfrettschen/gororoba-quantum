"""An audit admits captured bytes and rejects altered or escaping artifacts."""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import pytest


def validate(root: Path) -> None:
    try:
        module = importlib.import_module("provider_api_audit")
    except ModuleNotFoundError:
        pytest.fail("the provider API audit verifier is absent")
    module.check(root)


def test_capture_hash_rejects_changed_bytes(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2] / "docs/evidence/provider-api-audit"
    shutil.copytree(root, tmp_path, dirs_exist_ok=True)
    validate(tmp_path)
    (tmp_path / "iqm.json").write_bytes(b'{"observed":false}\n')
    with pytest.raises(ValueError, match="digest"):
        validate(tmp_path)


def test_capture_rejects_missing_manifest_member(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2] / "docs/evidence/provider-api-audit"
    index = json.loads((root / "index.json").read_text())
    del index["files"]["iqm.json"]
    (tmp_path / "index.json").write_text(json.dumps(index))
    with pytest.raises(ValueError, match="manifest membership"):
        validate(tmp_path)


def test_capture_refuses_manifest_path_escape(tmp_path: Path) -> None:
    (tmp_path / "index.json").write_text(
        json.dumps({"schema": "provider-api-audit-v1", "files": {"../unrelated.json": "0" * 64}})
    )
    with pytest.raises(ValueError, match="path"):
        validate(tmp_path)


def test_retained_capture_and_sampled_quote_model_replay() -> None:
    import oq_platform

    root = Path(__file__).resolve().parents[2] / "docs/evidence/provider-api-audit"
    validate(root)
    oq_platform.check(root / "open-quantum")
