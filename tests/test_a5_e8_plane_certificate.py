"""Source-bound E8 intersection certificate generator tests (no Singular needed)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "a5_e8_plane_certificate.py"
SPEC = importlib.util.spec_from_file_location("a5_e8_plane_certificate", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load {SOURCE}")
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class PlaneCertificateTests(unittest.TestCase):
    def test_both_primes_give_the_stated_checks(self) -> None:
        for prime in (32009, 32029):
            script = tool.make_script(prime, "y(1)*y(2),\n32008*y(3)^2+y(4)*y(5)")
            self.assertIn(f"ring Y={prime},(y(1..21)),dp;", script)
            self.assertIn("ideal K=\ny(1)*y(2),\n32008*y(3)^2+y(4)*y(5);", script)
            self.assertIn("minAssChar(std(K+N))", script)
            self.assertIn("nlin==18", script)
            self.assertIn("RESULT E8_EXACT_PROJECTIVE_PLANE_PASS", script)
            self.assertIn("inclusion_intersection_in_linear", script)
            self.assertIn("inclusion_linear_in_intersection", script)

    def test_script_digest_follows_the_relation_bytes(self) -> None:
        first = tool.make_script(32009, "y(1)*y(2)")
        second = tool.make_script(32009, "y(1)*y(3)")
        self.assertNotEqual(first, second)
        self.assertNotIn("read(", first)

    def test_reject_wrong_prime(self) -> None:
        with self.assertRaises(ValueError):
            tool.make_script(32003, "y(1)")

    def test_reject_text_outside_polynomial_syntax(self) -> None:
        for text in ("", 'y(1); system("sh","true")', 'y(1)"', "x(1)"):
            with self.assertRaises(ValueError):
                tool.make_script(32009, text)


if __name__ == "__main__":
    unittest.main()
