import inspect
from typing import Callable
# Inners
from .apply_signature_to_wraps import apply_signature_to_wraps


def create_signature_decorator(
    signature: inspect.Signature,
    *,
    validate: bool = True
) -> Callable:
    """
    Creates a decorator that applies the provided inspect.Signature
    to the decorated function.

    The returned decorator wraps the function in a new callable with
    the given signature. Input validation is delegated to
    apply_signature_to_wraps().

    Args:
        signature: The signature to be applied to the decorated function.
        validate:  If True, validates the input arguments on application
                   (default: True).

    Returns:
        A decorator that applies the provided signature to a function.

    Example:
        decorator = create_signature_decorator(my_signature)

        @decorator
        def my_func(*args, **kwargs):
            ...
    """

    # 1. Define the decorator
    def decorator(function: Callable) -> Callable:

        # 1.1 Apply the signature to the wrapper
        return apply_signature_to_wraps(
            function  = function,
            signature = signature,
            validate  = validate,
        )

    # 2. Return the decorator
    return decorator


_DESIGN_NOTES = """
# create_signature_decorator

## Purpose
A factory that produces a decorator from an `inspect.Signature` — the
higher-level counterpart to `apply_signature_to_wraps()`. Separates the
moment of signature definition from the moment of application, enabling
the decorator pattern.

## Pattern it enables
```python
decorator = create_signature_decorator(my_signature)

@decorator
def my_func(*args, **kwargs):
    ...
```
Equivalent to calling `apply_signature_to_wraps(my_func, my_signature)`
directly — but expressed as a decorator, which is the natural Python
pattern for function transformation.

## Relationship to apply_signature_to_wraps()
`create_signature_decorator()` is a thin wrapper — all the actual work
(wrapping, signature assignment, validation) is delegated to
`apply_signature_to_wraps()`. This function only sources the decorator
factory layer on top.

## Why validate is passed through
Validation is deferred to `apply_signature_to_wraps()` — it runs at
decoration time, not at factory time. This means the signature itself
is not validated when the decorator is created, only when it is applied
to a function. This is intentional — the factory is a preparation step,
not an execution step.

## Notes
- No input validation at factory level — `signature` is not validated
  when `create_signature_decorator()` is called, only when the returned
  decorator is applied.
- The inner `decorator` function is intentionally minimal — a single
  delegating call with no additional logic.
"""