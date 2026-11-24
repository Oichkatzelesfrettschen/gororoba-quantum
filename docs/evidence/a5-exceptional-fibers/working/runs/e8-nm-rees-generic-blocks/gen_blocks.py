"""Write the y-degree-1 block script of the Rees ideal of E8-bar at N- for one prime and one value of s2.

Arguments: PRIME ROOT VALUE STAGE_A_LOG, VALUE an integer or the word generic (s2 a transcendental parameter z).
Text generation only.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P, ROOT, VALUE = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
log = Path(sys.argv[4]).read_text().splitlines()
J = [line[5:].strip() for line in log if line.startswith("JGEN ")]
G = [line[5:].strip() for line in log if line.startswith("GGEN ")]
if len(G) != 21:
    raise RuntimeError(f"{len(G)} generators G, expected 21")
GB = {}
for line in log:
    m = re.match(r"RESULT Gbideg (\d+) = (\d+),(\d+)", line)
    if m:
        GB[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
generic = VALUE == "generic"
field = f"({P},z)" if generic else str(P)
zval = "z" if generic else str(int(VALUE) % P)
out = (
    (HERE / "deg1.tmpl")
    .read_text()
    .replace("@FIELD@", field)
    .replace("@P@", str(P))
    .replace("@JTEXT@", ",\n".join(J))
    .replace("@GTEXT@", ",\n".join(G))
    .replace("@ZVAL@", zval)
    .replace("@ZIDX@", "0")
    .replace("@GW@", ",".join(str(GB[k][0]) for k in range(1, 22)))
    .replace("@GV@", ",".join(str(GB[k][1]) for k in range(1, 22)))
    .replace("@CI8@", str(ROOT * pow(8, -1, P) % P))
    .replace("@IVAL@", str(ROOT))
    .replace("@W@", "14")
    .replace("@V@", "8")
    .replace("@MODE@", "1")
)
print(out)
