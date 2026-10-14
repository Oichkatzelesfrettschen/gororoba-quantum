import json
O = OctonionAlgebra(QQ)
B = list(O.basis())
def coords(x):
    v = x.vector()
    return [int(c) for c in v]
tbl = [[coords(B[i]*B[j]) for j in range(8)] for i in range(8)]
print(json.dumps({"sage": version(), "algebra": str(O), "basis": [str(b) for b in B], "table": tbl}))
