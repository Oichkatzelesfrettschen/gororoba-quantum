"""Differential qualification of external hypercomplex packages against cd_core.

Two modes:

- --extract ARCHIVES (local only) first binds each installed distribution
  to its pinned release: the archive in ARCHIVES whose sha256 matches the
  pin, the installed version for PyPI releases, and byte identity between
  every installed .py file and a member of that archive (a declared
  packaging shim is the only exception). It then imports each package,
  reads its basis multiplication table and writes
  docs/evidence/algebra_packages/tables.json: sign and product-index tables
  at dimensions 8 and 16, the declared relation to cd_core, and seeded
  product samples (hypercomplex at 32 and 64, both hypercomplex-engine
  evaluators from 32 to 4096) retained as sign strings.
- --check (CI) imports no external package. It recomputes cd_core signs,
  regenerates every sampled pair from its seed string, and verifies every
  declared relation against the retained tables:
  "identical" (same sign and index table), "signed relabeling" (an index map
  pi and sign flips eta carrying e_p e_q = s'(p, q) e_r onto cd_core), and
  "split" (same index table and associator signs as cd_core, half the
  imaginary units squaring to +1; such a table shares every basis associator
  with the ordinary algebra and is not isomorphic to it).

Each package is bound to its public release by the sha256 of its PyPI sdist
or GitHub archive; docs/notes/packages/ holds one note per package.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import itertools
import json
import random
import sys
import tarfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402

EVIDENCE = ROOT / "docs/evidence/algebra_packages/tables.json"
PYPI = "https://pypi.org/project/"
GITHUB = "https://github.com/"
RELEASES: dict[str, tuple[str, str, str]] = {
    "hypercomplex": (
        "0.3.4",
        PYPI + "hypercomplex/0.3.4/",
        "04241e5d01b3f10e813c70882a2caa9b7dc168f8b921d47156c3d964363f9352",
    ),
    "hypercomplex-engine": (
        "0.5.0",
        PYPI + "hypercomplex-engine/0.5.0/",
        "05634d7421e1b6bc427bbc9cb8b0b91599c46cf1b1321e1d0f3e2f259dc08cb7",
    ),
    "hypercomplex-algebra": (
        "0.2.0.2",
        PYPI + "hypercomplex-algebra/0.2.0.2/",
        "aa043b53a00409c4c1a6c83ecdfae188a20358aaddae587d489de46bff22f52a",
    ),
    "Cayley-Calculator": (
        "1.3.1",
        PYPI + "Cayley-Calculator/1.3.1/",
        "65922fc90cc0d8159830e5d90424cb7cda6c6306824bea628542c647f364d55b",
    ),
    "cayley-dickson": (
        "commit abf96e707e2a",
        GITHUB + "thoppe/Cayley-Dickson/archive/abf96e707e2af10c0f66480ebb00205d3d159e54.tar.gz",
        "446b43f2c955c563f79660045a728b1c96d7c3ee4f7fbc0ae1ae109e90465164",
    ),
    "octonion": (
        "0.1.0",
        PYPI + "octonion/0.1.0/",
        "01788b55497dd6be79411aa03ba17762211e73dafbd014b5f54e66934c98bfcc",
    ),
    "splitoct": (
        "commit e29e72f805c2",
        GITHUB + "EQUINOX24/SplitOct/archive/e29e72f805c2b2e15d904e2dc4d0955e02418390.tar.gz",
        "a192a1d5d9734b31670092be16c19a40b12a79db51ea2cfdfcb1e8a90a6505d6",
    ),
    "mathdunders": (
        "0.4.2",
        PYPI + "mathdunders/0.4.2/",
        "ff9b624725fafd34c51decbe3e661eb91b79bbd3841ab04d2256704df0845ce5",
    ),
}
# Installed files absent from the release archive, added by the local build
# recipe: name -> {installed path: sha256}.
PACKAGING_SHIMS = {
    "cayley-dickson": {
        "cayley_dickson/__init__.py": hashlib.sha256(b"from .cayley_dickson import *\n").hexdigest(),
    },
}
SAMPLED = {"hypercomplex": ((32, 64), 400), "hypercomplex-engine": (tuple(2**n for n in range(5, 13)), 3000)}
TORCH_TO_CD_PI = [0, 1, 2, 4, 3, 6, 7, 5]
TORCH_TO_CD_ETA = [0, 0, 0, 0, 0, 0, 1, 0]

Table = dict[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def unit_table(dim: int, mul: Callable[[int, int], Sequence[Any]]) -> Table:
    """Read e_i e_j from a coefficient-returning product; every product must be a signed basis unit."""
    signs, index = [], []
    for i in range(dim):
        srow, irow = [], []
        for j in range(dim):
            coeffs = [float(c) for c in mul(i, j)]
            nonzero = [k for k, c in enumerate(coeffs) if abs(c) > 1e-12]
            require(len(nonzero) == 1 and abs(abs(coeffs[nonzero[0]]) - 1) < 1e-12, f"e{i} e{j} is not a signed unit")
            srow.append(1 if coeffs[nonzero[0]] > 0 else -1)
            irow.append(nonzero[0])
        signs.append(srow)
        index.append(irow)
    return {"signs": signs, "index": index}


def int_table(signs: Any, index: Any) -> Table:
    return {"signs": [[int(x) for x in row] for row in signs], "index": [[int(x) for x in row] for row in index]}


def sample_pairs(name: str, dim: int, count: int) -> list[tuple[int, int]]:
    rng = random.Random(f"{name}:{dim}")
    return [(rng.randrange(dim), rng.randrange(dim)) for _ in range(count)]


def sign_string(dim: int, pairs: list[tuple[int, int]], mul: Callable[[int, int], tuple[int, int]]) -> str:
    """'+' or '-' per sampled product e_a e_b = sign e_index; 'x' when the index is not a xor b."""
    out = []
    for a, b in pairs:
        sign, index = mul(a, b)
        out.append("x" if index != a ^ b else "+" if sign > 0 else "-")
    return "".join(out)


def bind_installation(name: str, archives: Path) -> dict[str, Any]:
    """Tie the installed distribution to its pinned release archive by digest and file bytes."""
    version, _, sha = RELEASES[name]
    matches = [path for path in sorted(archives.iterdir()) if hashlib.sha256(path.read_bytes()).hexdigest() == sha]
    require(len(matches) == 1, f"{name}: no archive in the archive directory matches the pinned sha256")
    with tarfile.open(matches[0]) as archive:
        members = set()
        for member in archive.getmembers():
            handle = archive.extractfile(member) if member.isfile() else None
            if handle is not None:
                members.add(hashlib.sha256(handle.read()).hexdigest())
    dist = importlib.metadata.distribution(name)
    if not version.startswith("commit "):
        require(dist.version == version, f"{name}: installed version {dist.version} differs from {version}")
    shims = PACKAGING_SHIMS.get(name, {})
    modules = [f for f in dist.files or [] if str(f).endswith(".py")]
    identical = 0
    for file in modules:
        digest = hashlib.sha256(Path(str(file.locate())).read_bytes()).hexdigest()
        if digest in members:
            identical += 1
        else:
            require(shims.get(str(file)) == digest, f"{name}: installed {file} matches no release member")
    require(identical + len(shims) == len(modules), f"{name}: declared packaging shims are not installed")
    return {
        "distribution_version": dist.version,
        "module_files": len(modules),
        "byte_identical_to_release": identical,
        "packaging_shims": shims,
    }


def extract(archives: Path) -> dict[str, Any]:
    packages: dict[str, Any] = {
        name: {"version": version, "release": url, "release_sha256": sha, "tables": {}}
        for name, (version, url, sha) in RELEASES.items()
    }
    for name in RELEASES:
        packages[name]["installed"] = bind_installation(name, archives)
    import cayley_dickson
    import hypercomplex
    import hypercomplex_algebra
    import hypercomplex_engine
    import SplitOct

    def put(name: str, key: int | str, table: Table, relation: dict[str, Any]) -> None:
        packages[name]["tables"][str(key)] = table | {"relation": relation}

    identical = {"kind": "identical"}
    for n in (3, 4):
        dim = 2**n
        algebra = hypercomplex.cayley_dickson_algebra(n)

        def hypercomplex_product(i: int, j: int, a: Any = algebra) -> Sequence[Any]:
            return (a.e(i) * a.e(j)).coefficients()

        put("hypercomplex", dim, unit_table(dim, hypercomplex_product), identical)
        put("hypercomplex-engine", dim, int_table(*hypercomplex_engine.build_table("standard", n)), identical)
        basis: list[Any] = [1]
        for _ in range(n):
            basis = list(cayley_dickson.expand_basis(basis))

        def kd_product(i: int, j: int, b: list[Any] = basis) -> Sequence[Any]:
            return list(b[i] * b[j])

        put("cayley-dickson", dim, unit_table(dim, kd_product), identical)
    import Cayley_Calculator  # noqa: F401  (adds its module directory to sys.path)
    import sedenion

    def sedenion_unit(i: int) -> Any:
        return sedenion.Sedenion(*[1 if k == i else 0 for k in range(16)])

    put("Cayley-Calculator", 16, unit_table(16, lambda i, j: list(sedenion_unit(i) * sedenion_unit(j))), identical)
    put("hypercomplex-engine", "split-8", int_table(*hypercomplex_engine.build_table("split", 3)), {"kind": "split"})

    def split_unit(i: int) -> Any:
        return SplitOct.SplitOctonion([1 if k == i else 0 for k in range(8)])

    put("splitoct", 8, unit_table(8, lambda i, j: (split_unit(i) * split_unit(j)).x), {"kind": "split"})
    import octonion

    constants = octonion.STRUCTURE_CONSTANTS.detach().cpu().numpy()
    relabeling = {"kind": "signed relabeling", "pi": TORCH_TO_CD_PI, "eta": TORCH_TO_CD_ETA}
    put("octonion", 8, unit_table(8, lambda i, j: constants[i, j]), relabeling)
    require(
        hypercomplex_algebra.multiply_expressions("e5", "e6") == "-e3", "hypercomplex-algebra differs from its engine"
    )

    def hypercomplex_unit(dim: int) -> Callable[[int, int], tuple[int, int]]:
        algebra = hypercomplex.cayley_dickson_algebra(dim.bit_length() - 1)

        def mul(i: int, j: int) -> tuple[int, int]:
            coeffs = [float(c) for c in (algebra.e(i) * algebra.e(j)).coefficients()]
            index = next(k for k, c in enumerate(coeffs) if c != 0)
            return (1 if coeffs[index] > 0 else -1), index

        return mul

    def engine_unit(variant: str) -> Callable[[int, int], tuple[int, int]]:
        def mul(i: int, j: int) -> tuple[int, int]:
            sign, index = hypercomplex_engine.multiply("standard", (1, i), (1, j), engine=variant)
            return int(sign), int(index)

        return mul

    evaluators = {
        "hypercomplex": lambda dim: {"default": hypercomplex_unit(dim)},
        "hypercomplex-engine": lambda dim: {variant: engine_unit(variant) for variant in ("fast", "holographic")},
    }
    for name, (dims, count) in SAMPLED.items():
        packages[name]["samples"] = {}
        for dim in dims:
            pairs = sample_pairs(name, dim, count)
            packages[name]["samples"][str(dim)] = {
                "pairs": count,
                "signs": {label: sign_string(dim, pairs, mul) for label, mul in evaluators[name](dim).items()},
            }
    return {"schema": "algebra-package-tables-v1", "packages": packages}


def omega(sign: list[list[int]], p: int, q: int, r: int) -> int:
    return sign[p][q] * sign[p ^ q][r] * sign[q][r] * sign[p][q ^ r]


def check_table(name: str, dim: int, table: Table) -> None:
    sign, index, relation = table["signs"], table["index"], table["relation"]
    reference = [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]
    xor_indexed = all(index[p][q] == p ^ q for p in range(dim) for q in range(dim))
    if relation["kind"] == "identical":
        require(sign == reference and xor_indexed, f"{name} D={dim}: not identical to cd_core")
    elif relation["kind"] == "split":
        require(xor_indexed, f"{name}: split table is not XOR-indexed")
        triples = itertools.product(range(dim), repeat=3)
        require(
            all(omega(sign, p, q, r) == omega(reference, p, q, r) for p, q, r in triples),
            f"{name}: split associator signs differ from cd_core",
        )
        require(sum(sign[i][i] == 1 for i in range(1, dim)) == dim // 2, f"{name}: split basis squares differ")
    elif relation["kind"] == "signed relabeling":
        pi, eta = relation["pi"], relation["eta"]
        for p, q in itertools.product(range(dim), repeat=2):
            r = index[p][q]
            require(pi[r] == pi[p] ^ pi[q], f"{name}: index map is not a homomorphism")
            flip = (eta[p] + eta[q] + eta[r]) % 2
            require(sign[p][q] == reference[pi[p]][pi[q]] * (-1) ** flip, f"{name}: relabeling fails at e{p} e{q}")
    else:
        raise RuntimeError(f"{name}: unknown relation {relation['kind']}")


def check(data: dict[str, Any]) -> int:
    require(data.get("schema") == "algebra-package-tables-v1", "unknown evidence schema")
    packages = data["packages"]
    require(set(packages) == set(RELEASES), "package set differs from the declared releases")
    checked = 0
    for name, entry in packages.items():
        require(entry["release_sha256"] == RELEASES[name][2], f"{name}: release digest differs")
        installed = entry["installed"]
        require(
            installed["packaging_shims"] == PACKAGING_SHIMS.get(name, {})
            and installed["byte_identical_to_release"] + len(installed["packaging_shims"]) == installed["module_files"]
            and installed["module_files"] > 0,
            f"{name}: installed modules are not bound to the release archive",
        )
        for key, table in entry["tables"].items():
            check_table(name, int(str(key).rsplit("-", 1)[-1]), table)
            checked += 1
    for name, (dims, count) in SAMPLED.items():
        samples = packages[name].get("samples", {})
        require(sorted(samples) == sorted(str(dim) for dim in dims), f"{name}: sampled dimensions differ")
        for dim in dims:
            entry = samples[str(dim)]
            require(entry["pairs"] == count and bool(entry["signs"]), f"{name} D={dim}: sample size differs")
            expected = "".join("+" if cd_sign(dim, a, b) > 0 else "-" for a, b in sample_pairs(name, dim, count))
            for label, signs in entry["signs"].items():
                require(signs == expected, f"{name} D={dim} {label}: sampled products disagree with cd_core")
            checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--extract",
        type=Path,
        metavar="ARCHIVES",
        help="directory holding the pinned release archives; binds and imports the installed packages",
    )
    mode.add_argument("--check", action="store_true", help="verify retained evidence against cd_core")
    args = parser.parse_args()
    if args.extract:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps(extract(args.extract), indent=1) + "\n")
        print(f"wrote {EVIDENCE.relative_to(ROOT)}")
    checked = check(json.loads(EVIDENCE.read_text()))
    print(f"algebra package tables: {checked} tables and sample sets match their declared relation to cd_core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
