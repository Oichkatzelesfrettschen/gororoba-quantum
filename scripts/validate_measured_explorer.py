"""Browser validation receipt for the measured Cayley-Dickson explorer.

A headless Chromium session loads results/ripple/measured-cayley-dickson-ripples.html,
selects every acquisition family, and records each select control's option
count, uncaught page errors, and whether the page overflows a phone-width
viewport horizontally. The receipt binds those observations to the SHA-256 of
the page, the two measured evidence files, the page template, and the two
scripts that produce them. --check recomputes the hashes without a browser,
so a regenerated artifact fails until the browser validation reruns.

The browser run needs ci/requirements-browser.txt and a Chromium binary,
CHROMIUM or /usr/bin/chromium, falling back to Playwright's own download.

Usage: "$PYTHON" scripts/validate_measured_explorer.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "results/ripple/measured-acquisition-validation.json"
PAGE = ROOT / "results/ripple/measured-cayley-dickson-ripples.html"
SOURCES = (
    "gororoba_quantum/visualizations/measured_cayley_dickson_ripples.html",
    "results/ripple/measured-cayley-dickson-ripples.html",
    "results/ripple/measured-rank-sector.json",
    "results/ripple/measured-ripple.json",
    "scripts/extract_measured_ripple.py",
    "scripts/render_measured_ripple.py",
    "scripts/validate_measured_explorer.py",
)
# Controls each family must populate; an empty one marks a rendering regression.
REQUIRED_CONTROLS = {
    "ripple": ("kite", "edge", "phase", "walk", "depth", "pub", "member"),
    "rank-sector": ("sector", "probe", "pub", "member"),
}
DESKTOP = (1440, 1050)
MOBILE = (390, 844)


def digests() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def expected_families() -> list[str]:
    names = ("results/ripple/measured-ripple.json", "results/ripple/measured-rank-sector.json")
    return sorted(str(json.loads((ROOT / name).read_text())["family"]) for name in names)


def _failures(checks: dict[str, Any]) -> list[str]:
    failures = [f"page error: {error}" for error in checks["page_errors"]]
    if sorted(checks["families"]) != expected_families():
        failures.append(f"families {checks['families']} differ from the evidence {expected_families()}")
    failures += [
        f"{family} overflows a phone viewport" for family, wide in checks["mobile_horizontal_overflow"].items() if wide
    ]
    failures += [f"{family} leaves {names} empty" for family, names in checks["missing_controls"].items() if names]
    return failures


def physical_jobs() -> list[str]:
    """Job identities of every member in the two measured evidence files."""
    jobs = set()
    for name in ("results/ripple/measured-ripple.json", "results/ripple/measured-rank-sector.json"):
        evidence = json.loads((ROOT / name).read_text())
        jobs |= {str(member["job_id"]) for member in evidence["members"].values()}
    return sorted(jobs)


def browse() -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    errors: list[str] = []
    with sync_playwright() as playwright:
        executable = os.environ.get("CHROMIUM", "/usr/bin/chromium")
        browser = playwright.chromium.launch(
            executable_path=executable if Path(executable).exists() else None, headless=True
        )
        page = browser.new_page(viewport={"width": DESKTOP[0], "height": DESKTOP[1]})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(PAGE.as_uri())
        page.wait_for_load_state("load")
        families = page.eval_on_selector_all("#family option", "options => options.map(o => o.value)")
        controls = {}
        for family in families:
            page.select_option("#family", family)
            controls[family] = page.eval_on_selector_all(
                "select", "selects => Object.fromEntries(selects.map(s => [s.id, s.options.length]))"
            )
        page.set_viewport_size({"width": MOBILE[0], "height": MOBILE[1]})
        overflow = {}
        for family in families:
            page.select_option("#family", family)
            overflow[family] = page.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
        version = browser.version
        browser.close()
    return {
        "browser": f"Chromium {version} headless",
        "desktop_viewport": list(DESKTOP),
        "mobile_viewport": list(MOBILE),
        "families": families,
        "select_option_counts": controls,
        "mobile_horizontal_overflow": overflow,
        "missing_controls": {
            family: [name for name in REQUIRED_CONTROLS.get(family, ()) if not controls[family].get(name)]
            for family in families
        },
        "page_errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the receipt's hashes without a browser")
    arguments = parser.parse_args(argv)
    if arguments.check:
        receipt = json.loads(RECEIPT.read_text())
        current = digests()
        stale = sorted(name for name, value in current.items() if receipt["source_files"].get(name) != value)
        failing = _failures(receipt["browser_checks"])
        if stale or failing or receipt["physical_job_ids"] != physical_jobs():
            print(f"explorer receipt is stale or failing: {stale} {failing}")
            return 1
        print("explorer receipt binds the shipped page, evidence, and producers")
        return 0
    checks = browse()
    receipt = {
        "schema": "measured-acquisition-visual-validation-v2",
        "evidence_kind": "collected_hardware",
        "observed_at": datetime.now(UTC).isoformat(),
        "boundary": (
            "The measured artifacts replay retained raw counts and their inference gates. Browser checks "
            "establish rendering and control behavior; algebra, calibration replay and hardware causal "
            "attribution remain distinct."
        ),
        "browser_checks": checks,
        "physical_job_ids": physical_jobs(),
        "source_files": digests(),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    failures = _failures(checks)
    print(f"explorer validated: {len(checks['families'])} families, failures {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
