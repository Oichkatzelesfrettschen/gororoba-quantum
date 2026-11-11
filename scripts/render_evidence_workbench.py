"""Build an offline, source-bound workbench from explicitly selected retained inputs.

Example: python scripts/render_evidence_workbench.py --ramsey observations.csv
--acquisition measured-ripple.json --optical replication-score.json --out view.html
No service, provider submission, model refit, or retained-file rewrite occurs.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import evidence_workbench as evidence  # noqa: E402

ASSETS = ROOT / "gororoba_quantum" / "visualizations" / "evidence_workbench"


def build_bundle(args: argparse.Namespace) -> tuple[dict[str, Any], list[Path]]:
    paths = list(args.acquisition) + list(args.optical) + ([args.ramsey] if args.ramsey else [])
    evidence.require(bool(paths), "at least one input is required")
    evidence.require(not args.run_root or len(args.run_root) == len(args.acquisition), "provide one run root per acquisition")
    bundle: dict[str, Any] = {
        "schema": evidence.SCHEMA,
        "revision": args.revision,
        "sources": [],
        "ramsey": None,
        "acquisitions": [],
        "optical": [],
        "boundaries": [
            "Hardware, synthetic fixtures, fitted quantities and exact references retain separate identities.",
            "Joint events pair only within one (job_id, PUB, returned shot position).",
            "Returned shot order is not certified physical chronology; block plots are descriptive.",
            "A Bloch-compatible set is an admissible set, not Z tomography or a measured trajectory.",
        ],
    }

    def read(path: Path, kind: str) -> bytes:
        contents = evidence.read_bytes(path)
        bundle["sources"].append({"name": path.name, "kind": kind, "sha256": evidence.sha256(contents), "bytes": len(contents)})
        return contents

    if args.ramsey:
        bundle["ramsey"] = evidence.load_ramsey(read(args.ramsey, "ramsey_counts"))
    for i, path in enumerate(args.acquisition):
        checked = evidence.validate_acquisition(evidence.decode(read(path, "acquisition")))
        if args.run_root:
            from parallel import ordered_map

            checked = evidence.verify_sources(checked, args.run_root[i], lambda fn, tasks: ordered_map(fn, list(tasks)))
        bundle["acquisitions"].append(checked)
    for path in args.optical:
        bundle["optical"].append(evidence.load_ascella(evidence.decode(read(path, "optical_cohort")), path.name))
    return bundle, paths + list(args.run_root) + [ASSETS]


def render(bundle: dict[str, Any]) -> bytes:
    payload = evidence.canonical(bundle)
    identity = evidence.sha256(payload)
    serialized = payload.decode().replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    math_js = (ASSETS / "math.js").read_text(encoding="utf-8")
    app_js = (ASSETS / "app.js").read_text(encoding="utf-8")
    hashes = " ".join("'sha256-" + base64.b64encode(hashlib.sha256(code.encode()).digest()).decode() + "'" for code in (math_js, app_js))
    rows = (bundle.get("ramsey") or {}).get("rows", [])
    static = "<table><caption>Embedded Ramsey count records</caption><tr><th>Condition</th><th>Qubit</th><th>Delay (us)</th><th>X zeros / shots</th><th>Y zeros / shots</th></tr>"
    for row in rows:
        values = [row["condition"], row["qubit"], row["t"], f"{row['kx']}/{row['nx']}", f"{row['ky']}/{row['ny']}"]
        static += "<tr>" + "".join("<td>" + html.escape(str(v)) + "</td>" for v in values) + "</tr>"
    static += "</table>"
    replacements = {
        "__DATA__": serialized,
        "__DATA_SHA__": identity,
        "__STYLE__": (ASSETS / "style.css").read_text(encoding="utf-8"),
        "__MATH__": math_js,
        "__APP__": app_js,
        "__SCRIPT_POLICY__": hashes,
        "__STATIC__": static,
    }
    template = (ASSETS / "template.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        evidence.require(template.count(key) == 1, f"template token count differs: {key}")
        template = template.replace(key, value)
    return template.encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ramsey", type=Path)
    parser.add_argument("--acquisition", action="append", type=Path, default=[])
    parser.add_argument("--run-root", action="append", type=Path, default=[], help="Verify source hashes and replay raw statistics, in acquisition order")
    parser.add_argument("--optical", action="append", type=Path, default=[])
    parser.add_argument("--revision", default="unavailable", help="Source checkout commit; unavailable is retained rather than guessed")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Compare existing HTML without writing")
    args = parser.parse_args()
    try:
        bundle, protected = build_bundle(args)
        result = render(bundle)
        if args.check:
            evidence.require(evidence.read_bytes(args.out) == result, "rendered output differs")
        else:
            evidence.write_new(args.out, result, protected)
        print(json.dumps({"schema": evidence.SCHEMA, "html_sha256": evidence.sha256(result), "sources": bundle["sources"], "acquisitions": len(bundle["acquisitions"]), "optical_cohorts": len(bundle["optical"]), "check_only": args.check}, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, IndexError, OSError, ArithmeticError) as error:
        print(f"evidence workbench: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
