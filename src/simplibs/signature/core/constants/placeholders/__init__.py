from .ARGS import ARGS
from .KWARGS import KWARGS


__all__ = [
    "ARGS",
    "KWARGS",
]


_DESIGN_NOTES = """
# core/constants/placeholders

## Contents
Pre-built `inspect.Parameter` instances for variadic parameters.

| Name     | Description                    |
|----------|--------------------------------|
| `ARGS`   | *args (VAR_POSITIONAL)         |
| `KWARGS` | **kwargs (VAR_KEYWORD)         |
"""
