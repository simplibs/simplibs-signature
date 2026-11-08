import inspect
from typing import Final


KWARGS: Final[inspect.Parameter] = inspect.Parameter(
    name="kwargs",
    kind=inspect.Parameter.VAR_KEYWORD,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty,
)
"""A ready-made `**kwargs` parameter."""


_DESIGN_NOTES = """
# KWARGS — A Ready-Made `**kwargs`

## Purpose
Building `inspect.Parameter(name="kwargs", kind=VAR_KEYWORD, ...)` by hand takes
four arguments for a thing that is always the same. `KWARGS` is that parameter,
to be passed as a source to `create_signature`, `signature` or
`ParameterCollector.add_param`.

## Used by Flat Mode
Flat mode merges every `**kwargs` it meets, under whatever name, into this one
parameter, so a flattened signature always ends in a plain `**kwargs`.

## Immutable
`inspect.Parameter` is immutable, so one shared instance is safe.
"""
