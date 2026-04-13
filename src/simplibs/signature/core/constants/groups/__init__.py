from .BINDING_NAMES import BINDING_NAMES
from .VARIADIC_NAMES import VARIADIC_NAMES


__all__ = [
    "BINDING_NAMES",
    "VARIADIC_NAMES",
]


_DESIGN_NOTES = """
# core/constants/groups

## Contents
Constant sets of parameter names used for filtering and exclusion logic.

| Name              | Description                                      |
|-------------------|--------------------------------------------------|
| `BINDING_NAMES`   | frozenset({'self', 'cls'}) — binding parameters |
| `VARIADIC_NAMES`  | frozenset({'args', 'kwargs'}) — variadic names  |
"""
