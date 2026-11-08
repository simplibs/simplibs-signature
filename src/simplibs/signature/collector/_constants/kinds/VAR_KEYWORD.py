import inspect
from typing import Final


VAR_KEYWORD: Final[inspect._ParameterKind] = inspect.Parameter.VAR_KEYWORD
"""The kind of `**kwargs`, which collects the surplus keyword arguments."""


_DESIGN_NOTES = """
# VAR_KEYWORD — The `**kwargs` Kind

## Purpose
A signature holds at most one of this kind, and it is always last. The
collector treats a second one as a name collision even when it has a different
name; flat mode merges all of them into the single `KWARGS` placeholder.

## Why an Alias
Short, grep-able and imported from one place.
"""
