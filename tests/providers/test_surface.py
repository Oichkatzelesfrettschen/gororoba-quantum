"""Every provider-library name the repository's code imports resolves under the pinned versions.

ci/provider_surface.py reads gororoba_quantum/, scripts/ and ci/ when the test runs, so a new import joins the surface
without an edit here; a version bump that renames or removes any name the code reaches fails here before a script
meets it on a host.
"""

from __future__ import annotations

import importlib
from types import ModuleType

import pytest
from provider_surface import FOREIGN, PINNED, ROOT, surface


def resolve(module: str, dotted: str) -> object:
    target: object = importlib.import_module(module)
    for part in filter(None, dotted.split(".")):
        try:
            target = getattr(target, part)
        except AttributeError:
            if not isinstance(target, ModuleType):
                raise
            target = importlib.import_module(f"{target.__name__}.{part}")
    return target


# One xdist worker holds every case, so the scan (a few seconds of parsing) runs once.
pytestmark = pytest.mark.xdist_group("provider-surface")


def test_foreign_interpreter_files_exist() -> None:
    missing = [name for name in FOREIGN if not (ROOT / name).is_file()]
    if missing:
        raise AssertionError(f"FOREIGN names files that no longer exist: {missing}")


@pytest.mark.parametrize("package", PINNED)
def test_imported_names_resolve(package: str) -> None:
    uses = surface()[package]
    failures = []
    for (module, dotted), files in sorted(uses.items()):
        try:
            resolve(module, dotted)
        except (ImportError, AttributeError) as error:
            failures.append(f"{module}:{dotted or '*'} ({sorted(files)[0]}): {type(error).__name__}: {error}")
    if failures:
        raise AssertionError(f"{len(failures)} of {len(uses)} {package} names fail:\n" + "\n".join(failures))
