"""Run a generator of a Rocq source that lives in gororoba-math: GENERATOR [--check | --write] [generator options].

Four producers keep their bytes because retained ledgers and records bind their sha256
(scripts/cd_sign_rocq_ast.py, scripts/cd_sign_source_ast.py, gororoba_quantum/target_flip_certificate.py and
docs/evidence/cd-tower-kernel-certificates/kernel_certificates.py). Each writes and reads the proof at a module
constant that names proofs/NAME.v of this repository; this runner points that constant at
$GOROROBA_MATH/rocq/quantum/NAME.v and calls the producer's main, so the generated text, the markers and the
--check comparison are the producer's own.

--check (and any mode that only reads) needs the checkout at the commit of ci/gororoba_math.pin, the commit whose
bytes the retained digests bind; the producer reads a copy of the bytes that math_sources.verified_bytes returned,
so a source that is edited, symbolic-linked or off its retained digest fails before the comparison. --write
(--generate for kernel_certificates) needs no pin: it replaces the source in the checkout, refusing a target that is
a symbolic link or resolves outside the checkout. A write produces new bytes whose digest the retained records do
not hold yet, so no digest comparison applies there; the commit that lands the change in gororoba-math moves the
pin and the records are rebound. An unset GOROROBA_MATH ends the run with a message and status 2.
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
# directory of the module when it lies outside gororoba_quantum/ and scripts/)
GENERATORS = {
    "cd_sign_rocq_ast": ("PROOF", "CdSignPythonSemantics.v", "--write", None),
    "cd_sign_source_ast": ("PROOF", "CdSignSourceCertificate.v", "--write", None),
    "target_flip_certificate": ("CERTIFICATE_PATH", "TargetFlipN21.v", "--write", None),
    "kernel_certificates": (
        "ROCQ_FILE",
        "CdTowerCanonicalKernels.v",
        "--generate",
        "docs/evidence/cd-tower-kernel-certificates",
    ),
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in GENERATORS:
        print(f"usage: math_source_generators.py {{{'|'.join(GENERATORS)}}} [--check | --write] ...", file=sys.stderr)
        return 2
    name, options = argv[0], argv[1:]
    constant, source, write_flag, directory = GENERATORS[name]
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
            setattr(producer, constant, math_sources.writable_source(source, math))
        except math_sources.MathSourcesError as error:
            print(f"math_source_generators: {error}", file=sys.stderr)
            return 2
        result = producer.main()
        return 0 if result is None else int(result)
    # Every other mode reads the source: the producer reads a copy of the bytes that verified_bytes returned, so
    # the comparison covers the digest-checked content and not a second read of the checkout.
    try:
        data = math_sources.verified_bytes(source, math, ROOT)
    except math_sources.MathSourcesError as error:
        print(f"math_source_generators: {error}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="math-source-") as scratch:
        copy = Path(scratch) / source
        copy.write_bytes(data)
        setattr(producer, constant, copy)
        try:
            result = producer.main()
        except ValueError as error:
            # kernel_certificates names a mismatch relative to the repository root, which a copy lacks.
            print(f"math_source_generators: {name}: {error}", file=sys.stderr)
            return 1
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
