from typing import Callable
from simplibs.sentinels import UNSET, UnsetType
# Commons
from ..utils import create_copy_signature
# Inners
from .utils import create_signature_decorator


def signature_copy(
    base_func: Callable,
    return_type: type | None | UnsetType = UNSET,
) -> Callable:
    """
    Decorator that copies an inspect.Signature from the provided function or method.

    Always normalises the signature — removes self/cls and appends **kwargs.
    For full control over normalisation and validation use create_copy_signature().

    Args:
        base_func:   The function or method whose signature is to be copied.
        return_type: The return type of the signature. If UNSET, the original
                     is preserved. If None, the return annotation is removed.

    Returns:
        A decorator that applies the copied signature to a function.

    Example:
        @signature_copy(MyClass.__init__, return_type=MyClass)
        def my_func(*args, **kwargs):
            ...
    """

    # 1. Create a copy of the signature
    signature = create_copy_signature(
        base_func,
        return_type = return_type,
        normalize   = True,
        validate    = True,
    )

    # 2. Create and return the decorator
    return create_signature_decorator(signature, validate=False)


_DESIGN_NOTES = """
# signature_copy

## Purpose
A decorator factory that copies the signature of an existing function or
method onto the decorated function. The primary public-facing tool for
signature copying in the library — a convenience wrapper over
`create_copy_signature()` and `create_signature_decorator()`.

## Typical use case
Copying a signature from `__init__` onto a factory function or standalone
wrapper that accepts the same arguments but returns a value:
```python
@signature_copy(MyClass.__init__, return_type=MyClass)
def my_func(*args, **kwargs):
    ...
```

## What normalisation does
Normalisation is always applied — `self` / `cls` is removed and `**kwargs`
is appended. This makes the copied signature suitable for a standalone
function that is not bound to a class instance.

## Why validate=False in step 2
The signature produced in step 1 is already a valid `inspect.Signature`
— re-validating it inside `create_signature_decorator()` would be redundant.
`validate=False` is an intentional optimisation, not an oversight.

## return_type states
- `UNSET` (default) — the original return annotation is preserved as-is.
- `None`            — the return annotation is removed entirely.
- a type            — the return annotation is replaced with the given type.
  Useful when copying from `__init__` (which returns `None`) onto a factory
  function that returns an instance.

## Notes
- For full control over normalisation, validation, or return type handling
  use `create_copy_signature()` directly.
- The two-step flow (create signature → create decorator) mirrors the
  internal structure of `signature_from()` — both decorators share the
  same building blocks.
"""