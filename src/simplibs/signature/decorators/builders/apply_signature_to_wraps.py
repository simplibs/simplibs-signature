import inspect
from typing import Callable
from functools import wraps
from simplibs.validate import validate_call


@validate_call
def apply_signature_to_wraps(
    function: Callable,
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    """Wrap a function in a transparent wrapper that reports another signature.

    The wrapper is async for a coroutine function and plain otherwise, and
    passes every call through unchanged.

    Args:
        function: The function to wrap.
        signature: The signature the wrapper reports to `inspect`.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A new function, with the metadata of `function` and `signature` as
        its `__signature__`.
    """

    # 1. A coroutine function needs an async wrapper, so callers can still await it
    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            return await function(*args, **kwargs)
        wrapper = async_wrapper

    # 2. Anything else gets a plain wrapper
    else:
        @wraps(function)
        def sync_wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        wrapper = sync_wrapper

    # 3. Assign the custom signature
    wrapper.__signature__ = signature

    # 4. Return the transparent wrapper
    return wrapper


_DESIGN_NOTES = """
# apply_signature_to_wraps — A Signature Without Touching the Original

## Purpose
`set_signature` changes the function it is given. A decorator should not: the
same function may be decorated twice, or used undecorated elsewhere. This
function makes a new callable that forwards to the original and carries the
signature.

## Sync and Async
For `async def` the wrapper is `async def` as well and awaits the original,
so `inspect.iscoroutinefunction(wrapper)` stays true and `await wrapper()`
keeps working. A plain wrapper around a coroutine function would return a
coroutine object and silently lose that.

## `__signature__` Beats `__wrapped__`
`functools.wraps` sets `__wrapped__`, which `inspect.signature` normally
follows to the original. It stops at an object that has `__signature__`, so the
assigned signature is the one reported.

## Behaviour Is Not Changed
Arguments are forwarded as they come. The signature describes the call, it does
not enforce it.
"""
