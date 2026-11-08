from .create_keyword_parameter import create_keyword_parameter
from .create_positional_parameter import create_positional_parameter


_DESIGN_NOTES = """
# Parameter Creators Sub-Package

## Purpose
Short, readable constructors of `inspect.Parameter`. Plain imports, no
`__all__`: the package root decides what is public.

## Internal Components Registry

| Component                     | Type        | Description                                        |
| :---------------------------- | :---------- | :------------------------------------------------- |
| `create_keyword_parameter`    | Function    | A keyword-only parameter.                          |
| `create_positional_parameter` | Function    | A positional-only or ordinary positional parameter.|
| `_validations`                | Sub-package | The default-versus-annotation check.               |
"""
