"""Synthetic source and SVG fixtures; no historical replay in admission tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from publication_evidence import (
    blob_id,
    display_values,
    read_json,
    source_documents,
    svg_nodes,
    validate_display,
    within,
)


def sources() -> dict:
    return {
        "tuna_analysis": {
            "backend": "tuna_17",
            "teleport": [
                {
                    "input": label,
                    "I": 0,
                    "P1": 1,
                    "P2": 2,
                    "D": 3,
                    "corrected_fidelity": 0.8,
                    "corrected_ci95": [0.7, 0.9],
                }
                for label in ("0", "1", "+", "+i")
            ],
        },
        "tuna_cases": {"backend": "tuna_17", "shots": 1000, "nqubits": 4},
        "kingston_collect": [
            {
                "summary_interval": {
                    "selected_excess": {"lo": 0.1, "mean": 0.2, "hi": 0.3, "method": "student_t_over_14_replicas"},
                    "selected_margin": {"lo": -0.3, "mean": -0.2, "hi": -0.1, "method": "student_t_over_14_replicas"},
                }
            }
        ],
    }


class PublicationTests(unittest.TestCase):
    def test_values_are_derived_not_copied(self) -> None:
        values = display_values(sources())
        self.assertEqual(values["tuna17.svg"]["tuna_row_0_match"], "80.0%")
        self.assertEqual(values["kingston.svg"]["kingston_information_mean"], "+0.200")
        self.assertEqual(values["kingston.svg"]["kingston_margin_interval"], "\u22120.300 to \u22120.100")

    def test_unique_summary_and_input_contract(self) -> None:
        document = sources()
        document["kingston_collect"] *= 2
        with self.assertRaises(ValueError):
            display_values(document)
        document = sources()
        document["tuna_analysis"]["teleport"][0]["input"] = "1"
        with self.assertRaises(ValueError):
            display_values(document)

    def test_numerical_and_interval_mutations_fail(self) -> None:
        for value in (True, float("nan"), float("inf"), "0.2", 2):
            document = sources()
            document["tuna_analysis"]["teleport"][0]["corrected_fidelity"] = value
            with self.assertRaises(ValueError):
                display_values(document)
        document = sources()
        document["kingston_collect"][0]["summary_interval"]["selected_excess"]["lo"] = 0.9
        with self.assertRaises(ValueError):
            display_values(document)

    def test_json_rejects_duplicates_and_nonfinite_constants(self) -> None:
        for data in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.assertRaises(ValueError):
                read_json(data)

    def test_source_digest_is_checked_before_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = b'{"value":1}\n'
            (root / "fixture.json").write_bytes(data)
            manifest = {
                "schema": "teleportation-publication-sources-v1",
                "sources": [
                    {"role": "fixture", "path": "fixture.json", "git_blob_sha1": blob_id(data)},
                ],
            }
            documents, receipts = source_documents(root, manifest)
            self.assertEqual(documents["fixture"], {"value": 1})
            self.assertEqual(receipts[0]["bytes"], len(data))
            (root / "fixture.json").write_bytes(b'{"value":2}\n')
            with self.assertRaises(ValueError):
                source_documents(root, manifest)

    def test_path_escape_and_symlink_escape_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            for path in ("../escape", str(root / "absolute")):
                with self.assertRaises(ValueError):
                    within(root, path)
            outside = Path(tmp) / "outside"
            outside.write_text("fixture")
            (root / "link").symlink_to(outside)
            with self.assertRaises(ValueError):
                within(root, "link")

    def test_endpoint_node_binding(self) -> None:
        data = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 1440"><text id="metric">80.0%</text></svg>'
        validate_display(data, {"metric": "80.0%"})
        for changed in (
            data.replace(b"80.0", b"99.9"),
            data.replace(b'id="metric"', b'id="other"'),
            data.replace(b'id="metric"', b'id="metric" opacity="0"'),
        ):
            with self.assertRaises(ValueError):
                validate_display(changed, {"metric": "80.0%"})

    def test_active_svg_content_and_duplicate_ids_fail(self) -> None:
        base = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 1440">{}</svg>'
        for content in (
            "<script/>",
            "<image/>",
            '<text onclick="x()"/>',
            '<text href="remote"/>',
            '<text id="a"/><text id="a"/>',
            '<script xmlns="urn:foreign"/>',
            '<text style="display:none"/>',
            '<rect fill="url(remote)"/>',
        ):
            with self.assertRaises(ValueError):
                svg_nodes(base.format(content).encode())
        with self.assertRaises(ValueError):
            svg_nodes(b"<!DOCTYPE svg><svg/>")


if __name__ == "__main__":
    unittest.main()
