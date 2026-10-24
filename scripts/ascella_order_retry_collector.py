"""Check that the current collector reproduces the retained Ascella order-retry analysis.

results/quandela/runs/ascella-mosaiq-update-order-retry/analysis.json is
retained evidence: a research-state claim binds its sha256, and its
``source_sha256`` names the bytes of every file the producing analysis read,
the collector modules included. The run's own ``analysis.py --check`` is the
historical replay: it requires those exact bytes, so it passes on a tree
whose collector modules hold the recorded bytes and on no tree whose
collector moved.

This check validates the current collector against that record instead. It
recomputes the analysis with the modules the tree holds now and requires:
- every field outside ``source_sha256`` to match the retained record, counts,
  labels and types exactly and floats within the shared libm tolerance of
  ``bdsc_certificate.close``, as the historical replay compares them;
- the digests of the acquisition files and of ``analysis.py`` to match
  exactly, since those are the evidence and its analysis;
- the same set of bound paths.
A collector module whose bytes moved since production is named, and the
retained digest stays the record of the producing collector.

Usage: "$PYTHON" scripts/ascella_order_retry_collector.py [--self-test]
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "results/quandela/runs/ascella-mosaiq-update-order-retry"
sys.path[:0] = [str(RUN), str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import analysis  # noqa: E402
from bdsc_certificate import close  # noqa: E402


def compare(retained: dict[str, Any], fresh: dict[str, Any]) -> list[str]:
    """Raise unless fresh reproduces retained; return the collector modules whose bytes moved since production."""
    analysis.check_report_types(retained, fresh)
    recorded, current = retained["source_sha256"], fresh["source_sha256"]
    inputs = {path for path in current if path.startswith(RUN.relative_to(ROOT).as_posix() + "/")}
    for path in sorted(inputs):
        if recorded[path] != current[path]:
            raise ValueError(f"acquisition or analysis bytes differ from the retained record: {path}")
    close(
        {key: value for key, value in retained.items() if key != "source_sha256"},
        {key: value for key, value in fresh.items() if key != "source_sha256"},
        "Ascella four-output order analysis",
    )
    return sorted(path for path in current.keys() - inputs if recorded[path] != current[path])


def self_test(retained: dict[str, Any], fresh: dict[str, Any]) -> int:
    """Reject each mutation of the retained record that compare must catch; return how many were rejected."""

    def rejects(mutate: Any, fragment: str) -> None:
        mutated = copy.deepcopy(retained)
        mutate(mutated)
        try:
            compare(mutated, fresh)
        except ValueError as error:
            if fragment not in str(error):
                raise ValueError(f"mutation rejected for another reason: {error}") from error
            return
        raise ValueError(f"mutation accepted where {fragment!r} must reject")

    def count(record: dict[str, Any]) -> None:
        record["observations"][0]["counts"][0] += 1

    def probability(record: dict[str, Any]) -> None:
        record["observations"][0]["measured_conditional_probabilities"][0] += 1e-6

    def input_digest(record: dict[str, Any]) -> None:
        record["source_sha256"][f"{RUN.relative_to(ROOT).as_posix()}/results.json"] = "0" * 64

    def extra_path(record: dict[str, Any]) -> None:
        record["source_sha256"]["scripts/absent.py"] = "0" * 64

    def integer_type(record: dict[str, Any]) -> None:
        record["observations"][0]["accepted_samples"] = float(record["observations"][0]["accepted_samples"])

    mutations = (
        (count, "counts"),
        (probability, "measured_conditional_probabilities"),
        (input_digest, "acquisition or analysis bytes differ"),
        (extra_path, "object keys"),
        (integer_type, "value type"),
    )
    for mutate, fragment in mutations:
        rejects(mutate, fragment)
    moved = copy.deepcopy(retained)
    moved["source_sha256"]["gororoba_quantum/parallel.py"] = "0" * 64
    if "gororoba_quantum/parallel.py" not in compare(moved, fresh):
        raise ValueError("a moved collector module is not named")
    return len(mutations)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    retained = json.loads((RUN / "analysis.json").read_text())
    fresh = analysis.analyze(RUN)
    if arguments.self_test:
        rejected = self_test(retained, fresh)
        print(f"{rejected} retained-record mutations rejected; a moved collector module is named")
        return
    moved = compare(retained, fresh)
    print(
        f"Validated {len(fresh['observations'])} Ascella observations under the current collector; "
        f"modules moved since the producing collector: {', '.join(moved) or 'none'}"
    )


if __name__ == "__main__":
    main()
