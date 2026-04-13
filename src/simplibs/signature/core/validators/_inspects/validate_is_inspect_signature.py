import inspect
from typing import Any
# Outers
from ..exceptions import SignatureParameterError


def validate_is_inspect_signature(
    value: Any,
    value_name: str = "signature"
) -> None:
    """
    Validates that the provided value is an instance of inspect.Signature.

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

    Raises:
        SignatureParameterError(TypeError): If the value is not an inspect.Signature.
    """
    if not isinstance(value, inspect.Signature):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "an instance of inspect.Signature",
            problem     = f"'{value_name}' must be inspect.Signature, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a valid inspect.Signature object as '{value_name}'.",
                "You can obtain one via: inspect.signature(my_func).",
                "Or use SignatureCreator(...).signature from this library.",
            ),
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_inspect_signature

## Purpose
Validates that the provided value is an `inspect.Signature` instance.
Ensures that we are not trying to apply an invalid object as a function signature.

## Where it is used
- `add_params_to_signature()` — validates the base signature before modification.
- `replace_return_annotation_in_signature()` — validates the signature being modified.
- `delete_params_from_signature()` — validates the signature being modified.
- `set_signature()` — validates the signature before applying to a callable.
- `create_signature_decorator()` — validates the signature to decorate with.
- `apply_signature_to_wraps()` — validates the signature in decorator context.

## Validation Method
Simple `isinstance` check — rejects anything that is not a proper `inspect.Signature`.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
"""