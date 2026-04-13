from typing import Any
# Outers
from ..exceptions import SignatureParameterError


def validate_is_bool(
    value: Any,
    value_name: str
) -> None:
    """
    Validates that the provided value is of type bool.

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

    Raises:
        SignatureParameterError(TypeError): If the value is not a bool.
    """
    if not isinstance(value, bool):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a boolean value: True or False",
            problem     = f"'{value_name}' must be a bool, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a boolean value: {value_name}=True or {value_name}=False.",
                "Do not pass strings ('true'), integers (1/0) or other non-bool values.",
            ),
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_bool

## Purpose
Validates that the provided value is a bool — used wherever a parameter
must be strictly True or False, with no implicit conversion.

## Where it is used
- `ParameterCollector.__init__()` — validates `get_location` parameter.
- `SignatureCreator.__init__()` — validates `normalize` and `validate` parameters.
- `copy_signature()` — validates `normalize` and `validate` parameters.
- `add_params_to_signature()` — validates configuration bool flags.
- `@signature` decorator — validates bool parameters at decoration time.
- `@signature_copy` decorator — validates bool parameters at decoration time.

## Validation Method
Uses `isinstance` — strictly rejects integers (1/0), strings ('true'), and all
other non-bool values. No implicit conversion is performed.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- Boolean parameters control critical behavior (normalization, validation),
  so strict typing prevents subtle bugs.
"""