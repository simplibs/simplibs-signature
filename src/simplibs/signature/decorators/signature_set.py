import inspect
from typing import Callable
from simplibs.validate import validate_call
# Inners
from .builders import create_signature_decorator


@validate_call
def signature_set(
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    """Decorator factory that attaches a finished signature to a function.

    A decorator form of `set_signature`, but it wraps the function instead of
    changing it.

    Args:
        signature: The signature to attach.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A decorator that returns a wrapper reporting `signature`.
    """

    # 1. Create and return the decorator
    return create_signature_decorator(
        signature=signature,
        _validate_call=False
    )


_DESIGN_NOTES = """
# signature_set — Attach a Signature You Already Have

## Purpose
When the signature is ready (built by hand, by `create_signature`, read from
another function), nothing needs to be assembled. This decorator only attaches
it.

## Wraps, Does Not Modify
Despite the name's likeness to `set_signature`, the decorated function itself is
left alone: a wrapper is returned (see `apply_signature_to_wraps`).

## Related
`signature` assembles from sources, `signature_copy` copies from one callable.
"""
