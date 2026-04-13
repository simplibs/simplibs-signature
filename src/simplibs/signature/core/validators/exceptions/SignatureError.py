from simplibs.exception import SimpleException


class SignatureError(SimpleException):
    """Base exception for the simple-signature library."""
    error_name = "SIGNATURE ERROR"
    _skip_locations = ("simplibs/signature",)


_DESIGN_NOTES = """
# SignatureError

## Purpose
The base exception for the entire `simple-signature` library.
Not intended to be raised directly — exists solely as a common ancestor
so that all library exceptions can be caught with a single `except` clause.

All instances automatically skip internal library frames and point to user code.

## Group
Catches all errors raised by `simple-signature`:
```python
except SignatureError:
    # any error raised by the simple-signature library
```

## Subclasses
| Class                   | Description                                      |
|-------------------------|--------------------------------------------------|
| `SignatureParameterError` | Invalid argument passed by the user            |
| `SignatureBuildError`     | Signature could not be built at runtime         |
"""