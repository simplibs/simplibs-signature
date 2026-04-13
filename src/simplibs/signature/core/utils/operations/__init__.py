from .get_signature import get_signature
from .set_signature import set_signature
from .compose_signature import compose_signature


__all__ = [
    "get_signature",
    "set_signature",
    "compose_signature",
]


_DESIGN_NOTES = """
# core/utils/operations

## Contents
Basic operations for working with `inspect.Signature` objects.

| Name                | Description                                   |
|---------------------|-----------------------------------------------|
| `get_signature`     | Safely extract signature from a callable     |
| `set_signature`     | Assign a signature to a function via __signature__ |
| `compose_signature` | Create a signature from parameters           |
"""
