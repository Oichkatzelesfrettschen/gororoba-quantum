"""Block widths cols_b of the standard monomials in a retained qB.txt, by the engine's own character rule."""
import importlib.util, json, os, sys
import numpy as np
spec = importlib.util.spec_from_file_location("fiber_rank_v11", os.environ["FIBER_ENGINE"])
E = importlib.util.module_from_spec(spec); sys.modules["fiber_rank_v11"] = E; spec.loader.exec_module(E)
p, names, j_txt, g_txt = E.parse_header(os.environ["HEADER"])
n = len(names)
J = [E.parse_poly(s, names, p) for s in j_txt]; G = [E.parse_poly(s, names, p) for s in g_txt]
gens = E.independent_generators(E.sign_group([J, G], n, p), n)
basis = [next(iter(q)) for q in E.read_list(sys.argv[1], names, p)]
exps = np.array(basis, dtype=np.int64)
chars = np.stack([(exps @ g) % 2 for g in gens], axis=1) @ np.array([2**i for i in range(len(gens))])
print(json.dumps({"D": len(basis), "cols": np.bincount(chars, minlength=4).tolist(),
                  "degree_levels": np.bincount(exps.sum(axis=1)).tolist()}))
