import inspect
from typing import Any
# Outers
from ...validators import validate_is_inspect_signature


def replace_return_annotation_in_signature(
    signature: inspect.Signature,
    new_return_annotation: Any,
    *,
    validate: bool = True
) -> inspect.Signature:
    """
    Creates a new signature by replacing the return annotation of an existing one.

    Args:
        signature:             The source signature to modify.
        new_return_annotation: The new return type (type, string, or inspect.Signature.empty).
        validate:              If True, validates that 'signature' is a valid Signature object.

    Returns:
        A new inspect.Signature instance with the updated return annotation.

    Raises:
        SignatureParameterError(TypeError): If the input signature is not a valid inspect.Signature.
    """

    # 1. Validations
    if validate:
        validate_is_inspect_signature(signature)

    # 2. Create and return a new signature with updated return annotation
    return signature.replace(return_annotation=new_return_annotation)


_DESIGN_NOTES = """
# replace_return_annotation_in_signature

## Purpose
A specialized utility for updating the return type hint (annotation) of a
given signature without modifying its parameters. Provides a focused interface
for return annotation management.

## Where it is used
- User-facing utility for updating function return types.
- Used internally by `SignatureCreator` when applying return annotations.
- Foundation for return type customization in decorators and transformations.

## Implementation: The replace() Method
We leverage the built-in `inspect.Signature.replace()` method, designed
specifically for creating shallow copies with selective attribute overrides.
This ensures:
- The original signature object remains immutable.
- Only the return annotation is modified.
- All parameters are preserved exactly as-is.

## Validation Consistency
Even though the logic is simple, we apply `validate_is_inspect_signature()`.
This maintains consistency across the library: every user-facing function
validates its inputs and provides standardized, clear error messages.

## Handling "Empty" Annotations
In Python's `inspect` module, a missing return annotation is represented by
`inspect.Signature.empty`. This function naturally supports resetting an
annotation by passing this constant as `new_return_annotation`.

## Supported Annotation Types
`new_return_annotation` accepts any value:
- Type objects: `int`, `str`, `MyClass`
- Generic types: `list[str]`, `dict[str, int]` (Python 3.9+)
- String forward references: `"MyClass"` (PEP 563)
- Custom objects: Any value can be stored and retrieved
- Special value: `inspect.Signature.empty` to remove an annotation

## Notes
- `validate=False` is provided for internal performance optimization where
  the signature type has already been verified by a caller.
- The original `signature` is never modified — immutability is preserved.
- This function is intentionally simple — it delegates to `inspect.Signature`
  which handles all annotation compatibility.
"""