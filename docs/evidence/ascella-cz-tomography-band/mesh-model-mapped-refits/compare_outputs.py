"""Field-by-field comparison of two mesh_model.py outputs.

Usage: compare_outputs.py A.json B.json

Walks both JSON documents together and reports every numeric leaf that differs, with the absolute and relative
difference, the count of leaves that match bit for bit, and the largest relative difference.
"""

import json
import sys


def leaves(node: object, path: str = ""):
    if isinstance(node, dict):
        for key in sorted(node):
            yield from leaves(node[key], f"{path}/{key}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from leaves(item, f"{path}/{index}")
    else:
        yield path, node


def main() -> int:
    with open(sys.argv[1], encoding="utf-8") as handle:
        first = dict(leaves(json.load(handle)))
    with open(sys.argv[2], encoding="utf-8") as handle:
        second = dict(leaves(json.load(handle)))
    if first.keys() != second.keys():
        print("key sets differ")
        return 1
    equal = 0
    worst = 0.0
    for path in sorted(first):
        a, b = first[path], second[path]
        if a == b:
            equal += 1
            continue
        if not isinstance(a, float) or not isinstance(b, float):
            print(f"{path}\tnon-numeric difference\t{a!r}\t{b!r}")
            continue
        relative = abs(a - b) / max(abs(a), abs(b))
        worst = max(worst, relative)
        print(f"{path}\t{a!r}\t{b!r}\tabs {abs(a - b):.3e}\trel {relative:.3e}")
    print(f"leaves {len(first)} identical {equal} differing {len(first) - equal} max relative difference {worst:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
