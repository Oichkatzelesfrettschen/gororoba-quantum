"""Check or render the historical SVG masters, without executing archive code.

Full mode binds the rendered metrics to pinned repository records. The
explicit --layout-only mode reports evidence_bound=false. Rendering is an
on-demand dependency; bounded unit tests require neither Inkscape nor fonts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from publication_evidence import (  # noqa: E402
    display_values,
    read_json,
    source_documents,
    validate_display,
    validate_layout,
    verify_source_revision,
)
from teleportation_contract import require  # noqa: E402

ASSETS = ROOT / "docs/evidence/teleportation-publication"


def rendered_bounds(svg: Path) -> dict[str, tuple[float, ...]]:
    result = subprocess.run(
        ["inkscape", str(svg), "--query-all"], capture_output=True, text=True, check=True, timeout=60
    )
    bounds = {}
    for line in result.stdout.splitlines():
        parts = line.split(",")
        if len(parts) == 5:
            bounds[parts[0]] = tuple(map(float, parts[1:]))
    return bounds


def build(source_root: Path, out: Path, layout_only: bool = False, render: bool = False) -> dict[str, Any]:
    manifest = read_json((ASSETS / "sources.json").read_bytes())
    receipts: list[dict[str, Any]] = []
    values = None
    revision_check = "not checked: layout only"
    if not layout_only:
        documents, receipts = source_documents(source_root, manifest)
        revision_check = verify_source_revision(source_root, manifest)
        values = display_values(documents)
    require(not out.exists(), "release directory exists; do not overwrite a retained release")
    # Validate all inputs before creating any release file.
    masters = {}
    for name in ("tuna17.svg", "kingston.svg"):
        data = (ASSETS / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == manifest["masters"][name]["sha256"], f"master drift: {name}")
        validate_layout(data, name)
        if values is not None:
            validate_display(data, values[name])
        masters[name] = data
    if render:
        require(shutil.which("inkscape") is not None, "Inkscape is required for rendering")
    out.mkdir(parents=True, exist_ok=False)
    try:
        for name, data in masters.items():
            (out / name).write_bytes(data)
        report: dict[str, Any] = {
            "schema": "teleportation-publication-release-v1",
            "source_revision": manifest["source_revision"],
            "source_revision_check": revision_check,
            "evidence_bound": not layout_only,
            "source_receipts": receipts,
            "hardware_replayed": False,
            "renderer": None,
            "text_bounds": {},
            "scope": "historical display/source consistency and layout, not an independent hardware certification",
        }
        if render:
            version = subprocess.run(["inkscape", "--version"], capture_output=True, text=True, check=True, timeout=10)
            report["renderer"] = version.stdout.strip()
            for name in masters:
                svg = out / name
                subprocess.run(
                    [
                        "inkscape",
                        str(svg),
                        f"--export-filename={svg.with_suffix('.png')}",
                        "--export-width=2560",
                        "--export-height=1440",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60,
                )
            bounds = rendered_bounds(out / "tuna17.svg")
            x, y, width, height = bounds["tuna_decoder_box"]
            for ident in ("tuna_decoder_ideal", "tuna_decoder_note"):
                tx, ty, tw, th = bounds[ident]
                require(tx >= x + 12 and tx + tw <= x + width - 12, f"decoder horizontal overflow: {ident}")
                require(ty >= y and ty + th <= y + height, f"decoder vertical overflow: {ident}")
                report["text_bounds"][ident] = {"right_clearance_px": x + width - tx - tw}
        report["files"] = {
            path.name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
            for path in sorted(out.iterdir())
            if path.is_file()
        }
        (out / "release.json").write_text(
            json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        return report
    except BaseException:
        # Only the directory created by this invocation is removed.
        shutil.rmtree(out)
        raise


def check(source_root: Path) -> dict[str, Any]:
    """Build the full source-bound release in temporary storage and check its receipt against the manifest."""
    manifest = read_json((ASSETS / "sources.json").read_bytes())
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "release"
        report = build(source_root, out)
        require(read_json((out / "release.json").read_bytes()) == report, "release.json differs from the receipt")
        require(report["evidence_bound"] is True and report["hardware_replayed"] is False, "receipt scope flags")
        require(report["source_revision"] == manifest["source_revision"], "receipt source_revision")
        require(report["source_revision_check"] == "verified", f"source_revision: {report['source_revision_check']}")
        require(
            [(r["role"], r["path"], r["git_blob_sha1"]) for r in report["source_receipts"]]
            == [(s["role"], s["path"], s["git_blob_sha1"]) for s in manifest["sources"]],
            "receipt sources differ from the manifest",
        )
        require(
            {name: entry["sha256"] for name, entry in report["files"].items()}
            == {name: entry["sha256"] for name, entry in manifest["masters"].items()},
            "receipt masters differ from the manifest",
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true", help="build the source-bound release in a temporary directory")
    parser.add_argument("--layout-only", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    if args.check == (args.out is not None) or (args.check and (args.layout_only or args.render)):
        parser.error("give exactly one of --out or --check; --check takes no other mode flag")
    try:
        report = (
            check(args.source_root) if args.check else build(args.source_root, args.out, args.layout_only, args.render)
        )
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    if args.check:
        print(
            f"source-bound release verified: {len(report['source_receipts'])} sources, "
            f"{len(report['files'])} masters, source_revision {report['source_revision_check']}"
        )
    else:
        print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
