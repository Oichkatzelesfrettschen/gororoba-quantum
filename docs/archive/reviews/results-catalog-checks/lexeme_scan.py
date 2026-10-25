"""Count JSON number lexemes that an ordinary json.loads/json.dumps round trip changes in value."""
import json, re, subprocess, sys
from decimal import Decimal
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map
NUM = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')
def scan(path):
    lossy = 0; total = 0; ex = None
    def pf(s):
        nonlocal lossy, total, ex
        total += 1
        if Decimal(repr(float(s))) != Decimal(s):
            lossy += 1; ex = ex or s
        return float(s)
    def pi(s):
        nonlocal total
        total += 1
        return int(s)
    try:
        json.loads(open(ROOT / path, encoding="utf-8").read(), parse_float=pf, parse_int=pi)
    except Exception:
        return (path, -1, 0, None)
    return (path, total, lossy, ex)
def main():
    files = subprocess.run(["git", "ls-files", "*.json"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    rows = ordered_map(scan, files)
    tot = sum(r[1] for r in rows if r[1] > 0); bad = [r for r in rows if r[2]]
    print("files", len(files), "unparsed", sum(r[1] < 0 for r in rows), "number lexemes", tot)
    print("lexemes whose value changes under float parse (decimal value != value of repr(float))", sum(r[2] for r in bad), "in", len(bad), "files")
    for r in bad[:15]: print(" ", r[0], r[2], r[3])
if __name__ == "__main__":
    main()
