from .compose_signature import compose_signature
from .get_signature import get_signature
from .set_signature import set_signature


_DESIGN_NOTES = """
# Signature Operations Sub-Package

## Purpose
The three basic operations on signatures: read one, build one, attach one.
Plain imports, no `__all__`: the package root decides what is public.

## Internal Components Registry

| Component           | Type        | Description                                          |
| :------------------ | :---------- | :--------------------------------------------------- |
| `compose_signature` | Function    | Builds an `inspect.Signature`, always validated.     |
| `get_signature`     | Function    | Reads a signature with a readable failure.           |
| `set_signature`     | Function    | Attaches a signature through `__signature__`.        |
| `_validations`      | Sub-package | The errors of reading and building.                  |
"""
