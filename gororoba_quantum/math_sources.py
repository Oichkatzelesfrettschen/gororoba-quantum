"""Resolve the Rocq sources that gororoba-math holds under rocq/quantum for this repository.

The sources moved to gororoba-math; this repository keeps a pin, a resolver and
the retained replay bundles that read them. ``ci/gororoba_math.pin`` names the
commit of gororoba-math whose ``rocq/quantum`` tree the retained digests bind.
A local run locates a checkout of that commit through the environment variable
``GOROROBA_MATH``, and hosted CI fetches the pin (ci/fetch_gororoba_math.sh).

The set of moved sources is the ``.v`` lines of ``rocq/quantum/_RocqProject`` in
that checkout, so a pin bump that adds a source moves it without a code change.
A source this repository still tracks under ``proofs/`` and the project file
omits keeps resolving to the checkout's own copy.

A retained replay bundle (docs/evidence/BUNDLE/replay_rocq.sh) reads
``$repository_root/proofs/NAME.v``, where ``repository_root`` is three levels
above the script, and its bytes stay fixed. ``shadow_root`` builds a directory
tree whose ``proofs/`` holds the digest-checked sources and whose other entries
are the checkout's own, so the unmodified script resolves its inputs there.

References in records. A live record names a moved source as
``gororoba-math:rocq/quantum/NAME.v`` (REFERENCE_PREFIX); resolve_reference
maps it to the file of the checkout. A closed plan record keeps its
``proofs/NAME.v`` references and bytes; relocated_reference maps such a
reference to the new form while the repository no longer tracks the file.

Digests. Every moved source is checked against the sha256 the retained
records already hold: the ``proofs/NAME.v`` rows of docs/evidence/*/*.sha256
(STALE_MANIFESTS lists the one ledger whose row predates its source) and the
evidence entries of docs/state/research_state.json. Two different digests for
one source, a source without a digest, an unset GOROROBA_MATH, a checkout whose
HEAD differs from the pin and a source whose bytes differ each raise
MathSourcesError.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_VARIABLE = "GOROROBA_MATH"
REQUIRED_VARIABLE = "GOROROBA_MATH_REQUIRED"
SUBDIRECTORY = "rocq/quantum"
PROJECT_FILE = "_RocqProject"
REFERENCE_PREFIX = "gororoba-math:" + SUBDIRECTORY + "/"
PIN_FILE = "ci/gororoba_math.pin"
LEDGER_ROW = re.compile(r"([0-9a-f]{64}) [ *]proofs/([A-Za-z0-9_]+\.v)")
# A ledger whose row for a source predates the source's current bytes; the replay bundle it sits in compiles the
# current bytes against its receipts, and no gate runs the ledger (docs/evidence/cd-sign-python-translation/README.md).
STALE_MANIFESTS = frozenset({"docs/evidence/cd-sign-python-translation/source_hashes.sha256"})
REGISTRY = "docs/state/research_state.json"
HEX40 = re.compile(r"[0-9a-f]{40}")
REFERENCE_PATTERN = re.compile(re.escape(REFERENCE_PREFIX) + r"[A-Za-z0-9_]+\.v")


class MathSourcesError(RuntimeError):
    """The gororoba-math sources are unresolved, off the pin, or differ from the retained digests."""


def validated_url(value: str) -> str:
    """A clone URL that git may receive: an ``https://`` URL or the absolute path of an existing directory.

    Any other transport (``ext::`` command URLs, ``file:``, ``ssh:``, a relative path) and any value with ``::`` or
    whitespace raises MathSourcesError, since git runs the command of an ``ext::`` URL."""
    if "::" in value or any(character.isspace() or ord(character) < 32 for character in value):
        raise MathSourcesError(f"clone URL {value!r} holds '::' or whitespace")
    if value.startswith("https://") and len(value) > len("https://"):
        return value
    if value.startswith("/") and Path(value).is_dir():
        return value
    raise MathSourcesError(f"clone URL {value!r} is neither an https:// URL nor an absolute directory")


def read_pin(root: Path = ROOT) -> str:
    pin = (root / PIN_FILE).read_text(encoding="utf-8").strip()
    if not HEX40.fullmatch(pin):
        raise MathSourcesError(f"{PIN_FILE} is not a 40-digit commit")
    return pin


def checkout(environ: Mapping[str, str] | None = None, root: Path = ROOT, *, verify_pin: bool = True) -> Path:
    """The gororoba-math checkout GOROROBA_MATH names; its HEAD must equal the pin unless verify_pin is false."""
    value = (os.environ if environ is None else environ).get(ENVIRONMENT_VARIABLE, "")
    if not value:
        raise MathSourcesError(
            f"{ENVIRONMENT_VARIABLE} is unset; set it to a gororoba-math checkout at the commit of {PIN_FILE}"
        )
    math = Path(value).expanduser()
    if not (math / SUBDIRECTORY / PROJECT_FILE).is_file():
        raise MathSourcesError(f"{ENVIRONMENT_VARIABLE}={value} holds no {SUBDIRECTORY}/{PROJECT_FILE}")
    if verify_pin:
        head = subprocess.run(
            ["git", "-C", str(math), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        ).stdout.strip()
        pin = read_pin(root)
        if head != pin:
            raise MathSourcesError(f"{ENVIRONMENT_VARIABLE} is at {head or 'no commit'}; {PIN_FILE} names {pin}")
    return math


def moved_names(math: Path) -> list[str]:
    """The sources of the checkout's rocq/quantum project file, as file names."""
    lines = (math / SUBDIRECTORY / PROJECT_FILE).read_text(encoding="utf-8").splitlines()
    names = [line.strip() for line in lines if line.strip().endswith(".v")]
    if not names:
        raise MathSourcesError(f"{SUBDIRECTORY}/{PROJECT_FILE} lists no source")
    return names


def resolve_reference(reference: str, math: Path, root: Path = ROOT) -> Path:
    """The verified file of the checkout that a ``gororoba-math:rocq/quantum/NAME.v`` reference names.

    The file passes verified_source, so no caller receives a checkout path whose bytes the retained digests have not
    confirmed."""
    if REFERENCE_PATTERN.fullmatch(reference) is None:
        raise MathSourcesError(f"{reference} is no {REFERENCE_PREFIX}NAME.v reference")
    name = reference[len(REFERENCE_PREFIX) :]
    if name not in moved_names(math):
        raise MathSourcesError(f"{reference} names no source of the {PROJECT_FILE} of the checkout")
    return verified_source(name, math, root)


def reference_for(name: str) -> str:
    return REFERENCE_PREFIX + name


def relocated_reference(reference: str, root: Path = ROOT) -> str | None:
    """The gororoba-math reference of a retained ``proofs/NAME.v`` reference whose file this tree no longer tracks."""
    match = re.fullmatch(r"proofs/([A-Za-z0-9_]+\.v)", reference)
    if match is None or (root / reference).exists():
        return None
    return reference_for(match[1])


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_RECORDED_CACHE: dict[tuple[str, tuple[tuple[str, int, int], ...]], dict[str, str]] = {}


def recorded_digests(root: Path = ROOT) -> dict[str, str]:
    """The sha256 that the retained records hold for each source name; two different digests raise.

    The result is cached per root and per (path, mtime, size) of the ledgers and the registry it reads."""
    files = [*sorted((root / "docs/evidence").glob("*/*.sha256")), root / REGISTRY]
    signature = tuple((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in files)
    key = (str(root), signature)
    if key not in _RECORDED_CACHE:
        _RECORDED_CACHE[key] = _read_recorded_digests(root)
    return _RECORDED_CACHE[key]


def _read_recorded_digests(root: Path) -> dict[str, str]:
    found: dict[str, dict[str, list[str]]] = {}

    def note(name: str, digest: str, origin: str) -> None:
        found.setdefault(name, {}).setdefault(digest, []).append(origin)

    for ledger in sorted((root / "docs/evidence").glob("*/*.sha256")):
        relative = ledger.relative_to(root).as_posix()
        if relative in STALE_MANIFESTS:
            continue
        for row in ledger.read_text(encoding="utf-8").splitlines():
            if match := LEDGER_ROW.fullmatch(row):
                note(match[2], match[1], relative)
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    for claim in registry["claims"]:
        for item in claim.get("evidence", []):
            path = item["path"]
            for prefix in ("proofs/", REFERENCE_PREFIX):
                if path.startswith(prefix) and "/" not in path[len(prefix) :]:
                    note(path[len(prefix) :], item["sha256"], REGISTRY)
    for name, digests in found.items():
        if len(digests) != 1:
            raise MathSourcesError(
                f"{name} has {len(digests)} recorded digests: "
                + "; ".join(
                    f"{digest[:12]} in {', '.join(sorted(set(origins)))}" for digest, origins in digests.items()
                )
            )
    return {name: next(iter(digests)) for name, digests in found.items()}


def verified_source(name: str, math: Path, root: Path = ROOT) -> Path:
    """The file of source ``name`` in the checkout, after four checks: the name is a plain ``NAME.v``, the file is a
    regular file that is no symbolic link and resolves inside the checkout, a retained record holds a digest of it,
    and its sha256 equals that digest."""
    if re.fullmatch(r"[A-Za-z0-9_]+\.v", name) is None:
        raise MathSourcesError(f"{name} is no source file name")
    path = math / SUBDIRECTORY / name
    if path.is_symlink():
        raise MathSourcesError(f"{name} is a symbolic link in the checkout")
    if not path.is_file():
        raise MathSourcesError(f"{path} is missing")
    if not path.resolve().is_relative_to(math.resolve()):
        raise MathSourcesError(f"{name} resolves outside the checkout")
    recorded = recorded_digests(root)
    if name not in recorded:
        raise MathSourcesError(f"no retained record holds a digest of {name}")
    if sha256_file(path) != recorded[name]:
        raise MathSourcesError(f"{name} differs from the retained digest {recorded[name][:12]}")
    return path


def verified_sources(math: Path, root: Path = ROOT, names: list[str] | None = None) -> dict[str, Path]:
    """Each moved source (or the listed ones) mapped to its file through verified_source."""
    return {name: verified_source(name, math, root) for name in (names if names is not None else moved_names(math))}


def shadow_root(destination: Path, math: Path, root: Path = ROOT, bundle: str | None = None) -> Path:
    """Build ``destination`` as a stand-in for the repository root in which ``proofs/`` holds the sources.

    Every moved source is copied from the checkout after its digest check; a source the project file omits and the
    repository still tracks is copied from ``proofs/``. Each top-level entry of the repository except ``proofs`` and
    ``.git`` is a symbolic link to the real one. With ``bundle``, ``docs/evidence/BUNDLE`` is a copy of the real
    directory under a real ``docs/evidence``, so a script run from it finds its root three levels up without
    following a link.
    """
    sources = verified_sources(math, root)
    proofs = destination / "proofs"
    proofs.mkdir(parents=True)
    local = root / "proofs"
    if local.is_dir():
        for path in sorted(local.glob("*.v")):
            if path.name not in sources:
                shutil.copyfile(path, proofs / path.name)
    for name, path in sources.items():
        shutil.copyfile(path, proofs / name)
    for entry in sorted(root.iterdir()):
        if entry.name in {"proofs", ".git"} or (bundle is not None and entry.name == "docs"):
            continue
        (destination / entry.name).symlink_to(entry)
    if bundle is not None:
        evidence = destination / "docs/evidence"
        evidence.mkdir(parents=True)
        shutil.copytree(root / "docs/evidence" / bundle, evidence / bundle, symlinks=True)
        for entry in sorted((root / "docs").iterdir()):
            if entry.name != "evidence":
                (destination / "docs" / entry.name).symlink_to(entry)
    return destination
