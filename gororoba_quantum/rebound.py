"""A copy of a function whose module-level names resolve through a caller's overrides first."""

from __future__ import annotations

import types
from collections.abc import Callable
from typing import Any


def rebound(function: Callable[..., Any], **overrides: Any) -> Any:
    """A copy of `function` whose module-level names resolve through `overrides` before its own module's.

    The copy shares the code and defaults of the original, so a rule the original implements keeps one home, and a
    call it makes to another name in `overrides` reaches the override. The original module stays unmodified, which
    keeps a digest-bound historical function at its bytes. A callee the copy reaches through its module's own globals
    resolves in that module, so a caller that needs a nested callee rebound passes it as an override too.
    """
    if not isinstance(function, types.FunctionType):
        raise TypeError(f"{function!r} is not a plain function")
    clone = types.FunctionType(
        function.__code__, {**function.__globals__, **overrides}, function.__name__, function.__defaults__
    )
    clone.__kwdefaults__ = function.__kwdefaults__
    return clone
