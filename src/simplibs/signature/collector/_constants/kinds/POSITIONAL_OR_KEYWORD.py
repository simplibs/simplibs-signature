import inspect
from typing import Final


POSITIONAL_OR_KEYWORD: Final[inspect._ParameterKind] = inspect.Parameter.POSITIONAL_OR_KEYWORD
"""The kind of an ordinary parameter, passed by position or by name."""


_DESIGN_NOTES = """
# POSITIONAL_OR_KEYWORD — The Ordinary Parameter

## Purpose
The kind of a plain `def f(x)` parameter, and the second in the order Python
requires. A required parameter of this kind may not follow an optional one
of this kind or of `POSITIONAL_ONLY`.

## Why an Alias
Short, grep-able and imported from one place.
"""
