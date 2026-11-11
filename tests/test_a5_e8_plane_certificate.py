"""Source-bound E8 intersection certificate generator tests (no Singular needed)."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "a5_e8_plane_certificate.py"
SPEC = importlib.util.spec_from_file_location("a5_e8_plane_certificate", SOURCE)
assert SPEC and SPEC.loader
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class PlaneCertificateTests(unittest.TestCase):
    def test_four_valid_field_header_combinations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "relations-upto-d2.rel"
            source.write_text("y(1)*y(2)", encoding="utf-8")
            for prime in (32009, 32029):
                script = tool.make_script(prime, source)
                self.assertIn(f"ring Y={prime},(y(1..21)),dp;", script)
                self.assertIn("minAssChar(std(K+N))", script)
                self.assertIn("nlin==18", script)
                self.assertIn("RESULT E8_EXACT_PROJECTIVE_PLANE_PASS", script)
                self.assertIn("inclusion_intersection_in_linear", script)
                self.assertIn("inclusion_linear_in_intersection", script)

    def test_reject_wrong_prime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "relation.rel"
            source.write_text("y(1)", encoding="utf-8")
            with self.assertRaises(ValueError):
                tool.make_script(32003, source)

    def test_reject_missing_source(self) -> None:
        with self.assertRaises(FileNotFoundError):
            tool.make_script(32009, Path("/missing/a5-d2.rel"))


if __name__ == "__main__":
    unittest.main()
