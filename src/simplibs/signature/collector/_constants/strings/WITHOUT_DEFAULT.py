from typing import Final


WITHOUT_DEFAULT: Final[str] = "no_default"
"""Storage tier of the parameters that have no default value."""


_DESIGN_NOTES = """
# WITHOUT_DEFAULT — The Tier of Required Parameters

## Purpose
The key of the first list inside every kind of the collector's storage map.
Variadic parameters (`*args`, `**kwargs`) can never have a default, so they
always live here.

## Why a String Key
The storage map is `kind -> tier -> list`. Named tiers are readable at the
call site and cannot be confused with a list index.
"""
