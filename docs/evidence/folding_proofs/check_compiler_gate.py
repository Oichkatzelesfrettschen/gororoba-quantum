"""Reject incompatible recorded Rocq/OCaml builds before proof replay."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


class CompilerAdmissionTests(unittest.TestCase):
    def test_incompatible_versions_fail_at_admission(self) -> None:
        script = Path(__file__).with_name("replay_rocq.sh").resolve()
        incompatible = (
            "The Rocq Prover, version 9.1.1\ncompiled with OCaml 5.5.0",
            "The Rocq Prover, version 9.2\ncompiled with OCaml 5.4.0",
            "The Rocq Prover, version 9.1.1",
            "compiled with OCaml 5.4.0",
            "The Rocq Prover, version 9.1.1\ncompiled with OCaml 5.4.0\nunexpected build",
        )
        with tempfile.TemporaryDirectory(prefix="folding-compiler-admission-") as temporary:
            root = Path(temporary)
            compiler = root / "rocq-fixture"
            for version in incompatible:
                with self.subTest(version=version):
                    compiler.write_text(
                        "#!/bin/sh\nset -eu\n"
                        'if [ "$#" -ne 1 ] || [ "$1" != "--version" ]; then exit 97; fi\n'
                        "printf '%s\\n' " + shlex.quote(version) + "\n"
                    )
                    compiler.chmod(0o700)
                    environment = dict(os.environ, ROCQ=str(compiler), GOROROBA_ROOT=temporary, TMPDIR=temporary)
                    result = subprocess.run(
                        ["sh", str(script)], env=environment, capture_output=True, text=True, check=False
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("requires Rocq 9.1.1 compiled with OCaml 5.4.0", result.stderr)
                    self.assertEqual({path.name for path in root.iterdir()}, {"rocq-fixture"})


if __name__ == "__main__":
    unittest.main()
