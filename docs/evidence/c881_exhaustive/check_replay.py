"""Reject compiler and source drift before creating temporary proof objects."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


class ReplayAdmissionTests(unittest.TestCase):
    def reject(self, *, correct_version: bool) -> None:
        evidence = Path(__file__).resolve().parent
        version = (evidence / "toolchain.txt").read_text().strip()
        if not correct_version:
            version += "\nunreviewed compiler build"
        with tempfile.TemporaryDirectory(prefix="c881-admission-") as temporary:
            root = Path(temporary)
            compiler = root / "rocq-fixture"
            compiler.write_text(
                "#!/bin/sh\nset -eu\n"
                'if [ "$#" -ne 1 ] || [ "$1" != "--version" ]; then exit 97; fi\n'
                "printf '%s\\n' " + shlex.quote(version) + "\n"
            )
            compiler.chmod(0o700)
            for relative in ("theories/GF2Algebra.v", "verified/C881_GF2CubicMinDegree.v"):
                path = root / "proofs" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("source mutation\n")
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            result = subprocess.run(
                ["sh", str(evidence / "replay_rocq.sh")],
                env=dict(os.environ, ROCQ=str(compiler), GOROROBA_ROOT=temporary, TMPDIR=temporary),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("did NOT match" if correct_version else "requires the recorded", result.stderr)
            self.assertEqual(
                before, {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            )
            self.assertFalse(any(path.name.startswith("quantum-c881-") for path in root.iterdir()))

    def test_changed_compiler(self) -> None:
        self.reject(correct_version=False)

    def test_changed_source(self) -> None:
        self.reject(correct_version=True)


if __name__ == "__main__":
    unittest.main()
