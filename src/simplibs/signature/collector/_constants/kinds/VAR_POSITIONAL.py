import inspect
from typing import Final


VAR_POSITIONAL: Final[inspect._ParameterKind] = inspect.Parameter.VAR_POSITIONAL
"""The kind of `*args`, which collects the surplus positional arguments."""


_DESIGN_NOTES = """
# VAR_POSITIONAL — The `*args` Kind

## Purpose
A signature holds at most one of this kind. The collector treats a second one
as a name collision even when it has a different name, and flat mode drops it
because a keyword-only API has no place for it.

## Why an Alias
Short, grep-able and imported from one place.
"""
