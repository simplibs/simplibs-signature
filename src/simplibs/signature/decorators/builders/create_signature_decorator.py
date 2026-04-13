import inspect
from typing import Callable
# Outers
from ...core.validators import validate_is_inspect_signature
# Inners
from .apply_signature_to_wraps import apply_signature_to_wraps


def create_signature_decorator(
    signature: inspect.Signature,
    *,
    validate: bool = True
) -> Callable:
    """
    Creates a decorator factory from an inspect.Signature.

    The resulting decorator, when applied to a function, wraps it in
    a signature-aware callable using apply_signature_to_wraps().

    Args:
        signature: The signature to be applied by the decorator.
        validate:  If True, validates the signature at creation time
                   and the function at decoration time.

    Returns:
        A decorator function ready to be applied to callables.

    Raises:
        SignatureParameterError(TypeError): If signature is not a valid inspect.Signature.
    """

    # 1. Validations
    if validate:
        validate_is_inspect_signature(signature)

    # 2. Define the decorator factory
    def decorator(function: Callable) -> Callable:
        return apply_signature_to_wraps(
            function  = function,
            signature = signature,
            validate  = validate,
        )

    # 3. Return the decorator
    return decorator


_DESIGN_NOTES = """
# create_signature_decorator

## Purpose
A higher-level factory that converts an `inspect.Signature` object into a
reusable Python decorator. Bridges the gap between signature objects and
decorator patterns.

## Where it is used
- User-facing API for creating decorators from custom signatures.
- Used internally by the `@signature` and `@signature_copy` decorators.
- Foundation for advanced signature-based metaprogramming patterns.

## Early vs Late Validation Strategy
This implementation uses "Early Validation" — the signature is validated
immediately when the decorator factory is called (step 1), not when the
decorator is applied to a function. Benefits:
- Invalid signatures are caught early with clear error messages.
- Prevents silent failures where a broken decorator is passed around.
- Fail-fast philosophy — errors occur at the point of declaration.

## Decorator Factory Pattern
The returned `decorator` function is a thin bridge:
```python
sig_dec = create_signature_decorator(my_signature)

@sig_dec  # Calls decorator(my_function)
def my_function(a, b):
    pass
```

The `decorator` inner function delegates all complex logic to
`apply_signature_to_wraps`, maintaining clean separation of concerns.

## Validation Flow
1. **Factory Creation**: Signature is validated (if `validate=True`).
2. **Decoration Time**: Function callability is checked (if `validate=True`).
3. **Wrapping**: `apply_signature_to_wraps` performs async detection and wrapping.

This two-stage validation catches errors at the appropriate time, providing
clear error messages for each stage.

## Reusability
The returned decorator is a true Python decorator — it can be applied to
multiple functions:
```python
my_decorator = create_signature_decorator(custom_sig)

@my_decorator
def func_1(x): pass

@my_decorator
def func_2(y): pass  # Same decorator, different function
```

## Async Compatibility
Because `create_signature_decorator` delegates to `apply_signature_to_wraps`,
it automatically handles both sync and async functions correctly.

## Usage Example
```python
# 1. Build a signature
sig = compose_signature(
    parameters=(param1, param2),
    return_annotation=int
)

# 2. Create a decorator from it
apply_custom_sig = create_signature_decorator(sig)

# 3. Use the decorator
@apply_custom_sig
async def my_async_function(a, b):
    return a + b

# inspect.signature(my_async_function) now returns 'sig'
```

## Notes
- The `validate` flag controls validation at both factory and decoration time.
- The decorator preserves the original function's metadata via `@wraps`.
- Works seamlessly with both synchronous and asynchronous functions.
- The signature is applied via `__signature__` attribute assignment.
"""