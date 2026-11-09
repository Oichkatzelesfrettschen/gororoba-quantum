"""Degree-6, N = 19 extrapolation arithmetic for README.md beside this file.

All inputs are the measured terms named inline.
"""

GiB = 2**30
D = 235543
Sc2 = 221923217296 / 16  # sum of cols_b^2, from the probe preflight echelon term (w8nm_d6_n19_p32009.err)
c = D / 4
L = 110961608648  # generator_blocks term of the same preflight, bytes (formula verified byte-exact at d=3, d=4)
print("sum c^2 (1e9)", Sc2 / 1e9, "rms c", (Sc2 / 4) ** 0.5)
print("L GiB", L / GiB, "walk 10% GiB", 0.1 * L / GiB)
print("rows*widest (1e6)", 14953585152 / 16 / 1e6)
for rho in (0.62, 0.645, 0.657, 0.67, 0.75, 1.0):
    B = rho * Sc2 * 8 / 4
    print(
        f"rho {rho}: B_b {B / GiB:.1f} GiB, sum B {4 * B / GiB:.1f} GiB, "
        f"closure 7 B_b {7 * B / GiB:.1f} GiB, 4 B_b {4 * B / GiB:.1f}"
    )
print("Q GiB", 8624 * c * 8 / GiB)
print(
    "marshal (121 B/entry) chunk 4000 free c:",
    4000 * c * 121 / GiB,
    " free 19.6k:",
    4000 * 19600 * 121 / GiB,
    " chunk 500 free c:",
    500 * c * 121 / GiB,
)
r = D / 30940
print("D ratio vs d=4", r, r**2, r**3)
print(
    "closure from d=4 split: blas h",
    113.5 * r**3 / 3600,
    " r^2 part h",
    146 * r**2 / 3600,
    " rref h",
    23.4 * r**3 / 3600,
)
r6 = D / 93024
print("vs d=5: ", r6, r6**2, r6**3, "closure h", 4751 * (0.4 * r6**3 + 0.6 * r6**2) / 3600)
print(
    "products from d=5 2201 s: x",
    r6**2,
    "(L)",
    "to",
    2.1 * r6**2,
    "(matmul) ->",
    2201 * r6**2 / 3600,
    2201 * 2.1 * r6**2 / 3600,
    "h",
)
