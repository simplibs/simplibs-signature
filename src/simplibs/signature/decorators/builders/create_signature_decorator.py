import inspect
from typing import Callable
from simplibs.validate import validate_call
# Inners
from .apply_signature_to_wraps import apply_signature_to_wraps


@validate_call
def create_signature_decorator(
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    """Create a decorator that gives a function a fixed signature.

    Args:
        signature: The signature every decorated function will report.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A decorator. Applied to a function, it returns a wrapper made by
        `apply_signature_to_wraps`.
    """

    # 1. Define the decorator factory
    def decorator(function: Callable) -> Callable:
        return apply_signature_to_wraps(
            function = function,
            signature = signature,
            _validate_call = _validate_call,
        )

    # 2. Return the decorator
    return decorator


_DESIGN_NOTES = """
# create_signature_decorator — From a Signature to a Decorator

## Purpose
Both `signature_copy` and `signature_set` have a finished `inspect.Signature`
and need a decorator that applies it. This function is that last step, so the
two share it.

## `_validate_call` Is Forwarded
The switch is handed on to `apply_signature_to_wraps`, so one flag controls the
checks at creation and at decoration time.
"""
