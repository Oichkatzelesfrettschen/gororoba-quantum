"""Resolve the Rocq sources of gororoba-math that this repository's records cite.

The sources live in gororoba-math under ``rocq/quantum``; this repository holds a pin and a resolver and reads only the
sources a retained record names. ``ci/gororoba_math.pin`` names a commit of gororoba-math at which every cited source
keeps the sha256 its records hold, so a pin moves to any commit that leaves those bytes unchanged and a source no
record cites is never read. A local run locates a checkout of that commit through the environment variable
``GOROROBA_MATH`` (ci/fetch_gororoba_math.sh fetches the pin into a directory).

A source is cited when a record holds a digest of it: a ``proofs/NAME.v`` row of docs/evidence/*/*.sha256
(STALE_MANIFESTS lists the one ledger whose row predates its source) or an evidence entry of
docs/state/research_state.json that names ``proofs/NAME.v`` or ``gororoba-math:rocq/quantum/NAME.v``
(``cited_names``). A cited name must be a ``.v`` line of ``rocq/quantum/_RocqProject`` in the checkout.

A retained replay bundle (docs/evidence/BUNDLE/replay_rocq.sh) reads ``$repository_root/proofs/NAME.v``, where
``repository_root`` is three levels above the script, and its bytes stay fixed. ``shadow_root`` builds a directory tree
whose ``proofs/`` holds the digest-checked cited sources and whose other entries are the checkout's own, so a ledger
row ``proofs/NAME.v`` resolves there without a change to the ledger.

References in records. A live record names a source as ``gororoba-math:rocq/quantum/NAME.v`` (REFERENCE_PREFIX);
resolve_reference maps it to the file of the checkout. A closed plan record keeps its ``proofs/NAME.v`` references and
bytes; relocated_reference maps such a reference to the new form while the repository no longer tracks the file.

Digests. Every cited source is checked against the sha256 its records hold. Two different digests for one source, a
cited source absent from the project file, an unset GOROROBA_MATH, a checkout whose HEAD differs from the pin and a
source whose bytes differ each raise MathSourcesError.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
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


def cited_names(root: Path = ROOT) -> list[str]:
    """The sources that retained records cite, as file names in sorted order: the names recorded_digests holds."""
    return sorted(recorded_digests(root))


def _checked_location(name: str, math: Path) -> Path:
    """The path of source ``name`` in the checkout once the name is a plain ``NAME.v`` and the path is no symbolic
    link and resolves inside the checkout."""
    if re.fullmatch(r"[A-Za-z0-9_]+\.v", name) is None:
        raise MathSourcesError(f"{name} is no source file name")
    path = math / SUBDIRECTORY / name
    if path.is_symlink():
        raise MathSourcesError(f"{name} is a symbolic link in the checkout")
    if not path.resolve().is_relative_to(math.resolve()):
        raise MathSourcesError(f"{name} resolves outside the checkout")
    return path


def verified_bytes(name: str, math: Path, root: Path = ROOT) -> bytes:
    """The bytes of source ``name`` in the checkout, read once and hashed as read.

    The file must be a regular file at a checked location (no symbolic link, inside the checkout; the final
    component is opened with O_NOFOLLOW), a retained record must hold a digest of ``name``, and the sha256 of the
    returned bytes equals that digest. A caller that writes or parses these bytes uses what was verified."""
    path = _checked_location(name, math)
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as error:
        raise MathSourcesError(f"{path} cannot be opened: {error.strerror}") from error
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise MathSourcesError(f"{name} is not a regular file")
        data = handle.read()
    recorded = recorded_digests(root)
    if name not in recorded:
        raise MathSourcesError(f"no retained record holds a digest of {name}")
    if hashlib.sha256(data).hexdigest() != recorded[name]:
        raise MathSourcesError(f"{name} differs from the retained digest {recorded[name][:12]}")
    return data


def verified_source(name: str, math: Path, root: Path = ROOT) -> Path:
    """The location of source ``name`` in the checkout, after verified_bytes accepted its bytes.

    It guarantees the bytes at the moment of the call and nothing after it: a later read of the path can see other
    bytes. A caller that consumes the content calls verified_bytes and uses those bytes."""
    verified_bytes(name, math, root)
    return _checked_location(name, math)


def _require_listed(names: list[str], math: Path) -> None:
    listed = moved_names(math)
    absent = [name for name in names if name not in listed]
    if absent:
        raise MathSourcesError(f"{', '.join(absent)} is cited by a retained record and absent from {PROJECT_FILE}")


def verified_sources(math: Path, root: Path = ROOT, names: list[str] | None = None) -> dict[str, Path]:
    """Each cited source (or the listed ones) mapped to its file through verified_source.

    A cited source that the project file of the checkout omits raises MathSourcesError."""
    chosen = names if names is not None else cited_names(root)
    _require_listed(chosen, math)
    return {name: verified_source(name, math, root) for name in chosen}


def shadow_root(destination: Path, math: Path, root: Path = ROOT) -> Path:
    """Build ``destination`` as a stand-in for the repository root in which ``proofs/`` holds the cited sources.

    Every cited source is written from the bytes verified_bytes returned, so the copy is the digest-checked content; a
    source no record cites is not copied. Each top-level entry of the repository except ``proofs`` and ``.git`` is a
    symbolic link to the real one."""
    names = cited_names(root)
    _require_listed(names, math)
    contents = {name: verified_bytes(name, math, root) for name in names}
    proofs = destination / "proofs"
    proofs.mkdir(parents=True)
    for name, data in contents.items():
        (proofs / name).write_bytes(data)
    for entry in sorted(root.iterdir()):
        if entry.name not in {"proofs", ".git"}:
            (destination / entry.name).symlink_to(entry)
    return destination
