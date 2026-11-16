"""Exploratory: measured selector contrast minus the exact-pulse forward law at matched center visibility."""

import json

import scan_fits
from scan_forward import HERE, rs

import parallel


def main() -> None:
    # One process per table fills the scratch directory, so the batch workers below load files and build none.
    parallel.ordered_map(rs.table_item, [(kind, scan_fits.EXACT_WORLD, False) for kind in rs.FIT_KINDS], min_items=1)
    names = [b for b, r in scan_fits.analysis()["batch_rows"].items() if r["kind"] != "bridge"]
    out = dict(zip(names, parallel.ordered_map(scan_fits.exact_residual_batch, names, min_items=2), strict=True))
    for batch, line in out.items():
        print(batch, line["kind"], line["arms"])
        print("  measured", line["measured"], "vis", line["visibility"])
        for kind, v in line["exact"].items():
            print(f"  {kind:22s} model {v['model']} residual {v['residual']} z {v['z']}")
    (HERE / "exact_pulse_residuals.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
