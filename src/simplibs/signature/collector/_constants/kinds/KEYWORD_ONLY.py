import inspect
from typing import Final


KEYWORD_ONLY: Final[inspect._ParameterKind] = inspect.Parameter.KEYWORD_ONLY
"""The kind of a parameter that can only be passed by name (after `*` or `*args`)."""


_DESIGN_NOTES = """
# KEYWORD_ONLY — Parameters Passed by Name Only

## Purpose
One of the five kinds the collector stores. It is also the single target kind
of flat mode, where every regular parameter is turned into this one.

## Why an Alias
Short, grep-able and imported from one place, instead of `inspect.Parameter.KEYWORD_ONLY`
spelled out in every method.
"""
