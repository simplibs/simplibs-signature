import inspect
from typing import Final


EMPTY: Final = inspect.Parameter.empty
"""Marker of a missing default value or annotation (`inspect.Parameter.empty`)."""


_DESIGN_NOTES = """
# EMPTY — The Marker of "Nothing Given"

## Purpose
`inspect.Parameter.empty` is how the standard library says "this parameter has no
default" and "this parameter has no annotation". The collector asks that
question for every parameter it stores (`param.default is EMPTY`).

## Why an Alias
One short name, imported from one place, instead of a four-part attribute path
repeated in every method. It is the same object, so `is` comparison works
with values that come from `inspect` itself.
"""
