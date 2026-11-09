"""Static call graph of fiber_rank_v11.py: every function (incl. nested), line span, callers, callees."""

import ast
import sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)
funcs: dict[
    str, tuple[int, int | None, ast.FunctionDef | ast.AsyncFunctionDef]
] = {}  # qualname -> (lineno, endlineno, node)


def walk(node, prefix=""):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
            q = prefix + ch.name
            funcs[q] = (ch.lineno, ch.end_lineno, ch)
            walk(ch, q + ".")
        elif isinstance(ch, ast.ClassDef):
            walk(ch, prefix + ch.name + ".")
        else:
            walk(ch, prefix)


walk(tree)
short: dict[str, list[str]] = {}
for q in funcs:
    short.setdefault(q.split(".")[-1], []).append(q)

calls: dict[str, set[str]] = {q: set() for q in funcs}
refs: dict[str, set[str]] = {q: set() for q in funcs}
for q, (_lo, _hi, node) in funcs.items():
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                name: str | None = f.id
                ok_kind: str | None = "func"
            elif isinstance(f, ast.Attribute):
                name, ok_kind = f.attr, "method"
            else:
                name, ok_kind = None, None
            if name in short:
                for t in short[name]:
                    is_method = t.split(".")[0] in ("Space", "Echelon")
                    if t != q and (ok_kind == "method") == is_method:
                        calls[q].add(t)
        # function passed as value (e.g. parallel.ordered_map(run_step, ...), functools.partial(...))
        params = {a.arg for a in node.args.args}
        if isinstance(n, ast.Name) and n.id in short and n.id not in params and isinstance(n.ctx, ast.Load):
            for t in short[n.id]:
                if t != q and t not in calls[q]:
                    refs[q].add(t)
# nested function owner: treat as callee of parent if called there (already by walk since ast.walk includes nested defs)
# module-level (main) is a function here.
callers: dict[str, set[str]] = {q: set() for q in funcs}
for q in funcs:
    for t in calls[q] | refs[q]:
        callers[t].add(q)
print(f"{'line':>9}  {'function':<34} callers -> callees (r = passed as value)")
for q, (lo, hi, _) in sorted(funcs.items(), key=lambda kv: kv[1][0]):
    cs = ", ".join(sorted(callers[q])) or "-"
    ce = ", ".join(sorted(calls[q]) + [t + " (r)" for t in sorted(refs[q] - calls[q])]) or "-"
    print(f"{lo:>4}-{hi:<4}  {q:<34} IN: {cs}\n{'':>11}{'':<34} OUT: {ce}")
print(f"\n{len(funcs)} functions")
# module-level statements (not in a function) calling
mod_calls = set()
for n in tree.body:
    if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
        continue
    for m in ast.walk(n):
        if isinstance(m, ast.Call):
            f = m.func
            name = f.id if isinstance(f, ast.Name) else None
            if name in short:
                mod_calls.add(name)
print("module-level calls:", sorted(mod_calls))
