"""Check output-alias rejection and retained distinct-format rendering."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import render_rank_sector_norms as renderer


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def snapshot(directory: Path) -> dict[str, tuple[object, ...]]:
    """Record names, link targets, file bytes, and file identities in the fixture."""
    contents: dict[str, tuple[object, ...]] = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory).as_posix()
        if path.is_symlink():
            contents[relative] = ("symlink", os.readlink(path))
        elif path.is_file():
            stat = path.stat()
            contents[relative] = ("file", path.read_bytes(), stat.st_dev, stat.st_ino, stat.st_nlink)
        else:
            contents[relative] = ("directory",)
    return contents


def arguments(output: Path, png: Path, check: bool = False) -> list[str]:
    return ["render_rank_sector_norms.py", "--out", str(output), "--png", str(png), *(["--check"] if check else [])]


def main() -> int:
    rejected_cli = 0
    rejected_direct = 0
    with TemporaryDirectory(prefix="rank-sector-output-contract-") as temporary:
        directory = Path(temporary)
        protected = directory / "protected.svg"
        protected.write_bytes(b"retained output sentinel\n")
        subdirectory = directory / "subdirectory"
        subdirectory.mkdir()
        symbolic = directory / "symbolic.png"
        symbolic.symlink_to(protected.name)
        linked_directory = directory / "linked-directory"
        linked_directory.symlink_to(directory, target_is_directory=True)
        hardlink = directory / "hardlink.png"
        hardlink.hardlink_to(protected)
        missing = directory / "missing.svg"
        dangling = directory / "dangling.png"
        dangling.symlink_to(missing.name)
        pairs = (
            ("same path", protected, protected),
            ("canonical path", protected, subdirectory / ".." / protected.name),
            ("symbolic file", protected, symbolic),
            ("symbolic directory", protected, linked_directory / protected.name),
            ("hardlink", protected, hardlink),
            ("dangling symbolic file", missing, dangling),
        )
        before = snapshot(directory)
        for label, output, png in pairs:
            for check in (False, True):
                stderr = io.StringIO()
                with (
                    patch.object(sys, "argv", arguments(output, png, check)),
                    patch.object(renderer, "verified_traces", side_effect=RuntimeError("alias reached exact algebra")),
                    patch.object(renderer, "render", side_effect=RuntimeError("alias reached rendering")),
                    contextlib.redirect_stderr(stderr),
                ):
                    try:
                        renderer.main()
                    except SystemExit as error:
                        require(error.code == 2, f"{label}: CLI returned another error")
                    else:
                        raise RuntimeError(f"{label}: CLI accepted aliased output paths")
                require("--out and --png must identify distinct files" in stderr.getvalue(), "alias diagnostic differs")
                require(snapshot(directory) == before, f"{label}: rejected CLI changed the fixture")
                rejected_cli += 1
            try:
                renderer.render((), output, png)
            except ValueError as error:
                require("--out and --png" in str(error), f"{label}: direct render returned another error")
            else:
                raise RuntimeError(f"{label}: direct render accepted aliased output paths")
            require(snapshot(directory) == before, f"{label}: rejected direct render changed the fixture")
            rejected_direct += 1

        process = subprocess.run(
            [sys.executable, str(Path(renderer.__file__)), *arguments(protected, hardlink, True)[1:]],
            capture_output=True,
            text=True,
            check=False,
        )
        require(process.returncode == 2 and "--out and --png" in process.stderr, "entry-point alias rejection failed")
        require(snapshot(directory) == before, "rejected entry-point command changed the fixture")

        traces = renderer.verified_traces()
        output, png = directory / "valid.svg", directory / "valid.png"
        for check in (False, True):
            before_check = snapshot(directory)
            stdout = io.StringIO()
            with (
                patch.object(sys, "argv", arguments(output, png, check)),
                patch.object(renderer, "verified_traces", return_value=traces),
                contextlib.redirect_stdout(stdout),
            ):
                require(renderer.main() == 0, "distinct output paths failed")
            require(
                json.loads(stdout.getvalue())["verified_acquisition_values"] == 160, "exact verification count changed"
            )
            if check:
                require(snapshot(directory) == before_check, "distinct-path check rewrote retained files")
        require(output.read_bytes().startswith(b"<?xml"), "distinct SVG output has another format")
        require(png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "distinct PNG output has another format")
        for generated, retained in (
            (output, renderer.ROOT / "results/ripple/rank-sector-norms.svg"),
            (png, renderer.ROOT / "results/ripple/rank-sector-norms.png"),
        ):
            require(renderer.same_image(retained, generated), f"{retained.name}: renderer output changed")
        report = {
            "rejected_cli_aliases": rejected_cli,
            "rejected_direct_aliases": rejected_direct,
            "entry_point_rejections": 1,
            "distinct_path_render_and_check": True,
            "verified_acquisition_values": 160,
            "svg_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
        }
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
