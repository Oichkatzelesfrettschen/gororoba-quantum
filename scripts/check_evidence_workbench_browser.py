"""Check a separately generated workbench with an explicitly selected browser.

The document-content harness exercises UI contracts, not native file-handler
behavior, assistive technology, physical touch hardware, or source authenticity.
No provider or external website is contacted by the loaded document.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--engine", choices=("chromium", "firefox", "webkit"), default="chromium")
    parser.add_argument("--executable", type=Path)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        raise ValueError("choose a new report directory")
    args.out.mkdir(parents=True)
    source = args.html.read_bytes()
    checks: list[str] = []
    errors: list[str] = []
    requests: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise ValueError(name)
        checks.append(name)

    with sync_playwright() as p:
        engine = getattr(p, args.engine)
        browser = engine.launch(executable_path=str(args.executable) if args.executable else None, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050}, accept_downloads=True)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("request", lambda r: requests.append(r.url))
        page.set_content(source.decode(), wait_until="load")
        check(page.evaluate("window.__workbenchReady === true"), "document_ready")
        check(page.locator("#error").is_hidden(), "no_initial_error")
        initial = page.evaluate("EvidenceWorkbench.saveState()")
        for view in ("ramsey", "dependence", "blocks", "members", "rank", "optical", "provenance"):
            page.click(f'[data-view="{view}"]')
            check(page.locator("#error").is_hidden(), "workspace_" + view)
            check(bool(page.locator("#plot > title").text_content()), "figure_title_" + view)
        page.evaluate("value => EvidenceWorkbench.restore(value)", initial)
        if page.evaluate("EvidenceWorkbench.data.ramsey !== null"):
            for geometry in ("xy", "bloch", "setting"):
                page.select_option("#geometry", geometry)
                check(page.locator("#error").is_hidden(), "geometry_" + geometry)
            page.select_option("#geometry", "xy")
            check(page.locator("#yaw").is_disabled(), "xy_camera_controls_disabled")
            page.select_option("#geometry", "setting")
            check(page.locator("#uncertainty").is_disabled(), "setting_uncertainty_control_disabled")
            check(page.locator("#mle").is_disabled(), "setting_mle_overlay_disabled")
            page.select_option("#geometry", "bloch")
            page.click("#theme")
            page.screenshot(path=str(args.out / "bloch.png"), full_page=False)
            page.select_option("#geometry", "xy")
            page.locator("#mle").check()
            check(page.evaluate("EvidenceWorkbench.state.mle"), "constrained_xy_overlay")
            page.locator("#plot").focus()
            before = page.evaluate("EvidenceWorkbench.state.index")
            page.keyboard.press("ArrowRight")
            after = page.evaluate("EvidenceWorkbench.state.index")
            check(after != before, "keyboard_record_selection")
            page.click("#nextDelay")
            check(
                page.evaluate(
                    "EvidenceWorkbench.ramseyRows().every(p => String(p.t) === EvidenceWorkbench.state.delay)"
                ),
                "acquired_setting_filter",
            )
            page.emulate_media(reduced_motion="reduce")
            page.click("#play")
            check("Reduced motion" in page.locator("#status").inner_text(), "reduced_motion_prevents_playback")
            page.emulate_media(reduced_motion="no-preference")
        for color in ("condition", "qubit", "monochrome"):
            page.select_option("#color", color)
            check(page.locator("#error").is_hidden(), "color_" + color)
        rejected = page.evaluate("""() => {const v=EvidenceWorkbench.saveState();v.bundle_sha256='wrong';
            try {EvidenceWorkbench.restore(v);return false;} catch {return true;}}""")
        check(rejected, "foreign_saved_view_rejected")
        page.evaluate("value => EvidenceWorkbench.restore(value)", initial)
        if page.evaluate("EvidenceWorkbench.data.acquisitions.length > 0"):
            page.click('[data-view="members"]')
            page.locator("#preparation").check()
            saved = page.evaluate("EvidenceWorkbench.saveState()")
            page.locator("#preparation").uncheck()
            page.evaluate("value => EvidenceWorkbench.restore(value)", saved)
            check(page.locator("#preparation").is_checked(), "model_layers_round_trip")
            page.click('[data-view="dependence"]')
            page.select_option("#metric", "correlation")
            check(page.locator("#error").is_hidden(), "correlation_matrix")
            if page.evaluate("EvidenceWorkbench.data.acquisitions[0].payload.evidence_kind === 'synthetic_fixture'"):
                check("SYNTHETIC FIXTURE" in page.locator("#plotTitle").inner_text(), "synthetic_label")
            page.screenshot(path=str(args.out / "dependence.png"), full_page=False)
        page.evaluate("value => EvidenceWorkbench.restore(value)", initial)
        with page.expect_download() as event:
            page.click("#exportSVG")
        svg_path = args.out / "export.svg"
        event.value.save_as(str(svg_path))
        svg = svg_path.read_text()
        check("<metadata>" in svg and "bundle_sha256" in svg, "svg_source_metadata")
        check("Evidence source:" in svg and "Selected context:" in svg, "svg_visible_context")
        with page.expect_download() as event:
            page.click("#exportPNG")
        png_path = args.out / "export.png"
        event.value.save_as(str(png_path))
        check(png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "png_bytes")
        with page.expect_download() as event:
            page.click("#exportCSV")
        csv_path = args.out / "export.csv"
        event.value.save_as(str(csv_path))
        check("Bundle SHA-256" in csv_path.read_text(), "csv_source_context")
        for width in (320, 390, 768, 1440):
            page.set_viewport_size({"width": width, "height": 1000})
            page.wait_for_timeout(80)
            check(page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"no_body_overflow_{width}")
            check(page.locator("#error").is_hidden(), f"responsive_{width}")
            if width in (390, 1440):
                page.locator("#plot").scroll_into_view_if_needed()
                page.screenshot(path=str(args.out / f"viewport-{width}.png"), full_page=False)
        external = [url for url in requests if url.startswith(("http://", "https://"))]
        check(not external, "zero_external_network_requests")
        check(not errors, "zero_uncaught_errors")
        report = {
            "passed": True,
            "engine": args.engine,
            "browser_version": browser.version,
            "html_sha256": hashlib.sha256(source).hexdigest(),
            "checks": checks,
            "document_requests": requests,
            "external_network_requests": external,
            "page_errors": errors,
            "boundary": "document-content tests; no native file-handler, screenreader, or physical-touch certification",
        }
        (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        browser.close()
    print(json.dumps({"passed": True, "checks": len(checks), "report": str(args.out / "report.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
