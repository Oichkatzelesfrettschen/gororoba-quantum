"""Hilbert-Samuel data of the local rings k[t]/J at the origin, read from the standard-monomial tables of the exports.

Usage: hilbert_samuel.py EXPORTS_AUDIT_TSV OUT_TSV

exports-audit.tsv (written by exports_audit.py) holds, per export, the number of standard monomials of
std(J + m^N) by degree. The standard monomials of the truncated quotient k[t]/(J + m^N) form a basis whose count is
the length l(N) of the quotient, and the count at degree d below N is the Hilbert function of the initial ideal of
J in the graded reverse lexicographic order. For a local ring of dimension D and multiplicity e the length is a
polynomial of degree D in N for large N, so the D-th finite difference of l(N) at consecutive N is the constant e.
The script reports, for each family and prime, the lengths at the consecutive N that the exports hold, their
successive finite differences, and the degree-wise Hilbert function differences.
"""

import json
import sys
from collections import defaultdict


def differences(values: list[int]) -> list[list[int]]:
    rows = [values]
    while len(rows[-1]) > 1:
        rows.append([b - a for a, b in zip(rows[-1], rows[-1][1:], strict=False)])
    return rows


def main() -> int:
    source, out = sys.argv[1], sys.argv[2]
    lengths: dict[tuple[str, str], dict[int, int]] = defaultdict(dict)
    histograms: dict[tuple[str, str], dict[int, dict[int, int]]] = defaultdict(dict)
    with open(source, encoding="ascii") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for line in handle:
            row = dict(zip(header, line.rstrip("\n").split("\t"), strict=False))
            if not row["qb_monomials"] or row["directory"].endswith(".dead-reboot"):
                continue
            key = (row["family"].replace("xm-nm", "xmnm"), row["prime"])
            order = int(row["order"])
            lengths[key][order] = int(row["qb_monomials"])
            histograms[key][order] = {int(d): c for d, c in json.loads(row["qb_degree_histogram"]).items()}
    with open(out, "w", encoding="ascii") as handle:
        handle.write("family\tprime\tkind\tstart_N\tvalues\n")
        for key in sorted(lengths):
            orders = sorted(lengths[key])
            runs: list[list[int]] = [[]]
            for order in orders:
                if runs[-1] and order != runs[-1][-1] + 1:
                    runs.append([])
                runs[-1].append(order)
            for run in runs:
                if len(run) < 2:
                    continue
                values = [lengths[key][n] for n in run]
                for level, row_values in enumerate(differences(values)):
                    handle.write(
                        f"{key[0]}\t{key[1]}\tdiff{level}_of_length\t{run[0]}\t{','.join(str(v) for v in row_values)}\n"
                    )
            top = max(orders)
            hist = histograms[key][top]
            degrees = [d for d in sorted(hist) if d < top - 1]
            values = [hist[d] for d in degrees]
            for level, row_values in enumerate(differences(values)):
                handle.write(
                    f"{key[0]}\t{key[1]}\tdiff{level}_of_hf_N{top}\t0\t{','.join(str(v) for v in row_values)}\n"
                )
    with open(out.replace(".tsv", "-relations.tsv"), "w", encoding="ascii") as handle:
        handle.write("prime\trelation\tstatus\tdetail\n")
        for prime in sorted({k[1] for k in lengths}):
            vb = lengths.get(("e8-vb", prime), {})
            x = lengths.get(("xmnm", prime), {})
            common = sorted(set(vb) & set(x))
            same = bool(common) and all(vb[n] == x[n] for n in common)
            detail = ",".join(f"{n}:{vb[n]}/{x[n]}" for n in common)
            handle.write(
                f"{prime}\tquotient length of E8-bar -> VB against X-\t{'equal' if same else 'differs'}\t{detail}\n"
            )
            hv, hx, he = (
                histograms.get(("e8-vb", prime)),
                histograms.get(("xmnm", prime)),
                histograms.get(("e8nm", prime)),
            )
            if hv and hx:
                a, b = hv[max(hv)], hx[max(hx)]
                ok = all(a[d] == b[d] + b[d - 1] for d in range(1, 8))
                verdict, counts = ("holds" if ok else "fails"), [a[d] for d in range(8)]
                handle.write(f"{prime}\tVB(d) = X(d) + X(d-1) for d = 1 to 7\t{verdict}\t{counts}\n")
            if hv and he:
                a, b = hv[max(hv)], he[max(he)]
                ok = all(a[d] == b[d] - b[d - 1] for d in range(1, 8))
                verdict, counts = ("holds" if ok else "fails"), [a[d] for d in range(8)]
                handle.write(f"{prime}\tVB(d) = E8(d) - E8(d-1) for d = 1 to 7\t{verdict}\t{counts}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
