import inspect
from typing import Final


POSITIONAL_ONLY: Final[inspect._ParameterKind] = inspect.Parameter.POSITIONAL_ONLY
"""The kind of a parameter that can only be passed by position (before `/`)."""


_DESIGN_NOTES = """
# POSITIONAL_ONLY — Parameters Passed by Position Only

## Purpose
The first of the five kinds, in the order Python requires. The collector also
uses it to judge the order of defaults: once an optional positional-only
parameter is stored, a required one can no longer follow.

## Why an Alias
Short, grep-able and imported from one place.
"""
