import inspect
from typing import Callable
# Outers
from ..core.validators import validate_is_inspect_signature
# Inners
from .builders import create_signature_decorator


def signature_set(
    signature: inspect.Signature,
    *,
    validate: bool = True
) -> Callable:
    """
    A decorator factory that assigns a pre-existing Signature to a function.

    Provides a clean, declarative way to attach an `inspect.Signature` instance
    to a callable without any further modifications. Acts as a high-level
    decorator wrapper around `set_signature()`.

    Args:
        signature:  The pre-constructed signature instance to be applied.
        validate:   If True, ensures the input is a valid inspect.Signature.

    Returns:
        A decorator that applies the signature to the target function.

    Raises:
        SignatureParameterError(TypeError): If `signature` is not an inspect.Signature.
    """

    # 1. Validations
    if validate:
        validate_is_inspect_signature(signature)

    # 2. Create and return the decorator
    # Uses existing infrastructure to handle wrapping and async/sync detection
    return create_signature_decorator(signature, validate=True)


_DESIGN_NOTES = """
# signature_set

## Purpose
A specialized, lightweight decorator for the final stage of signature management.
It is designed for cases where a signature has already been fully constructed 
(e.g., via `create_signature` or `compose_signature`) and simply needs to 
be attached to a function definition.

## Where it is used
- When signatures are defined as constants or shared across multiple functions.
- In scenarios where the signature logic is decoupled from the function 
  implementation (e.g., external schema-driven API generation).
- As a cleaner alternative to: `func.__signature__ = sig`

## Naming Consistency
The name `signature_set` was chosen to align with:
1. The decorator prefix convention (`signature`, `signature_copy`).
2. Its functional counterpart `set_signature(func, sig)`.

## Integration with create_signature_decorator
Instead of manually setting `__signature__`, this decorator utilizes 
`create_signature_decorator`. This ensures that:
- The target function is properly wrapped using `functools.wraps`.
- The nature of the function (async vs. sync) is respected.
- The assignment is handled consistently with the rest of the library.

## No-Transformation Guarantee
Unlike `signature` or `signature_copy`, this decorator performs zero 
modifications to the provided signature. It is a "pure" assignment tool.

## Validation Strategy
- **Factory Stage**: Validates that the provided object is indeed a 
  valid `inspect.Signature` instance.
- **Decoration Stage**: The internal `create_signature_decorator` validates 
  that the object being decorated is a callable.

## Usage Examples
```python
# Use a pre-defined signature for multiple functions
API_SIG = create_signature(
    create_keyword_parameter('token', annotation=str),
    return_source=dict
)

@signature_set(API_SIG)
def get_data(token):
    ...

@signature_set(API_SIG)
def delete_data(token):
    ...
```

## Performance Characteristics
- **Efficiency**: Extremely high, as it bypasses the `ParameterCollector` 
  and all merging logic. It only involves a single validation and 
  function wrapping.
"""