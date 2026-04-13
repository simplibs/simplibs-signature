from .create_positional_parameter import create_positional_parameter
from .create_keyword_parameter import create_keyword_parameter


__all__ = [
    "create_positional_parameter",
    "create_keyword_parameter",
]


_DESIGN_NOTES = """
# core/utils/parameters

## Contents
Factory functions for building `inspect.Parameter` instances.

| Name                          | Description                              |
|-------------------------------|------------------------------------------|
| `create_positional_parameter` | Creates POSITIONAL_ONLY or POSITIONAL_OR_KEYWORD parameters |
| `create_keyword_parameter`    | Creates KEYWORD_ONLY parameters         |
"""
