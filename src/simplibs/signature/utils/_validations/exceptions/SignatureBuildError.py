# Inners
from .SignatureError import SignatureError


class SignatureBuildError(SignatureError):
    """Raised when a signature cannot be built — missing sources, unsupported types."""


_DESIGN_NOTES = """
# SignatureBuildError

## Purpose
A grouped exception for all runtime errors that occur during signature
construction — missing parameter sources, unsupported callable types,
duplicate parameters, or unintrospectable functions.

## Group
Catches all build-time errors raised by the library:
```python
except SignatureBuildError:
    # signature could not be built — check parameter sources and callable types
```

## Hierarchy
`SignatureBuildError` → `SignatureError` → `SimpleException`
Can therefore also be caught as `SignatureError` alongside `SignatureParameterError`.
"""