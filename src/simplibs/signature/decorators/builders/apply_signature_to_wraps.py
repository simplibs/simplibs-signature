import inspect
from typing import Callable
from functools import wraps
# Outers
from ...core.validators import validate_is_callable, validate_is_inspect_signature


def apply_signature_to_wraps(
    function: Callable,
    signature: inspect.Signature,
    *,
    validate: bool = True
) -> Callable:
    """
    Creates a wrapper around a function with an assigned inspect.Signature.

    This utility detects whether the source function is synchronous or
    asynchronous and creates the appropriate wrapper type to ensure
    compatibility with asyncio while injecting the custom signature.

    Args:
        function:  The function to be wrapped.
        signature: The signature to assign to the wrapper.
        validate:  If True, validates the input arguments.

    Returns:
        A new wrapper (sync or async) with the assigned signature.

    Raises:
        SignatureParameterError(TypeError): If inputs are of invalid types.
    """

    # 1. Validations
    if validate:
        validate_is_callable(function)
        validate_is_inspect_signature(signature)

    # 2. Define the wrapper with async support
    # Must match the nature of the original function (sync vs async)
    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            return await function(*args, **kwargs)
        wrapper = async_wrapper
    else:
        @wraps(function)
        def sync_wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        wrapper = sync_wrapper

    # 3. Assign the custom signature
    # This attribute is recognized by inspect.signature()
    wrapper.__signature__ = signature

    # 4. Return the transparent wrapper
    return wrapper


_DESIGN_NOTES = """
# apply_signature_to_wraps

## Purpose
The core engine for creating signature-aware wrappers. Ensures that function
metadata is preserved via `@wraps` while a new `__signature__` is injected.

## Where it is used
- Called by `create_signature_decorator()` to wrap functions during decoration.
- Used by decorator implementations to apply custom signatures to callables.
- Foundation for async-aware signature wrapping throughout the library.

## Async Awareness (Critical Design Feature)
A standard synchronous wrapper would fail if applied to an `async def` function
— it would return a coroutine without awaiting it. This implementation uses
`inspect.iscoroutinefunction()` to branch the wrapper logic:
- **Async functions**: Wrapped in an `async def` wrapper with `await`.
- **Sync functions**: Wrapped in a standard `def` wrapper.

This dual-path design ensures:
- Full compatibility with asyncio and modern async frameworks.
- Transparent behavior — async functions remain async, sync remain sync.
- Proper awaiting of coroutines — no silent bugs from forgotten await.

## Metadata Preservation
By using `functools.wraps`, we copy `__name__`, `__doc__`, `__annotations__`,
and other attributes from the original function. Explicitly setting
`__signature__` afterwards ensures our customized signature takes precedence
over the original during introspection.

## Wrapping Strategy
The wrapper function is intentionally simple:
- No argument modification or inspection.
- No exception handling or logging.
- Direct delegation to the original function.

This transparency ensures:
- Behavior is unchanged; only the reported signature differs.
- Stack traces remain clean.
- Performance impact is minimal (single function call overhead).

## How inspect.Signature Works
When `inspect.signature(wrapper)` is called:
1. Python checks for `wrapper.__signature__`.
2. If present, it returns that value immediately.
3. If absent, it introspects the function's code and annotations.

By setting `__signature__`, we provide a "fast path" for signature inspection.

## Notes
- Validation is performed upfront to ensure we don't wrap invalid objects.
- The resulting wrapper is "transparent" — it looks and behaves like the
  original function to most tools, but reports the injected signature.
- Both sync and async wrappers are indistinguishable in behavior except for
  their coroutine nature.
"""