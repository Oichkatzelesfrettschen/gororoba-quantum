"""A copy of a function whose module-level names resolve through a caller's overrides first."""

from __future__ import annotations

import types
from collections.abc import Callable
from typing import Any


def rebound(function: Callable[..., Any], **overrides: Any) -> Any:
    """A copy of `function` whose direct global-name lookups resolve through `overrides` before its module's.

    Only names that the copied code itself loads are overridden. The copy shares the code and defaults of the
    original, and the original module stays unmodified, which keeps a digest-bound historical function at its bytes.
    A callee that the copy calls keeps its own module's globals, so a callee that must see an override is rebound too
    and passed as an override of the caller (measured: a nested callee reads its own module's value, a direct lookup
    reads the override). The copy snapshots the module's globals when `rebound` runs, so a later change to the module
    does not reach it.
    """
    if not isinstance(function, types.FunctionType):
        raise TypeError(f"{function!r} is not a plain function")
    clone = types.FunctionType(
        function.__code__, {**function.__globals__, **overrides}, function.__name__, function.__defaults__
    )
    clone.__kwdefaults__ = function.__kwdefaults__
    return clone
