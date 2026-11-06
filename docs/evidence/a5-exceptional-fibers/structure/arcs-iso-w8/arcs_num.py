"""Numeric search for arc families on the Iso -> N- and W8 -> N- slices: exact truncated series over F_p with
first-order dual parts in every parameter.

An arc is given in the split coordinates a = t2 + i t4, b = t2 - i t4, c = t5 + i t6, d = t5 - i t6:
a = s (a1 + a2 s + ...), c, d, t7 and the remaining free coordinates (t3 on Iso; t1, t9 on W8) are series without
constant term, and b = (g + c d - t7^2) / a with g = 0 (Iso) or the t1, t9 part of J (W8). Every coefficient is
either a parameter or a fixed value. The value of a family at a parameter point is the order nu of G(x(s)), the
limit vector F (coefficient of s^nu), the rank of [dF/dtheta | F], and the values of K2 and of the component tests at
F. This search only proposes families; a proposed family is certified symbolically (`certify.sing` scripts), since
a rank at one point of the coefficient of s^nu is a lower bound on the dimension of the limit cone only where the
lower coefficients vanish identically.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/arcs_num.py FIBER PRIME
"""

import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE))
from arcs_scan import FIBERS, ROOTS  # noqa: E402  # type: ignore[import-not-found]

TERM = re.compile(r"([+-]?)(\d*)\*?((?:[A-Za-z]\w*(?:\(\d+\))?(?:\^\d+)?\*?)*)")


def parse(text: str, names: list[str], p: int) -> list[tuple[int, tuple[int, ...]]]:
    """Sparse polynomial: list of (coefficient mod p, exponent tuple over names)."""
    idx = {n: k for k, n in enumerate(names)}
    out: list[tuple[int, tuple[int, ...]]] = []
    text = text.replace(" ", "").replace("\n", "")
    for m in re.finditer(r"[+-]?[^+-]+", text):
        tok = m.group(0)
        sign = -1 if tok.startswith("-") else 1
        tok = tok.lstrip("+-")
        coef = 1
        exps = [0] * len(names)
        for f in tok.split("*"):
            if not f:
                continue
            if f.isdigit():
                coef = coef * int(f) % p
                continue
            base, _, e = f.partition("^")
            if base not in idx:
                raise ValueError(f"unknown factor {base!r}")
            exps[idx[base]] += int(e or 1)
        out.append((sign * coef % p, tuple(exps)))
    return out


def ideal_list(text: str) -> list[str]:
    body = text.strip().rstrip(";")
    return [g for g in body.split(",") if g.strip()]


class Jet:
    """Series truncated at s^N with value row and m derivative rows, entries mod p (shape (m + 1, N + 1))."""

    def __init__(self, arr: np.ndarray, p: int) -> None:
        self.a = arr % p
        self.p = p

    @staticmethod
    def toeplitz(v: np.ndarray) -> np.ndarray:
        n = v.shape[0]
        t = np.zeros((n, n), dtype=np.int64)
        for k in range(n):
            t[k:, k] = v[: n - k]
        return t

    def __mul__(self, o: Jet) -> Jet:
        p = self.p
        ta, tb = self.toeplitz(self.a[0]), self.toeplitz(o.a[0])
        out = np.empty_like(self.a)
        out[0] = (ta @ o.a[0]) % p
        out[1:] = ((o.a[1:] @ ta.T) % p + (self.a[1:] @ tb.T) % p) % p
        return Jet(out, p)

    def __add__(self, o: Jet) -> Jet:
        return Jet(self.a + o.a, self.p)

    def __sub__(self, o: Jet) -> Jet:
        return Jet(self.a - o.a, self.p)

    def scale(self, c: int) -> Jet:
        return Jet(self.a * (c % self.p), self.p)

    def shift_down(self) -> Jet:
        """Divide by s; the s^0 coefficient (value and derivatives) must vanish."""
        if np.any(self.a[:, 0] % self.p):
            raise ValueError("division by s of a series with a constant term")
        out = np.zeros_like(self.a)
        out[:, :-1] = self.a[:, 1:]
        return Jet(out, self.p)

    def inverse(self) -> Jet:
        """1 / x for x with a unit constant term (value row), with the derivative rows -x'/x^2."""
        p, n = self.p, self.a.shape[1]
        v = self.a[0]
        inv = np.zeros(n, dtype=np.int64)
        inv[0] = pow(int(v[0]), p - 2, p)
        for k in range(1, n):
            inv[k] = (-inv[0] * int(sum(int(v[j]) * int(inv[k - j]) for j in range(1, k + 1)))) % p
        ti = self.toeplitz(inv)
        out = np.empty_like(self.a)
        out[0] = inv
        out[1:] = (-(self.a[1:] @ ti.T % p) @ ti.T) % p
        return Jet(out, p)


def evaluate(poly: list[tuple[int, tuple[int, ...]]], xs: list[Jet], p: int) -> Jet:
    m1, n1 = xs[0].a.shape
    one = np.zeros((m1, n1), dtype=np.int64)
    one[0, 0] = 1
    cache: dict[tuple[int, int], Jet] = {}

    def pw(i: int, e: int) -> Jet:
        if (i, e) not in cache:
            cache[(i, e)] = xs[i] if e == 1 else pw(i, e - 1) * xs[i]
        return cache[(i, e)]

    acc = Jet(np.zeros((m1, n1), dtype=np.int64), p)
    for c, ex in poly:
        t = Jet(one.copy(), p)
        for i, e in enumerate(ex):
            if e:
                t = t * pw(i, e)
        acc = acc + t.scale(c)
    return acc


def eval_point(poly: list[tuple[int, tuple[int, ...]]], x: list[int], p: int) -> int:
    tot = 0
    for c, ex in poly:
        v = c
        for i, e in enumerate(ex):
            if e:
                v = v * pow(x[i], e, p) % p
        tot = (tot + v) % p
    return tot


def rank_mod(m: np.ndarray, p: int) -> int:
    a = m.copy() % p
    r = 0
    rows, cols = a.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if a[i, c]), None)
        if piv is None:
            continue
        a[[r, piv]] = a[[piv, r]]
        a[r] = a[r] * pow(int(a[r, c]), p - 2, p) % p
        for i in range(rows):
            if i != r and a[i, c]:
                a[i] = (a[i] - a[i, c] * a[r]) % p
        r += 1
        if r == rows:
            break
    return r


class Slice:
    def __init__(self, fiber: str, p: int) -> None:
        f = FIBERS[fiber]
        self.fiber, self.p, self.i = fiber, p, ROOTS[p]
        hdr = (ROOT / f["header"][p]).read_text()
        self.vars = re.search(r"ring r=\d+,\((.*?)\)", hdr).group(1).split(",")  # type: ignore[union-attr]
        jtxt = re.search(r"ideal J=(.*?);", hdr, re.S).group(1)  # type: ignore[union-attr]
        gtxt = re.search(r"ideal G=(.*?);", hdr, re.S).group(1)  # type: ignore[union-attr]
        self.J = parse(jtxt, self.vars, p)
        self.G = [parse(g, self.vars, p) for g in ideal_list(gtxt)]
        run = [parse(g, self.vars, p) for g in ideal_list((ROOT / f["gens"][p]).read_text())]
        self.eps = []
        for g, h in zip(self.G, run, strict=True):
            sg, sh = sorted(g), sorted(h)
            if sg == sh:
                self.eps.append(1)
            elif sg == sorted(((-c) % p, e) for c, e in h):
                self.eps.append(-1)
            else:
                raise ValueError("run generator is not +-G")
        ynames = [f"y({k})" for k in range(1, len(self.G) + 1)]
        self.K2 = [parse(r, ynames, p) for r in ideal_list((ROOT / f["k2"][p]).read_text())]
        self.tests: dict[str, list[list[tuple[int, tuple[int, ...]]]]] = {}
        r = ROOTS[p]
        if fiber == "w8":
            lam = f"y(22),y(19)+y(21),y(18),y(13)-y(23),y(11)+{r}*y(23),y(8)+y(24),y(4)+y(12)-y(24),y(3),y(2)+{r}*y(24)"
            self.tests["Lam"] = [parse(x, ynames, p) for x in ideal_list(lam)]
            if p == 32009:
                q = (HERE.parent / "w8-kp" / "quotient.txt").read_text()
                self.tests["Q"] = [parse(x, ynames, p) for x in ideal_list(q)]

    def arc(self, coeffs: dict[str, list[int | tuple[str, int]]], params: list[str], vals: list[int], n: int) -> dict:
        """coeffs: coordinate -> list of s^1.. coefficients, each an int or (param name, offset), meaning the
        parameter plus the offset."""
        p = self.p
        m = len(params)
        pidx = {q: k for k, q in enumerate(params)}

        def series(name: str) -> Jet:
            arr = np.zeros((m + 1, n + 1), dtype=np.int64)
            for k, c in enumerate(coeffs.get(name, []), start=1):
                if k > n:
                    break
                if isinstance(c, tuple):
                    j = pidx[c[0]]
                    arr[0, k] = (vals[j] + c[1]) % p
                    arr[1 + j, k] = 1
                else:
                    arr[0, k] = c % p
            return Jet(arr, p)

        a, c, d, t7 = series("a"), series("c"), series("d"), series("t7")
        g = Jet(np.zeros((m + 1, n + 1), dtype=np.int64), p)
        if self.fiber == "w8":
            t1, t9 = series("t1"), series("t9")
            g = (t1 * t1 * t9 * t9) - (t1 * t1 * t9).scale(2) + (t1 * t9 * t9).scale(2) - (t1 * t9).scale(4)
        num = g + c * d - t7 * t7
        oa = next(k for k in range(n + 1) if a.a[0, k])
        a_red = a  # b = (num / s^oa) / (a / s^oa); a / s^oa has a unit constant term
        for _ in range(oa):
            num, a_red = num.shift_down(), a_red.shift_down()
        b = num * a_red.inverse()
        half, inv2i = pow(2, p - 2, p), pow(2 * self.i, p - 2, p)
        t2, t4 = (a + b).scale(half), (a - b).scale(inv2i)
        t5, t6 = (c + d).scale(half), (c - d).scale(inv2i)
        coords = {"t2": t2, "t4": t4, "t5": t5, "t6": t6, "t7": t7}
        if self.fiber == "iso":
            coords["t3"] = series("t3")
        else:
            coords["t1"], coords["t9"] = t1, t9
        xs = [coords[v] for v in self.vars]
        jv = evaluate(self.J, xs, p)
        gs = [evaluate(g_, xs, p) for g_ in self.G]
        nz = [next((k for k in range(n + 1) if gj.a[0, k]), n + 1) for gj in gs]
        nu = min(nz)
        if nu > n:
            return {"nu": None}
        F = np.array([gj.a[0, nu] for gj in gs], dtype=np.int64)
        dF = np.array([gj.a[1:, nu] for gj in gs], dtype=np.int64)  # rows: generators, cols: params
        M = np.concatenate([dF, F[:, None]], axis=1)
        Fr = [(e * int(v)) % p for e, v in zip(self.eps, F, strict=True)]
        res = {
            "nu": nu,
            "J_zero_through": next((k for k in range(n + 1) if jv.a[0, k]), n + 1) - 1,
            "rank": rank_mod(M, p),
            "K2": all(eval_point(r, Fr, p) == 0 for r in self.K2),
            "lower_zero_at_point": all(not np.any(gj.a[0, :nu]) for gj in gs),
            "exact": nu <= n + 1,
        }
        for name, polys in self.tests.items():
            res[name] = all(eval_point(r, Fr, p) == 0 for r in polys)
        return res


def family(kind: str, fiber: str, top: int, o9: int = 2) -> tuple[dict, list[str]]:
    """Families: 'generic' (all coefficients free, a1 = 1) and 'L0' (leading direction in L0)."""
    params: list[str] = []

    def free(name: str, first: int, last: int) -> list[int | tuple[str, int]]:
        out: list[int | tuple[str, int]] = [0] * (first - 1)
        for k in range(first, last + 1):
            q = f"{name}{k}"
            params.append(q)
            out.append((q, 0))
        return out

    co: dict[str, list[int | tuple[str, int]]] = {}
    other = ["t3"] if fiber == "iso" else ["t1"]
    if kind == "generic":
        co["a"] = [1, *free("a", 2, top)[1:]] if top >= 2 else [1]
        for x in ["c", "d", "t7", *other]:
            co[x] = free(x, 1, top)
        if fiber == "w8":
            co["t9"] = free("t9", 1, top)
    else:  # L0: a1 = 1, b1 = -1, c1 = T + 1, d1 = T - 1 with T = t7_1
        params.append("T1")
        co["a"] = [1, *free("a", 2, top)[1:]]
        co["t7"] = [("T1", 0), *free("t7", 2, top)[1:]]
        co["c"] = [("T1", 1), *free("c", 2, top)[1:]]
        co["d"] = [("T1", -1), *free("d", 2, top)[1:]]
        for x in other:
            co[x] = free(x, 1, top)
        if fiber == "w8":
            co["t9"] = free("t9", o9, top + 1)
    return co, params


def weighted(fiber: str, w: dict[str, int], extra: int) -> tuple[dict, list[str]]:
    """Each coordinate starts at s^w[x] with a free leading coefficient (a: leading coefficient 1) and carries free
    coefficients through s^(w[x] + extra)."""
    params: list[str] = []
    co: dict[str, list[int | tuple[str, int]]] = {}
    for x, wx in w.items():
        lst: list[int | tuple[str, int]] = [0] * (wx - 1)
        for k in range(wx, wx + extra + 1):
            if x == "a" and k == wx:
                lst.append(1)
                continue
            q = f"{x}_{k}"
            params.append(q)
            lst.append((q, 0))
        co[x] = lst
    return co, params


class WeightedFamily:
    """One weighted family's evaluation, picklable for parallel.ordered_map; each worker builds its Slice once."""

    def __init__(self, fiber: str, p: int, extra: int, n: int) -> None:
        self.fiber, self.p, self.extra, self.n = fiber, p, extra, n
        self._slice: Slice | None = None

    def __getstate__(self) -> dict:
        return {"fiber": self.fiber, "p": self.p, "extra": self.extra, "n": self.n, "_slice": None}

    def __call__(self, w: dict[str, int]) -> dict | None:
        if self._slice is None:
            self._slice = Slice(self.fiber, self.p)
        co, params = weighted(self.fiber, w, self.extra)
        vals = [(97 * k + 31) % self.p + 2 for k in range(len(params))]
        try:
            r = self._slice.arc(co, params, vals, self.n)
        except ValueError:
            return None
        if r.get("nu") is None or not r["exact"] or r["J_zero_through"] < self.n:
            return None
        return r


def search(fiber: str, p: int, extra: int = 2, n: int = 16) -> None:
    import itertools

    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    names = ["a", "c", "d", "t7"] + (["t3"] if fiber == "iso" else ["t1", "t9"])
    families = []
    for ws in itertools.product(range(1, 5), repeat=len(names)):
        w = dict(zip(names, ws, strict=True))
        orders = [w["c"] + w["d"], 2 * w["t7"]] + ([w["t1"] + w["t9"]] if fiber == "w8" else [])
        if min(orders) > w["a"]:
            families.append(w)
    results = parallel.ordered_map(WeightedFamily(fiber, p, extra, n), families)
    best: dict[tuple, int] = {}
    for w, r in zip(families, results, strict=True):
        if r is None:
            continue
        key = (r["rank"], r["K2"], r.get("Lam"), r.get("Q"))
        best[key] = best.get(key, 0) + 1
        done = sum(best.values())
        if done % 500 == 0:
            print("progress", done, "valid families; tallies", dict(sorted(best.items(), reverse=True)), flush=True)
        if r["rank"] >= (5 if fiber == "iso" else 6):
            print("HIT", w, r, flush=True)
    for key in sorted(best, reverse=True):
        print("rank, K2, Lam, Q =", key, "families", best[key])


def l0_puiseux(fiber: str, k: int, extra: int, o9: int | None = None) -> tuple[dict, list[str]]:
    """Leading direction in L0 at order k (a_k = 1, b_k = -1, c_k = T + 1, d_k = T - 1, t7_k = T; t3 or t1 free at
    order k), free coefficients from order k + 1 through k + extra; t9 on W8 starts at order o9 (default 2k)."""
    params: list[str] = ["T"]
    co: dict[str, list[int | tuple[str, int]]] = {}
    lead: dict[str, int | tuple[str, int]] = {"a": 1, "c": ("T", 1), "d": ("T", -1), "t7": ("T", 0)}
    other = "t3" if fiber == "iso" else "t1"
    for x in ["a", "c", "d", "t7", other]:
        lst: list[int | tuple[str, int]] = [0] * (k - 1)
        if x in lead:
            lst.append(lead[x])
        else:
            params.append(f"{x}_{k}")
            lst.append((f"{x}_{k}", 0))
        for j in range(k + 1, k + extra + 1):
            params.append(f"{x}_{j}")
            lst.append((f"{x}_{j}", 0))
        co[x] = lst
    if fiber == "w8":
        start = o9 or 2 * k
        lst = [0] * (start - 1)
        for j in range(start, start + extra + 1):
            params.append(f"t9_{j}")
            lst.append((f"t9_{j}", 0))
        co["t9"] = lst
    return co, params


def l0_t4zero(fiber: str, oa: int, extra: int, o9: int = 2) -> tuple[dict, list[str]]:
    """Leading direction in L0 with t4 = t6 = 0: c1 = d1 = t7_1 = T, a of order oa >= 2 (leading coefficient 1),
    free coefficients above the leading ones through order 1 + extra (a through oa + extra)."""
    params: list[str] = ["T"]
    co: dict[str, list[int | tuple[str, int]]] = {}
    co["a"] = [*([0] * (oa - 1)), 1]
    for j in range(oa + 1, oa + extra + 1):
        params.append(f"a_{j}")
        co["a"].append((f"a_{j}", 0))
    other = "t3" if fiber == "iso" else "t1"
    for x in ["c", "d", "t7", other]:
        lst: list[int | tuple[str, int]] = [("T", 0)] if x != other else []
        if x == other:
            params.append(f"{x}_1")
            lst.append((f"{x}_1", 0))
        for j in range(2, 2 + extra):
            params.append(f"{x}_{j}")
            lst.append((f"{x}_{j}", 0))
        co[x] = lst
    if fiber == "w8":
        lst = [0] * (o9 - 1)
        for j in range(o9, o9 + extra + 1):
            params.append(f"t9_{j}")
            lst.append((f"t9_{j}", 0))
        co["t9"] = lst
    return co, params


def adapted_arc(sl: Slice, k: int, extra: int, k9: int, point_shift: int = 0, n: int = 24) -> dict:
    """Arcs tangent to L0 with normal contact k: t3 or t1, t4, t5 of order 1 (free series through order 1 + extra);
    w1 = t2 and w3 = t5 - t7 (and t9 on W8, from order k9) of order k with free coefficients through k + extra;
    w2 = t4 - t6 solved from J by fixed-point iteration, w2 = (rest) / (2 t4) with rest of order >= k + 1."""
    p = sl.p
    params: list[str] = []

    def free_series(name: str, first: int, last: int) -> list[tuple[str, int]]:
        out = []
        for j in range(first, last + 1):
            params.append(f"{name}_{j}")
            out.append((f"{name}_{j}", j))
        return out

    other = "t3" if sl.fiber == "iso" else "t1"
    spec = {
        other: free_series(other, 1, 1 + extra),
        "t4": free_series("t4", 1, 1 + extra),
        "t5": free_series("t5", 1, 1 + extra),
        "w1": free_series("w1", k, k + extra),
        "w3": free_series("w3", k, k + extra),
    }
    if sl.fiber == "w8":
        spec["t9"] = free_series("t9", k9, k9 + extra)
    m = len(params)
    vals = [(97 * j + 31 + point_shift) % p + 2 for j in range(m)]
    pidx = {q: j for j, q in enumerate(params)}

    def jet(name: str) -> Jet:
        arr = np.zeros((m + 1, n + 1), dtype=np.int64)
        for q, e in spec[name]:
            if e <= n:
                arr[0, e] = vals[pidx[q]] % p
                arr[1 + pidx[q], e] = 1
        return Jet(arr, p)

    t4, t5, w1, w3, o = jet("t4"), jet("t5"), jet("w1"), jet("w3"), jet(other)
    g = Jet(np.zeros((m + 1, n + 1), dtype=np.int64), p)
    if sl.fiber == "w8":
        t1, t9 = o, jet("t9")
        g = (t1 * t1 * t9 * t9) - (t1 * t1 * t9).scale(2) + (t1 * t9 * t9).scale(2) - (t1 * t9).scale(4)
    # Iso: J = w1^2 + w2 (2 t4 - w2) - w3 (2 t5 - w3); W8: J = g - [that]. Solve 2 t4 w2 = rhs + w2^2.
    sign = 1 if sl.fiber == "w8" else -1  # W8: 2 t4 w2 = g - w1^2 + w3(2 t5 - w3) + w2^2 ; Iso: g = 0
    base = w3 * (t5.scale(2) - w3) - w1 * w1 + (g if sign == 1 else g.scale(0))
    inv_t4 = t4.shift_down().inverse()
    half = pow(2, p - 2, p)
    w2 = Jet(np.zeros_like(base.a), p)
    for _ in range(n + 2):
        w2 = ((base + w2 * w2).shift_down() * inv_t4).scale(half)
    t2, t6, t7 = w1, t4 - w2, t5 - w3
    coords = {"t2": t2, "t4": t4, "t5": t5, "t6": t6, "t7": t7, other: o}
    if sl.fiber == "w8":
        coords["t9"] = jet("t9")
    xs = [coords[v] for v in sl.vars]
    jv = evaluate(sl.J, xs, p)
    gs = [evaluate(g_, xs, p) for g_ in sl.G]
    nu = min(next((j for j in range(n + 1) if gj.a[0, j]), n + 1) for gj in gs)
    if nu > n - 2:
        return {"nu": None}
    F = np.array([gj.a[0, nu] for gj in gs], dtype=np.int64)
    dF = np.array([gj.a[1:, nu] for gj in gs], dtype=np.int64)
    Fr = [(e * int(v)) % p for e, v in zip(sl.eps, F, strict=True)]
    res = {
        "params": m,
        "nu": nu,
        "J_zero_through": next((j for j in range(n + 1) if jv.a[0, j]), n + 1) - 1,
        "rank": rank_mod(np.concatenate([dF, F[:, None]], axis=1), p),
        "K2": all(eval_point(r, Fr, p) == 0 for r in sl.K2),
    }
    for name, polys in sl.tests.items():
        res[name] = all(eval_point(r, Fr, p) == 0 for r in polys)
    return res


def valid(r: dict, n: int) -> bool:
    """An arc counts when it passes through the origin (nu >= 1), J vanishes on it through the truncation order, and
    its limit is exact."""
    return r.get("nu") not in (None, 0) and r.get("J_zero_through", -1) >= n - 2 and r.get("exact", True)


class ModeCase:
    """One explicit-family or adapted-arc evaluation, picklable for parallel.ordered_map; each worker builds its Slice
    once. A case is ("arc", co, params, n, catch) or ("adapted", k, extra, k9, n)."""

    def __init__(self, fiber: str, p: int) -> None:
        self.fiber, self.p = fiber, p
        self._slice: Slice | None = None

    def __getstate__(self) -> dict:
        return {"fiber": self.fiber, "p": self.p, "_slice": None}

    def __call__(self, case: tuple) -> dict:
        if self._slice is None:
            self._slice = Slice(self.fiber, self.p)
        if case[0] == "adapted":
            _, k, extra, k9, n = case
            return adapted_arc(self._slice, k, extra, k9, n=n)
        _, co, params, n, catch = case
        vals = [(97 * j + 31) % self.p + 2 for j in range(len(params))]
        try:
            return self._slice.arc(co, params, vals, n)
        except ValueError:
            if catch:
                return {"nu": None}
            raise


def cli() -> None:
    import argparse

    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fiber", choices=sorted(FIBERS))
    ap.add_argument("prime", type=int, choices=sorted(ROOTS))
    ap.add_argument("mode", choices=["basic", "weighted", "puiseux", "t4zero", "adapted"])
    a = ap.parse_args()
    if a.mode == "weighted":
        search(a.fiber, a.prime)
        return
    # every family is specified first; the independent evaluations are then mapped in parallel
    cases: list[tuple[str, tuple, int]] = []
    if a.mode == "basic":
        for kind in ("generic", "L0"):
            for top in (1, 2, 3, 4):
                if kind == "L0" and top < 2:
                    continue
                for o9 in (2, 3) if (a.fiber == "w8" and kind == "L0") else (2,):
                    co, params = family(kind, a.fiber, top, o9)
                    cases.append((f"{kind} top {top} t9 order {o9}", ("arc", co, params, 14, False), 14))
    elif a.mode in ("puiseux", "t4zero"):
        for k in (2, 3, 4):
            for extra in (1, 2, 3):
                for o9 in [2] if a.fiber == "iso" else [k + 1, 2 * k, 2 * k + 1]:
                    if a.mode == "puiseux":
                        if k == 4:
                            continue
                        co, params = l0_puiseux(a.fiber, k, extra, o9)
                    else:
                        co, params = l0_t4zero(a.fiber, k, extra, o9)
                    cases.append((f"{a.mode} order {k} extra {extra} t9 {o9}", ("arc", co, params, 20, True), 20))
    else:
        for k in (2, 3, 4):
            for k9 in [1] if a.fiber == "iso" else [2, k, k + 1, 2 * k]:
                for extra in (1, 2, 3):
                    cases.append((f"adapted contact {k} t9 from {k9} extra {extra}", ("adapted", k, extra, k9, 24), 24))
    results = parallel.ordered_map(ModeCase(a.fiber, a.prime), [c for _, c, _ in cases], min_items=2)
    bad = 0
    for (tag, _, n), r in zip(cases, results, strict=True):
        if valid(r, n):
            print(tag, r, flush=True)
        else:
            bad += 1
    print("invalid arcs dropped (not through the origin, J not vanishing, or inexact):", bad)


if __name__ == "__main__":
    cli()
