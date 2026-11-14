"""Score the float64 producer's own records (producer_record.py) against the 256-bit arb reference of fp_backends.py.

Each record's 32 rates, F, F', process fidelity, F_sd and percentiles enter fp_backends.compare under the keys the
backends use, so the precision score is the same measure the backend table reports.

usage: python score_producer.py INPUTS.npz OUT.json RECORD.json...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import fp_backends as fp


def as_result(record: dict, d: dict) -> dict:
    """The producer record in fp_backends' result layout: rates in the inputs' name order, then the scored keys."""
    prediction = record["tomography_prediction"]
    rates = []
    for name in d["names"]:
        setting, outcome = str(name)[:-3], int(str(name)[-2])
        rates.append(prediction["rates"][setting][outcome])
    result: dict = {"rates": rates, "process_fidelity": prediction["process_fidelity"]}
    for table in (str(t) for t in d["tables"]):
        entry = prediction[table]
        low, high = entry["F_percentile_95"]
        result.update(
            {
                f"{table}/F": entry["F"],
                f"{table}/F_prime": entry["F_prime"],
                f"{table}/F_sd": entry["F_sd"],
                f"{table}/p2.5": low,
                f"{table}/p97.5": high,
            }
        )
    return result


def main() -> int:
    d = fp.load(sys.argv[1])
    reference = fp.arb_reference(d)
    report: dict[str, Any] = {"reference": f"arb {fp.PREC}-bit normal equations", "records": {}}
    for path in sys.argv[3:]:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
        scored = fp.compare(as_result(record, d), reference)
        report["records"][Path(path).name] = {
            "commit": record["commit"],
            "openblas_threads": record["openblas_threads"],
            **scored,
        }
        print(Path(path).name, scored["bits_correct_on_scores"], scored["max_rate_abs_error"], flush=True)
    Path(sys.argv[2]).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
