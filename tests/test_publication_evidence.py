"""Synthetic source and SVG fixtures; no historical replay in admission tests."""

from __future__ import annotations

import copy
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from publication_evidence import (
    blob_id,
    display_values,
    read_json,
    source_documents,
    svg_nodes,
    validate_display,
    validate_layout,
    verify_source_revision,
    within,
)

ASSETS = Path(__file__).resolve().parents[1] / "docs/evidence/teleportation-publication"
SVG_OPEN = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 1440"{root}>'
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=GIT_ENV)
    return done.stdout.strip()


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
            {"jobs": []},
            {
                "measured_statistics": {"summary_interval": summary(0.1, 0.2, 0.3, -0.3, -0.2, -0.1)},
                "replayed_statistics": {"summary_interval": summary(0.6, 0.7, 0.8, 0.4, 0.5, 0.6)},
            },
        ],
    }


def summary(lo: float, mean: float, hi: float, margin_lo: float, margin_mean: float, margin_hi: float) -> dict:
    method = "student_t_over_14_replicas"
    return {
        "selected_excess": {"lo": lo, "mean": mean, "hi": hi, "method": method},
        "selected_margin": {"lo": margin_lo, "mean": margin_mean, "hi": margin_hi, "method": method},
    }


class PublicationTests(unittest.TestCase):
    def test_values_are_derived_not_copied(self) -> None:
        values = display_values(sources())
        self.assertEqual(values["tuna17.svg"]["tuna_row_0_match"], "80.0%")
        self.assertEqual(values["kingston.svg"]["kingston_information_mean"], "+0.200")
        self.assertEqual(values["kingston.svg"]["kingston_margin_interval"], "\u22120.300 to \u22120.100")

    def test_measured_node_is_selected_and_replayed_values_are_not_displayed(self) -> None:
        document = sources()
        shown = display_values(document)["kingston.svg"]
        self.assertEqual(shown["kingston_information_mean"], "+0.200")
        self.assertEqual(shown["kingston_margin_mean"], "\u22120.200")
        self.assertNotIn("0.7", "".join(shown.values()))
        self.assertNotIn("0.5", "".join(shown.values()))
        # Swapping the two nodes swaps the displayed values: selection follows the key path, not the order.
        measured = document["kingston_collect"][1]
        measured["measured_statistics"], measured["replayed_statistics"] = (
            measured["replayed_statistics"],
            measured["measured_statistics"],
        )
        self.assertEqual(display_values(document)["kingston.svg"]["kingston_information_mean"], "+0.700")
        # Dropping the replayed node leaves the measured selection unchanged.
        del document["kingston_collect"][1]["replayed_statistics"]
        self.assertEqual(display_values(document)["kingston.svg"]["kingston_information_mean"], "+0.700")

    def test_measured_node_must_exist_exactly_once(self) -> None:
        absent = sources()
        del absent["kingston_collect"][1]["measured_statistics"]
        with self.assertRaises(ValueError):
            display_values(absent)
        duplicated = sources()
        duplicated["kingston_collect"].append(copy.deepcopy(duplicated["kingston_collect"][1]))
        with self.assertRaises(ValueError):
            display_values(duplicated)

    def test_unique_input_contract(self) -> None:
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
        document["kingston_collect"][1]["measured_statistics"]["summary_interval"]["selected_excess"]["lo"] = 0.9
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

    def test_invisible_presentation_of_a_bound_endpoint_fails(self) -> None:
        def page(root: str = "", text: str = "", inner: str = "80.0%") -> bytes:
            return (SVG_OPEN.format(root=root) + f'<text id="metric"{text}>{inner}</text></svg>').encode()

        validate_display(page(), {"metric": "80.0%"})
        validate_display(page(' fill-opacity="1"', ' font-size="22" fill="#f8fbff"'), {"metric": "80.0%"})
        mutations = {
            "visibility hidden": page(text=' visibility="hidden"'),
            "visibility collapse": page(text=' visibility="collapse"'),
            "display none": page(text=' display="none"'),
            "opacity zero": page(text=' opacity="0"'),
            "fill-opacity zero": page(text=' fill-opacity="0"'),
            "fill-opacity zero percent": page(text=' fill-opacity="0%"'),
            "font-size zero": page(text=' font-size="0"'),
            "font-size zero px": page(text=' font-size="0px"'),
            "fill none": page(text=' fill="none"'),
            "fill transparent": page(text=' fill="transparent"'),
            "unparseable opacity": page(text=' opacity="clear"'),
            "fill rgba zero alpha": page(text=' fill="rgba(255,255,255,0)"'),
            "fill hex zero alpha": page(text=' fill="#ffffff00"'),
            "fill short hex": page(text=' fill="#fff"'),
            "transform scale zero": page(text=' transform="scale(0)"'),
            "ancestor fill zero alpha": page(root=' fill="#ffffff00"'),
            "ancestor transform": page(root=' transform="scale(0)"'),
            "span fill zero alpha": page(inner='80.0%<tspan fill="rgba(0,0,0,0)"/>'),
            "span transform": page(inner='80.0%<tspan transform="scale(0)"/>'),
            "ancestor visibility hidden": page(root=' visibility="hidden"'),
            "ancestor display none": page(root=' display="none"'),
            "ancestor opacity zero": page(root=' opacity="0"'),
            "ancestor fill-opacity zero": page(root=' fill-opacity="0"'),
            "ancestor font-size zero": page(root=' font-size="0"'),
            "span visibility hidden": page(inner='80.0%<tspan visibility="hidden"/>'),
            "span font-size zero": page(inner='80.0%<tspan font-size="0"/>'),
            "style display none": page(text=' style="display:none"'),
            "style visibility hidden": page(text=' style="visibility:hidden"'),
            "style opacity zero": page(text=' style="opacity:0"'),
            "style fill-opacity zero": page(text=' style="fill-opacity:0"'),
            "style font-size zero": page(text=' style="font-size:0"'),
        }
        for label, data in mutations.items():
            with self.subTest(label), self.assertRaises(ValueError):
                validate_display(data, {"metric": "80.0%"})

    def test_processing_instructions_fail_in_prolog_and_body(self) -> None:
        body = SVG_OPEN.format(root="") + '<text id="metric">80.0%</text></svg>'
        sheet = '<?xml-stylesheet type="text/css" href="https://example.invalid/hide.css"?>'
        for label, document in {
            "prolog stylesheet": sheet + body,
            "body stylesheet": body.replace("<text", sheet + "<text", 1),
            "prolog other target": "<?other data?>" + body,
            "trailing": body + sheet,
        }.items():
            with self.subTest(label), self.assertRaises(ValueError):
                svg_nodes(document.encode())
        svg_nodes(("<?xml version='1.0' encoding='utf-8'?>\n" + body).encode())

    def test_committed_masters_pass_layout_and_visibility(self) -> None:
        for name in ("tuna17.svg", "kingston.svg"):
            data = (ASSETS / name).read_bytes()
            validate_layout(data, name)
            root, nodes = svg_nodes(data)
            bound = {
                ident: node
                for ident, node in nodes.items()
                if ident.startswith(("tuna_", "kingston_")) and node.tag.endswith("}text")
            }
            self.assertTrue(bound)
            validate_display(data, {ident: "".join(node.itertext()) for ident, node in bound.items()})

    def test_tuna_range_is_derived_from_unrounded_fidelities(self) -> None:
        document = sources()
        rows = document["tuna_analysis"]["teleport"]
        self.assertEqual(display_values(document)["tuna17.svg"]["tuna_range"].split("-")[0], "The 0.0")
        for row, score in zip(rows, (0.74560546875, 0.8265380859375, 0.84442138671875, 0.86224365234375), strict=True):
            row["corrected_fidelity"] = score
        # The difference of the rounded percentages (86.2 - 74.6) would read 11.6.
        self.assertEqual(
            display_values(document)["tuna17.svg"]["tuna_range"],
            "The 11.7-point range cannot isolate input sensitivity",
        )

    def test_source_revision_blob_ids_are_checked_against_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            data = b'{"value":1}\n'
            (root / "fixture.json").write_bytes(data)
            git(root, "add", "fixture.json")
            git(root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture")
            revision = git(root, "rev-parse", "HEAD")
            manifest: dict[str, Any] = {
                "schema": "teleportation-publication-sources-v1",
                "source_revision": revision,
                "sources": [{"role": "fixture", "path": "fixture.json", "git_blob_sha1": blob_id(data)}],
            }
            self.assertEqual(verify_source_revision(root, manifest), "verified")
            wrong_blob = copy.deepcopy(manifest)
            wrong_blob["sources"][0]["git_blob_sha1"] = blob_id(b'{"value":2}\n')
            with self.assertRaises(ValueError):
                verify_source_revision(root, wrong_blob)
            wrong_path = copy.deepcopy(manifest)
            wrong_path["sources"][0]["path"] = "absent.json"
            with self.assertRaises(ValueError):
                verify_source_revision(root, wrong_path)
            for bad in ("0" * 40, "HEAD", "--help", revision[:12]):
                with self.subTest(bad), self.assertRaises(ValueError):
                    verify_source_revision(root, {**manifest, "source_revision": bad})
            # A working-tree edit leaves the committed blob, which the manifest names, as the verified one.
            (root / "fixture.json").write_bytes(b'{"value":2}\n')
            self.assertEqual(verify_source_revision(root, manifest), "verified")

    def test_source_revision_is_unverified_outside_a_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"source_revision": "0" * 40, "sources": []}
            self.assertTrue(verify_source_revision(Path(tmp), manifest).startswith("unverified: "))


if __name__ == "__main__":
    unittest.main()
