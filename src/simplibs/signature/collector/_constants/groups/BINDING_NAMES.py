from typing import Final


BINDING_NAMES: Final[frozenset[str]] = frozenset({"cls", "self"})
"""The conventional names of the bound first parameter of a method."""


_DESIGN_NOTES = """
# BINDING_NAMES — The Parameters a Method Gets for Free

## Purpose
`self` and `cls` are filled in by Python when a method is called, so a signature
built for the caller usually should not show them. The collector adds these names
to its exclusions when `include_binding=False`.

## Why Names, Not a Kind
A bound parameter is an ordinary `POSITIONAL_OR_KEYWORD` one; nothing but the
convention marks it. Variadics, by contrast, have a kind of their own and are
filtered by it (see `add_param`).

## Why a `frozenset`
Immutable, so no caller can change what every other caller excludes, and it
feeds `set.update` directly.
"""
