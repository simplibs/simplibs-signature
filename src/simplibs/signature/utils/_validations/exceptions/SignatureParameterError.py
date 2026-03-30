# Inners
from .SignatureError import SignatureError


class SignatureParameterError(SignatureError):
    """Raised when an argument of an incorrect type is passed by the user."""


_DESIGN_NOTES = """
# SignatureParameterError

## Purpose
A grouped exception for all invalid-argument errors in `simple-signature`.
Raised whenever the user passes a value of an incorrect type to a parameter.

## Group
Catches all invalid-argument errors raised by the library:
```python
except SignatureParameterError:
    # wrong argument type passed to SignatureCreator, ParameterCollector,
    # or any signature decorator
```

## Hierarchy
`SignatureParameterError` → `SignatureError` → `SimpleException`
Can therefore also be caught as `SignatureError` alongside `SignatureBuildError`.
"""