"""Rebuild the prediction record on this host and list every path where it differs from the checked-in file."""

import json
import sys

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402


def walk(a, b, path):
    if type(a) is not type(b):
        print(path, "type", type(a).__name__, type(b).__name__)
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                print(path + "/" + str(k), "missing in", "old" if k not in a else "new")
            else:
                walk(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list):
        if len(a) != len(b):
            print(path, "length", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            walk(x, y, f"{path}[{i}]")
    elif a != b:
        print(path, repr(a)[:200], "->", repr(b)[:200])


def main():
    ps.build_tables()
    new = json.loads(json.dumps(ps.predictions(), sort_keys=True))
    old = json.load(open("results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/prediction.json"))
    json.dump(new, open("docs/local/wsl/prediction_wsl.json", "w"), indent=1, sort_keys=True)
    walk(old, new, "")
    print("diff-done")


if __name__ == "__main__":
    main()
