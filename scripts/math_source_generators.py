"""Run a generator of a Rocq source that lives in gororoba-math: GENERATOR [--check | --write] [generator options].

Four producers keep their bytes because retained ledgers and records bind their sha256
(scripts/cd_sign_rocq_ast.py, scripts/cd_sign_source_ast.py, gororoba_quantum/target_flip_certificate.py and
docs/evidence/cd-tower-kernel-certificates/kernel_certificates.py). Each writes and reads the proof at a module
constant that names proofs/NAME.v of this repository; this runner points that constant at
$GOROROBA_MATH/rocq/quantum/NAME.v and calls the producer's main, so the generated text, the markers and the
--check comparison are the producer's own.

A producer of the Gaussian-integer certificates (docs/evidence/a5-gaussian-certificates/) renders more than one
source: its entry then lists the constants and the source names as two tuples of equal length, and every constant
receives the location of the source at its position, under the rules above for one.

--check (and any mode that only reads) needs the checkout at the commit of ci/gororoba_math.pin, the commit whose
bytes the retained digests bind; the producer reads a copy of the bytes that math_sources.verified_bytes returned,
so a source that is edited, symbolic-linked or off its retained digest fails before the comparison. --write
(--generate for kernel_certificates) needs no pin: it replaces the source in the checkout, refusing a target that is
a symbolic link or resolves outside the checkout. A write produces new bytes whose digest the retained records do
not hold yet, so no digest comparison applies there; the commit that lands the change in gororoba-math moves the
pin and the records are rebound. An unset GOROROBA_MATH ends the run with a message and status 2.

The options a producer receives are its mode flags, spelled in full. Any other option ends the run with status 2
before the producer loads, since a producer option that names a path (--output of target_flip_certificate) or an
abbreviation argparse expands would move the read or the write off the location this runner checked. A producer
that writes through its replace_text function writes through replace_text of this module instead, whose scratch
file is created exclusively.
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(1, str(ROOT / "scripts"))

import math_sources  # noqa: E402

# producer module -> (module constant holding the proof path, source name in rocq/quantum, the flag that writes,
# directory of the module when it lies outside gororoba_quantum/ and scripts/). The producer accepts the write flag
# and --check, and nothing else. A producer of several sources lists its constants and their source names as
# tuples of equal length.
Names = str | tuple[str, ...]
GENERATORS: dict[str, tuple[Names, Names, str, str | None]] = {
    "cd_sign_rocq_ast": ("PROOF", "CdSignPythonSemantics.v", "--write", None),
    "cd_sign_source_ast": ("PROOF", "CdSignSourceCertificate.v", "--write", None),
    "target_flip_certificate": ("CERTIFICATE_PATH", "TargetFlipN21.v", "--write", None),
    "kernel_certificates": (
        "ROCQ_FILE",
        "CdTowerCanonicalKernels.v",
        "--generate",
        "docs/evidence/cd-tower-kernel-certificates",
    ),
    "gaussian_certificates": (
        ("G2_ROCQ_FILE", "ARC_ROCQ_FILE"),
        ("CdTowerG2Derivations.v", "A5W8ArcMatrixRanks.v"),
        "--write",
        "docs/evidence/a5-gaussian-certificates",
    ),
    "render_span": (
        "ROCQ_FILE",
        "CdTowerG2DerivationSpan.v",
        "--write",
        "docs/evidence/a5-gaussian-certificates",
    ),
}


def replace_text(path: Path, text: str) -> None:
    """Replace ``path`` with ``text`` through a scratch file created exclusively beside it.

    os.O_EXCL (tempfile.mkstemp) fails on an existing name, a symbolic link included, so the bytes land in a new
    regular file of this directory; os.replace then renames that file over ``path``, and a reader sees the old
    bytes or the new ones. The mode of an existing ``path`` carries over."""
    mode = path.stat().st_mode & 0o777 if path.is_file() else 0o644
    descriptor, scratch = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(scratch, mode)
        os.replace(scratch, path)
    except BaseException:
        Path(scratch).unlink(missing_ok=True)
        raise


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in GENERATORS:
        print(f"usage: math_source_generators.py {{{'|'.join(GENERATORS)}}} [--check | --write]", file=sys.stderr)
        return 2
    name, options = argv[0], argv[1:]
    constant, source, write_flag, directory = GENERATORS[name]
    constants = (constant,) if isinstance(constant, str) else constant
    sources = (source,) if isinstance(source, str) else source
    if len(constants) != len(sources) or not constants:
        print(
            f"math_source_generators: {name} lists {len(constants)} constants for {len(sources)} sources",
            file=sys.stderr,
        )
        return 2
    refused = [option for option in options if option not in {"--check", write_flag}]
    if refused:
        print(
            f"math_source_generators: {name} takes --check or {write_flag}, spelled in full; refused: "
            + " ".join(refused),
            file=sys.stderr,
        )
        return 2
    if directory is not None:
        sys.path.insert(2, str(ROOT / directory))
    try:
        math = math_sources.checkout(os.environ, ROOT, verify_pin=write_flag not in options)
    except math_sources.MathSourcesError as error:
        print(f"math_source_generators: {error}", file=sys.stderr)
        return 2
    producer = importlib.import_module(name)
    sys.argv = [str(producer.__file__), *options]
    if write_flag in options:
        # A write produces new bytes whose digest the retained records do not hold yet, so no digest comparison
        # applies; the target must be a plain file location inside the checkout, never a link out of it.
        try:
            targets = [math_sources.writable_source(each, math) for each in sources]
        except math_sources.MathSourcesError as error:
            print(f"math_source_generators: {error}", file=sys.stderr)
            return 2
        for each_constant, target in zip(constants, targets, strict=True):
            setattr(producer, each_constant, target)
        if hasattr(producer, "replace_text"):
            setattr(producer, "replace_text", replace_text)  # noqa: B010
        result = producer.main()
        return 0 if result is None else int(result)
    # Every other mode reads the source: the producer reads a copy of the bytes that verified_bytes returned, so
    # the comparison covers the digest-checked content and not a second read of the checkout.
    try:
        contents = [math_sources.verified_bytes(each, math, ROOT) for each in sources]
    except math_sources.MathSourcesError as error:
        print(f"math_source_generators: {error}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="math-source-") as scratch:
        for each_constant, each, data in zip(constants, sources, contents, strict=True):
            copy = Path(scratch) / each
            copy.write_bytes(data)
            setattr(producer, each_constant, copy)
        try:
            result = producer.main()
        except ValueError as error:
            # kernel_certificates names a mismatch relative to the repository root, which a copy lacks.
            print(f"math_source_generators: {name}: {error}", file=sys.stderr)
            return 1
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
