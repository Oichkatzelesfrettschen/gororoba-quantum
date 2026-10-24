"""Contract for ci/gate_ledger.py: each read kind the tracer records reruns exactly its gate after an edit;
-I children, -I shells, non-Python programs and repository writes never skip; a command or host change
reruns; a failure stores nothing and removes the earlier pass; a shard merge drops decided failures.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock

import host_identity
import pytest
import run_gates
from gate_ledger import load, merge, shell_untraceable, write

pytestmark = pytest.mark.audit

THREADED_FILES = 400


def test_every_read_kind_reruns_exactly_its_gate() -> None:
    """Every read kind flips SKIP to RUN after an edit; escapes, failures and key inputs never skip."""
    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="gate-ledger-contract-") as temporary:
        root = Path(temporary) / "repo"
        (root / "data" / "listed").mkdir(parents=True)
        (root / "data" / "globbed").mkdir(parents=True)
        (root / "pkg").mkdir()
        files = {
            "plain.py": "import pathlib\npathlib.Path('data/plain.txt').read_text()\n",
            "data/plain.txt": "v1\n",
            "importer.py": "import sys\nsys.path.insert(0, 'pkg')\nimport helper\n",
            "pkg/helper.py": "VALUE = 1\n",
            "globber.py": "import glob\nglob.glob('data/globbed/*.txt')\n",
            "data/globbed/a.txt": "",
            "lister.py": "import os\nos.listdir('data/listed')\n",
            "data/listed/a.txt": "",
            "pooled.py": (
                "import multiprocessing\n"
                "def read(path):\n"
                "    with open(path) as handle:\n"
                "        return handle.read()\n"
                "if __name__ == '__main__':\n"
                "    with multiprocessing.get_context('spawn').Pool(1) as pool:\n"
                "        pool.map(read, ['data/pooled.txt'])\n"
            ),
            "data/pooled.txt": "v1\n",
            "exists.py": (
                "from pathlib import Path\nlater = Path('data/later.txt')\nif later.exists():\n    later.read_text()\n"
            ),
            "linked.py": "open('data/linked.txt').read()\nopen('data/outside.txt').read()\n",
            "data/target_a.txt": "same\n",
            "data/target_b.txt": "same\n",
            "threaded.py": (
                "from concurrent.futures import ThreadPoolExecutor\n"
                "from pathlib import Path\n"
                f"paths = [f'data/threaded/{{k}}.txt' for k in range({THREADED_FILES})]\n"
                "with ThreadPoolExecutor(8) as pool:\n"
                "    list(pool.map(lambda path: Path(path).read_text(), paths))\n"
            ),
            "isolated.py": "import subprocess, sys\nsubprocess.run([sys.executable, '-I', '-c', 'pass'], check=True)\n",
            "shells.py": "import subprocess\nsubprocess.run(['true'], check=True)\n",
            "writer.py": "open('data/written.txt', 'w').close()\n",
            "fails.py": "raise SystemExit(1)\n",
        }
        (root / "data" / "threaded").mkdir()
        for k in range(THREADED_FILES):
            files[f"data/threaded/{k}.txt"] = f"{k}\n"
        for name, text in files.items():
            (root / name).write_text(text)
        outside = Path(temporary) / "outside"
        outside.mkdir()
        (outside / "a.txt").write_text("same\n")
        (outside / "b.txt").write_text("same\n")
        (root / "data" / "linked.txt").symlink_to("target_a.txt")
        (root / "data" / "outside.txt").symlink_to(outside / "a.txt")

        def retarget(link: Path, target: Path | str) -> None:
            link.unlink()
            link.symlink_to(target)

        # A pyc-only module: the compiled file stands without its source.
        (root / "compiled").mkdir()
        (root / "compiled" / "only.py").write_text("VALUE = 1\n")
        import py_compile

        py_compile.compile(str(root / "compiled" / "only.py"), cfile=str(root / "compiled" / "only.pyc"))
        (root / "compiled" / "only.py").unlink()

        def recompile(text: str) -> None:
            source = Path(temporary) / "only.py"
            source.write_text(text)
            py_compile.compile(str(source), cfile=str(root / "compiled" / "only.pyc"))

        (root / "pyc.py").write_text("import sys\nsys.path.insert(0, 'compiled')\nimport only\n")

        def gate(name: str, cmd: str) -> dict[str, Any]:
            return {"name": name, "cwd": ".", "cmd": cmd, "seconds": 0.1}

        gates = [
            gate("plain", '"$PYTHON" -B plain.py'),
            gate("import", '"$PYTHON" -B importer.py'),
            gate("pyc", '"$PYTHON" -B pyc.py'),
            gate("glob", '"$PYTHON" -B globber.py'),
            gate("listdir", '"$PYTHON" -B lister.py'),
            gate("pool", '"$PYTHON" -B pooled.py'),
            gate("threads", '"$PYTHON" -B threaded.py'),
            gate("exists", '"$PYTHON" -B exists.py'),
            gate("link", '"$PYTHON" -B linked.py'),
            gate("isolated-child", '"$PYTHON" -B isolated.py'),
            gate("isolated-shell", '"$PYTHON" -I -B plain.py'),
            gate("program-child", '"$PYTHON" -B shells.py'),
            gate("program-shell", 'true && "$PYTHON" -B plain.py'),
            gate("writer", '"$PYTHON" -B writer.py'),
            gate("failure", '"$PYTHON" -B fails.py'),
        ]
        environment = run_gates.environment_for(None)
        environment["PYTHON"] = python
        environment.pop("PYTHONPATH", None)
        ledger = Path(temporary) / "ledger.json"

        def run(chosen: list[dict[str, Any]], host: dict[str, str] | None = None) -> dict[str, str]:
            verdicts: dict[str, str] = {}
            env = dict(environment, **(host or {}))
            outcome = run_gates.execute(chosen, env, root, ledger=ledger, ledger_out=ledger)
            for gate_result in outcome:
                verdicts[gate_result.gate["name"]] = gate_result.verdict
            return verdicts

        first = run(gates)
        expected_first = {gate["name"]: "PASS" for gate in gates}
        expected_first["failure"] = "FAIL"
        if first != expected_first:
            raise AssertionError(f"first pass verdicts {first}")
        stored = load(ledger)
        traceable = {"plain", "import", "pyc", "glob", "listdir", "pool", "threads", "exists", "link"}
        if set(stored) != traceable:
            raise AssertionError(f"the ledger stores {sorted(stored)}, expected {sorted(traceable)}")
        if "compiled/only.pyc" not in stored["pyc"]["reads"]["files"]:
            raise AssertionError(f"a pyc-only import is outside the read set: {stored['pyc']['reads']}")
        threaded = {name for name in stored["threads"]["reads"]["files"] if name.startswith("data/threaded/")}
        if len(threaded) != THREADED_FILES:
            raise AssertionError(f"threads recorded {len(threaded)} of {THREADED_FILES} files read from worker threads")
        second = run(gates)
        expected_second = {name: ("SKIP" if name in traceable else verdict) for name, verdict in first.items()}
        if second != expected_second:
            raise AssertionError(f"second pass verdicts {second}, expected {expected_second}")
        edits = {
            "plain": lambda: (root / "data" / "plain.txt").write_text("v2\n"),
            "import": lambda: (root / "pkg" / "helper.py").write_text("VALUE = 2\n"),
            "pyc": lambda: recompile("VALUE = 2\n"),
            "glob": lambda: (root / "data" / "globbed" / "b.txt").write_text(""),
            "listdir": lambda: (root / "data" / "listed" / "b.txt").write_text(""),
            "pool": lambda: (root / "data" / "pooled.txt").write_text("v2\n"),
            "threads": lambda: (root / "data" / "threaded" / f"{THREADED_FILES - 1}.txt").write_text("v2\n"),
            "exists": lambda: (root / "data" / "later.txt").write_text("appeared\n"),
            "link": lambda: retarget(root / "data" / "linked.txt", "target_b.txt"),
        }
        if "data/outside.txt" not in stored["link"]["reads"]["links"]:
            raise AssertionError(f"a link leaving the root is outside the read set: {stored['link']['reads']}")
        edits["link-outside"] = lambda: retarget(root / "data" / "outside.txt", outside / "b.txt")
        for name, edit in edits.items():
            edit()
            verdicts = run([entry for entry in gates if entry["name"] in traceable])
            reran = {gate_name for gate_name, verdict in verdicts.items() if verdict != "SKIP"}
            if reran != {name.removesuffix("-outside")}:
                raise AssertionError(f"an edit read by {name} reran {sorted(reran)}")
        plain = [entry for entry in gates if entry["name"] == "plain"]
        edited = [dict(plain[0], cmd='"$PYTHON" -B -W error plain.py')]
        if run(edited) != {"plain": "PASS"}:
            raise AssertionError("an edited command reused the stored key")
        if run(edited) != {"plain": "SKIP"}:
            raise AssertionError("an unchanged command after its pass ran again")
        if run(edited, {"GOROROBA_LEDGER_PROBE": "host"}) != {"plain": "PASS"}:
            raise AssertionError("a changed host identity reused the stored key")
        real_identity = host_identity.interpreter_identity

        def upgraded(python: str) -> list[Any]:
            path, (version, distributions) = real_identity(python)
            return [path, [version, [*distributions, ["planted-distribution", "1.0"]]]]

        with mock.patch.object(host_identity, "interpreter_identity", upgraded):
            if run(edited, {"GOROROBA_LEDGER_PROBE": "host"}) != {"plain": "PASS"}:
                raise AssertionError("a changed interpreter distribution set reused the stored key")
        patches = Path(temporary) / "patches"
        patches.mkdir()
        (patches / "fix.patch").write_text("v1\n")
        with mock.patch.object(host_identity, "PATCHES", patches):
            run(edited)
            if run(edited) != {"plain": "SKIP"}:
                raise AssertionError("an unchanged patch set reran a stored pass")
            (patches / "fix.patch").write_text("v2\n")
            if run(edited) != {"plain": "PASS"}:
                raise AssertionError("an edited ci/patches file reused the stored key")
        if run(edited, {"IQM_TOKENS_FILE": "/nonexistent/tokens.json"}) != {"plain": "PASS"}:
            raise AssertionError("a newly set credential location reused the stored key")
        (root / "fails.py").write_text("raise SystemExit(0)\n")
        failing = [entry for entry in gates if entry["name"] == "failure"]
        run(failing)
        (root / "fails.py").write_text("raise SystemExit(1)\n")
        if run(failing) != {"failure": "FAIL"} or "failure" in load(ledger):
            raise AssertionError("a failure after a pass kept the stored pass")
        shards = [Path(temporary) / f"shard-{index}.json" for index in range(2)]
        write(shards[0], {"plain": load(ledger)["plain"]}, ["plain"])
        write(shards[1], {}, ["glob"])
        merged, _selected = merge(ledger, shards)
        if "glob" in merged or "plain" not in merged or "import" not in merged:
            raise AssertionError(f"a shard merge kept a dropped entry or lost a base entry: {sorted(merged)}")


@pytest.mark.parametrize(
    ("command", "escapes"),
    (
        ('"$PYTHON" -B -W error x.py && "$PYTHON" y.py', False),
        ('"$PYTHON" -IB x.py', True),
        ('"$PYTHON" -W error -E x.py', True),
        ('"$PYTHON" x.py | sha256sum', True),
        ("sha256sum -c x", True),
        ('"$PYTHON" x.py; true', True),
        ('"$PYTHON" x.py --check results/runs/*-mesh-*/', True),
        ('"$PYTHON" x.py data/[ab].json', True),
        ('"$PYTHON" x.py ~/data', True),
        ('"$PYTHON" x.py "$RUNNER_TEMP/out"', True),
        ('"$PYTHON" x.py $(ls)', True),
        ('PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" x.py && "$PYTHON" y.py', False),
        ('PYTHONPATH=elsewhere "$PYTHON" x.py', True),
        ('GOROROBA_READ_TRACE= "$PYTHON" x.py', True),
    ),
)
def test_shell_classification(command: str, escapes: bool) -> None:
    if (shell_untraceable(command) is not None) != escapes:
        raise AssertionError(f"shell classification of {command!r} is wrong")
