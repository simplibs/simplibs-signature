from .groups import BINDING_NAMES, VARIADIC_NAMES
from .placeholders import ARGS, KWARGS


__all__ = [
    # Groups
    "BINDING_NAMES",
    "VARIADIC_NAMES",
    # Placeholders
    "ARGS",
    "KWARGS",
]


_DESIGN_NOTES = """
# core/constants

## Contents
Constant values and pre-built objects used throughout the library for
filtering, exclusion, and placeholder parameters.

| Name              | Type      | Description                        |
|-------------------|-----------|------------------------------------|
| `BINDING_NAMES`   | frozenset | {'self', 'cls'} — binding params   |
| `VARIADIC_NAMES`  | frozenset | {'args', 'kwargs'} — variadic names|
| `ARGS`            | Parameter | Pre-built *args (VAR_POSITIONAL)   |
| `KWARGS`          | Parameter | Pre-built **kwargs (VAR_KEYWORD)   |
"""
