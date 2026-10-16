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
  "split" (same index table and associator signs as cd_core, e1 to e3
  squaring to -1 and e4 to e7 to +1, e0 the identity; such a table shares every basis associator
  with the ordinary algebra and is not isomorphic to it).

Each package is bound to its public release by the sha256 of its PyPI sdist
or GitHub archive; docs/notes/packages/ holds one note per package.

Two further modes build the same stack where no Arch package exists, such as
a Kaggle kernel:

- --fetch ARCHIVES downloads every pinned archive from ARCHIVE_URLS into
  ARCHIVES and keeps it only if its sha256 matches the pin.
- --install ARCHIVES unpacks each pinned archive, applies BUILD_RECIPES (the
  prepare() step of the local PKGBUILD, transcribed byte for byte), and
  installs it with pip without dependencies, then installs RUNTIME_PINS.
  --extract afterwards proves the result: it must regenerate tables.json
  with the bytes the repository retains.
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
SDIST = "https://files.pythonhosted.org/packages/source/{0}/{1}/{1}-{2}.tar.gz"
# Download location of each pinned archive, as the local PKGBUILD's source array names it.
ARCHIVE_URLS = {
    "hypercomplex": SDIST.format("h", "hypercomplex", "0.3.4"),
    "hypercomplex-engine": SDIST.format("h", "hypercomplex_engine", "0.5.0"),
    "hypercomplex-algebra": SDIST.format("h", "hypercomplex_algebra", "0.2.0.2"),
    "Cayley-Calculator": SDIST.format("c", "cayley_calculator", "1.3.1"),
    "cayley-dickson": RELEASES["cayley-dickson"][1],
    "octonion": SDIST.format("o", "octonion", "0.1.0"),
    "splitoct": RELEASES["splitoct"][1],
    "mathdunders": SDIST.format("m", "mathdunders", "0.4.2"),
}
_CAYLEY_DICKSON_PYPROJECT = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "cayley-dickson"
version = "0.1.0"
description = "Cayley-Dickson process in Python"
readme = "README.md"
license = "LicenseRef-All-Rights-Reserved"
dependencies = [
    "numpy",
    "pandas",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["cayley_dickson*", "src*"]
"""
_SPLITOCT_PYPROJECT = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "SplitOct"
version = "0.16"
description = "Split octonion algebra in python with SymPy"
readme = "README.md"
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
dependencies = [
    "sympy",
]

[tool.setuptools]
py-modules = ["SplitOct"]
"""
# The prepare() step of python-cayley-dickson and python-splitoct in the local
# PKGBUILDs: files written ("write") and archive members copied ("copy") before
# the wheel is built. The other packages build from their sdist unchanged.
BUILD_RECIPES: dict[str, dict[str, dict[str, str]]] = {
    "cayley-dickson": {
        "copy": {"src/cayley_dickson.py": "cayley_dickson/cayley_dickson.py"},
        "write": {
            "cayley_dickson/__init__.py": "from .cayley_dickson import *\n",
            "pyproject.toml": _CAYLEY_DICKSON_PYPROJECT,
        },
    },
    "splitoct": {"copy": {"src/SplitOct.py": "SplitOct.py"}, "write": {"pyproject.toml": _SPLITOCT_PYPROJECT}},
}
# Runtime dependencies an imported package needs beyond numpy, scipy, pandas,
# sympy and torch, pinned to the Arch package versions on the build host.
RUNTIME_PINS = ("numpy-quaternion==2024.0.13",)
# Installed files absent from the release archive, added by the local build
# recipe: name -> {installed path: sha256}.
PACKAGING_SHIMS = {
    "cayley-dickson": {
        "cayley_dickson/__init__.py": hashlib.sha256(b"from .cayley_dickson import *\n").hexdigest(),
    },
}
SAMPLED = {
    "hypercomplex": ((32, 64), 400, ("default",)),
    "hypercomplex-engine": (tuple(2**n for n in range(5, 13)), 3000, ("fast", "holographic")),
}
TORCH_TO_CD_PI = [0, 1, 2, 4, 3, 6, 7, 5]
TORCH_TO_CD_ETA = [0, 0, 0, 0, 0, 0, 1, 0]
IDENTICAL: dict[str, Any] = {"kind": "identical"}
SPLIT: dict[str, Any] = {"kind": "split"}
# Declared relation of every retained table to cd_core; --check requires exactly these.
RELATIONS: dict[str, dict[str, dict[str, Any]]] = {
    "hypercomplex": {"8": IDENTICAL, "16": IDENTICAL},
    "hypercomplex-engine": {"8": IDENTICAL, "16": IDENTICAL, "split-8": SPLIT},
    "hypercomplex-algebra": {},
    "Cayley-Calculator": {"16": IDENTICAL},
    "cayley-dickson": {"8": IDENTICAL, "16": IDENTICAL},
    "octonion": {"8": {"kind": "signed relabeling", "pi": TORCH_TO_CD_PI, "eta": TORCH_TO_CD_ETA}},
    "splitoct": {"8": SPLIT},
    "mathdunders": {},
}
# Basis squares of the split octonion tables: e1, e2, e3 square to -1, e4 to e7 to +1.
SPLIT_SQUARES = [1, -1, -1, -1, 1, 1, 1, 1]
EXPRESSION_SAMPLES = 200
EXPRESSION_DIM = 64

Table = dict[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def signed_unit(coefficients: Sequence[Any], label: str) -> tuple[int, int]:
    """(sign, index) of a coefficient vector that must be exactly one basis unit with coefficient +-1."""
    coeffs = [float(c) for c in coefficients]
    nonzero = [k for k, c in enumerate(coeffs) if abs(c) > 1e-12]
    require(len(nonzero) == 1 and abs(abs(coeffs[nonzero[0]]) - 1) < 1e-12, f"{label} is not a signed unit")
    return (1 if coeffs[nonzero[0]] > 0 else -1), nonzero[0]


def unit_table(dim: int, mul: Callable[[int, int], Sequence[Any]]) -> Table:
    """Read e_i e_j from a coefficient-returning product; every product must be a signed basis unit."""
    signs, index = [], []
    for i in range(dim):
        srow, irow = [], []
        for j in range(dim):
            sign, k = signed_unit(mul(i, j), f"e{i} e{j}")
            srow.append(sign)
            irow.append(k)
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
    matches = [
        path
        for path in sorted(archives.iterdir())
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == sha
    ]
    require(len(matches) == 1, f"{name}: {len(matches)} archives match the pinned sha256; exactly one is required")
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


def require_bound(module: Any, name: str) -> None:
    """The imported module file must belong to the distribution bind_installation checked."""
    files = {Path(str(f.locate())).resolve() for f in importlib.metadata.distribution(name).files or []}
    require(Path(module.__file__).resolve() in files, f"{module.__name__} resolves outside the {name} distribution")


def parse_expression(text: str) -> tuple[int, int]:
    """hypercomplex-algebra writes a signed basis unit as '[-]1' for e0 and '[-]eN' otherwise."""
    sign = -1 if text.startswith("-") else 1
    body = text.lstrip("-")
    require(body == "1" or (body.startswith("e") and body[1:].isdigit()), f"unexpected product {text!r}")
    return sign, 0 if body == "1" else int(body[1:])


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

    for module, owner in (
        (cayley_dickson, "cayley-dickson"),
        (hypercomplex, "hypercomplex"),
        (hypercomplex_algebra, "hypercomplex-algebra"),
        (hypercomplex_engine, "hypercomplex-engine"),
        (SplitOct, "splitoct"),
    ):
        require_bound(module, owner)

    def put(name: str, key: int | str, table: Table, relation: dict[str, Any]) -> None:
        packages[name]["tables"][str(key)] = table | {"relation": relation}

    for n in (3, 4):
        dim = 2**n
        algebra = hypercomplex.cayley_dickson_algebra(n)

        def hypercomplex_product(i: int, j: int, a: Any = algebra) -> Sequence[Any]:
            return (a.e(i) * a.e(j)).coefficients()

        put("hypercomplex", dim, unit_table(dim, hypercomplex_product), IDENTICAL)
        put("hypercomplex-engine", dim, int_table(*hypercomplex_engine.build_table("standard", n)), IDENTICAL)
        basis: list[Any] = [1]
        for _ in range(n):
            basis = list(cayley_dickson.expand_basis(basis))

        def kd_product(i: int, j: int, b: list[Any] = basis) -> Sequence[Any]:
            return list(b[i] * b[j])

        put("cayley-dickson", dim, unit_table(dim, kd_product), IDENTICAL)
    import Cayley_Calculator  # noqa: F401  (adds its module directory to sys.path)
    import sedenion

    require_bound(sedenion, "Cayley-Calculator")

    def sedenion_unit(i: int) -> Any:
        return sedenion.Sedenion(*[1 if k == i else 0 for k in range(16)])

    put("Cayley-Calculator", 16, unit_table(16, lambda i, j: list(sedenion_unit(i) * sedenion_unit(j))), IDENTICAL)
    put("hypercomplex-engine", "split-8", int_table(*hypercomplex_engine.build_table("split", 3)), SPLIT)

    def split_unit(i: int) -> Any:
        return SplitOct.SplitOctonion([1 if k == i else 0 for k in range(8)])

    put("splitoct", 8, unit_table(8, lambda i, j: (split_unit(i) * split_unit(j)).x), SPLIT)
    import octonion

    require_bound(octonion, "octonion")
    constants = octonion.STRUCTURE_CONSTANTS.detach().cpu().numpy()
    put("octonion", 8, unit_table(8, lambda i, j: constants[i, j]), RELATIONS["octonion"]["8"])
    expression_pairs = sample_pairs("hypercomplex-algebra", EXPRESSION_DIM, EXPRESSION_SAMPLES)
    packages["hypercomplex-algebra"]["expression_samples"] = {
        "dim": EXPRESSION_DIM,
        "pairs": EXPRESSION_SAMPLES,
        "products": [hypercomplex_algebra.multiply_expressions(f"e{a}", f"e{b}") for a, b in expression_pairs],
    }

    def hypercomplex_unit(dim: int) -> Callable[[int, int], tuple[int, int]]:
        algebra = hypercomplex.cayley_dickson_algebra(dim.bit_length() - 1)

        def mul(i: int, j: int) -> tuple[int, int]:
            return signed_unit((algebra.e(i) * algebra.e(j)).coefficients(), f"D={dim} e{i} e{j}")

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
    for name, (dims, count, _) in SAMPLED.items():
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
    require(
        len(sign) == len(index) == dim and all(len(row) == dim for row in sign + index),
        f"{name} D={dim}: table shape is not {dim} x {dim}",
    )
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
        require([sign[i][i] for i in range(dim)] == SPLIT_SQUARES, f"{name}: split basis squares differ")
        require(all(sign[0][q] == 1 and sign[q][0] == 1 for q in range(dim)), f"{name}: e0 is not the split identity")
    elif relation["kind"] == "signed relabeling":
        pi, eta = relation["pi"], relation["eta"]
        require(sorted(pi) == list(range(dim)) and len(eta) == dim, f"{name}: relabeling is not a permutation")
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
        version, release, sha = RELEASES[name]
        require(
            (entry["version"], entry["release"], entry["release_sha256"]) == (version, release, sha),
            f"{name}: recorded release differs from the pin",
        )
        require(set(entry["tables"]) == set(RELATIONS[name]), f"{name}: retained table set differs")
        for key, table in entry["tables"].items():
            require(table["relation"] == RELATIONS[name][key], f"{name} {key}: declared relation differs")
        installed = entry["installed"]
        require(
            (version.startswith("commit ") or installed["distribution_version"] == version)
            and installed["packaging_shims"] == PACKAGING_SHIMS.get(name, {})
            and installed["byte_identical_to_release"] + len(installed["packaging_shims"]) == installed["module_files"]
            and installed["module_files"] > 0,
            f"{name}: installed modules are not bound to the release archive",
        )
        for key, table in entry["tables"].items():
            check_table(name, int(str(key).rsplit("-", 1)[-1]), table)
            checked += 1
    split = packages["splitoct"]["tables"]["8"], packages["hypercomplex-engine"]["tables"]["split-8"]
    require(
        (split[0]["signs"], split[0]["index"]) == (split[1]["signs"], split[1]["index"]),
        "the splitoct and hypercomplex-engine split tables differ",
    )
    expressions = packages["hypercomplex-algebra"]["expression_samples"]
    require(
        (expressions["dim"], expressions["pairs"], len(expressions["products"]))
        == (EXPRESSION_DIM, EXPRESSION_SAMPLES, EXPRESSION_SAMPLES),
        "hypercomplex-algebra expression sample size differs",
    )
    pairs = sample_pairs("hypercomplex-algebra", EXPRESSION_DIM, EXPRESSION_SAMPLES)
    for (a, b), text in zip(pairs, expressions["products"], strict=True):
        require(
            parse_expression(text) == (cd_sign(EXPRESSION_DIM, a, b), a ^ b),
            f"hypercomplex-algebra: e{a} e{b} = {text} differs from cd_core",
        )
    checked += 1
    for name, (dims, count, labels) in SAMPLED.items():
        samples = packages[name].get("samples", {})
        require(sorted(samples) == sorted(str(dim) for dim in dims), f"{name}: sampled dimensions differ")
        for dim in dims:
            entry = samples[str(dim)]
            require(entry["pairs"] == count, f"{name} D={dim}: sample size differs")
            require(sorted(entry["signs"]) == sorted(labels), f"{name} D={dim}: sampled evaluators differ")
            expected = "".join("+" if cd_sign(dim, a, b) > 0 else "-" for a, b in sample_pairs(name, dim, count))
            for label, signs in entry["signs"].items():
                require(signs == expected, f"{name} D={dim} {label}: sampled products disagree with cd_core")
            checked += 1
    return checked


def archive_name(name: str) -> str:
    return f"{name}-{RELEASES[name][2][:12]}.tar.gz"


def fetch(archives: Path) -> None:
    import urllib.request

    archives.mkdir(parents=True, exist_ok=True)
    for name, url in ARCHIVE_URLS.items():
        target = archives / archive_name(name)
        if not target.is_file():
            with urllib.request.urlopen(url, timeout=120) as response:
                data = response.read()
            require(
                hashlib.sha256(data).hexdigest() == RELEASES[name][2], f"{name}: {url} differs from the pinned sha256"
            )
            target.write_bytes(data)
        require(
            hashlib.sha256(target.read_bytes()).hexdigest() == RELEASES[name][2],
            f"{name}: {target} differs from the pin",
        )
        print(f"{name}: {target.name} matches the pinned sha256")


def install(archives: Path) -> None:
    import shutil
    import subprocess
    import tempfile

    for name in RELEASES:
        archive = archives / archive_name(name)
        require(
            hashlib.sha256(archive.read_bytes()).hexdigest() == RELEASES[name][2], f"{name}: {archive} is not the pin"
        )
        with tempfile.TemporaryDirectory() as scratch:
            with tarfile.open(archive) as tar:
                tar.extractall(scratch, filter="data")
            (top,) = [path for path in Path(scratch).iterdir() if path.is_dir()]
            recipe = BUILD_RECIPES.get(name, {})
            for source, destination in recipe.get("copy", {}).items():
                (top / destination).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(top / source, top / destination)
            for destination, text in recipe.get("write", {}).items():
                (top / destination).parent.mkdir(parents=True, exist_ok=True)
                (top / destination).write_text(text, encoding="utf-8")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", str(top)], check=True)
        print(f"{name}: installed from {archive.name}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *RUNTIME_PINS], check=True)


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
    mode.add_argument("--fetch", type=Path, metavar="ARCHIVES", help="download and verify every pinned archive")
    mode.add_argument("--install", type=Path, metavar="ARCHIVES", help="build and install the pinned archives")
    args = parser.parse_args()
    if args.fetch:
        fetch(args.fetch)
        return 0
    if args.install:
        install(args.install)
        return 0
    if args.extract:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps(extract(args.extract), indent=1) + "\n")
        print(f"wrote {EVIDENCE.relative_to(ROOT)}")
    checked = check(json.loads(EVIDENCE.read_text()))
    print(f"algebra package tables: {checked} tables and sample sets match their declared relation to cd_core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
