import inspect
from typing import Final


ARGS: Final[inspect.Parameter] = inspect.Parameter(
    name="args",
    kind=inspect.Parameter.VAR_POSITIONAL,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty,
)
"""A ready-made `*args` parameter."""


_DESIGN_NOTES = """
# ARGS — A Ready-Made `*args`

## Purpose
Building `inspect.Parameter(name="args", kind=VAR_POSITIONAL, ...)` by hand takes
four arguments for a thing that is always the same. `ARGS` is that parameter,
to be passed as a source to `create_signature`, `signature` or
`ParameterCollector.add_param`.

## Public, Not Used Internally
The library itself never needs it: flat mode drops `*args` instead of creating
one. It is exported as the counterpart of `KWARGS`, for callers who want an
open-ended signature.

## Immutable
`inspect.Parameter` is immutable, so one shared instance is safe.
"""
