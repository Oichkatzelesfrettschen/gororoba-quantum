"""Protect the boundary between terminal measurement samples and unitary probabilities."""

import json
from pathlib import Path
from types import SimpleNamespace

import local_photonic_compiler_crosscheck
import pytest
from local_photonic_compiler_crosscheck import photonic, terminal_unitary


@pytest.mark.parametrize("missing", ["all", "manifest", "case"])
def test_qi_worker_rejects_incomplete_frozen_input_set(
    missing: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import shutil

    runner = local_photonic_compiler_crosscheck
    relative = Path("results/quantum_inspire/runs/tuna17-quaternion-order-noise")
    if missing != "all":
        shutil.copytree(runner.ROOT / relative, tmp_path / relative)
        manifest_path = tmp_path / relative / "order-batch-00/cases.json"
        if missing == "manifest":
            manifest_path.rename(manifest_path.with_suffix(".missing"))
        else:
            manifest = json.loads(manifest_path.read_text())
            manifest["circuits"].pop()
            manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner.sys, "argv", ["crosscheck", "--qi-worker", "--out", str(tmp_path / "output")])
    monkeypatch.setattr(runner, "version", lambda name: "test")
    monkeypatch.setattr(runner, "ordered_map", lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match="case denominator"):
        runner.main()


def test_terminal_measurement_removal_keeps_unitary_gates() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nH q[0]\nb[0] = measure q[0]\n"
    expected = "version 3.0\nqubit[1] q\nbit[1] b\nH q[0]\n"
    if terminal_unitary(source) != expected:
        raise RuntimeError("unitary probe must preserve source gates")


def test_intermediate_measurement_rejects_unitary_probe() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nb[0] = measure q[0]\nX q[0]\n"
    with pytest.raises(ValueError, match="terminal"):
        terminal_unitary(source)


def test_physical_experiment_api_retains_twelve_mode_distribution() -> None:
    pytest.importorskip("perceval")
    row = photonic(("results/hypercomplex/photonic-successors/ascella/order-repeat-block-0", 0))
    if not row["passed"] or row["modes"] != 12 or len(row["probabilities"]["Naive"]) != 12:
        raise RuntimeError(f"physical single-photon experiment must retain all twelve outputs: {row}")


def test_inline_measurement_comment_preserves_terminal_guard() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nb[0] = measure q[0] // terminal\nX q[0]\n"
    with pytest.raises(ValueError, match="terminal"):
        terminal_unitary(source)


def test_unsupported_measurement_assignment_fails_closed() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] c\nc[0] = measure q[0]\n"
    with pytest.raises(ValueError, match="supported terminal"):
        terminal_unitary(source)


def test_worker_execution_error_retains_record_and_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = local_photonic_compiler_crosscheck
    monkeypatch.setattr(runner.sys, "argv", ["crosscheck", "--qi-worker", "--out", str(tmp_path)])
    monkeypatch.setattr(runner, "version", lambda name: "test")
    monkeypatch.setattr(runner, "ordered_map", lambda *args, **kwargs: [{"passed": False, "error": "simulator failed"}])
    with pytest.raises(SystemExit, match="1"):
        runner.main()
    record = json.loads((tmp_path / "qi.json").read_text())
    if record["rows"][0]["error"] != "simulator failed":
        raise RuntimeError("worker diagnostics must precede the unsuccessful exit")


def test_parent_retains_photonic_record_when_qi_child_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_stack

    def failed_child(*args: object, **kwargs: object) -> str:
        raise SystemExit("synthetic child failure")

    runner = local_photonic_compiler_crosscheck
    monkeypatch.setattr(runner.sys, "argv", ["crosscheck", "--out", str(tmp_path)])
    monkeypatch.setattr(runner, "version", lambda name: "test")
    monkeypatch.setattr(runner, "ordered_map", lambda *args, **kwargs: [{"passed": True}])
    monkeypatch.setattr(qi_stack, "probe", lambda: SimpleNamespace(available=True))
    monkeypatch.setattr(qi_stack, "run", failed_child)
    with pytest.raises(SystemExit, match="1"):
        runner.main()
    record = json.loads((tmp_path / "photonic.json").read_text())
    if record["qi_worker_error"] != "QI subprocess failed" or record["rows"] != [{"passed": True}]:
        raise RuntimeError("the parent must retain photonic rows and the child failure outcome")
