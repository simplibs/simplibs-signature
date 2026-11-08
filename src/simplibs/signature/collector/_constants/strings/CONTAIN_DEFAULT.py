from typing import Final


CONTAIN_DEFAULT: Final[str] = "default"
"""Storage tier of the parameters that have a default value."""


_DESIGN_NOTES = """
# CONTAIN_DEFAULT — The Tier of Optional Parameters

## Purpose
The key of the second list inside every kind of the collector's storage map.
`get_ordered_params` reads it after `WITHOUT_DEFAULT`, which puts required
parameters before optional ones inside each kind, as Python demands.

## Why a String Key
The storage map is `kind -> tier -> list`. Named tiers are readable at the
call site and cannot be confused with a list index.
"""
