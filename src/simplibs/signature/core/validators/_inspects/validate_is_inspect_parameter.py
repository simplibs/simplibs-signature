import inspect
from typing import Any
# Outers
from ..exceptions import SignatureBuildError


def validate_is_inspect_parameter(
    value: Any,
    value_name: str = "param"
) -> None:
    """
    Validates that the provided value is an instance of inspect.Parameter.

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

    Raises:
        SignatureBuildError(TypeError): If the value is not an inspect.Parameter.
    """
    if not isinstance(value, inspect.Parameter):
        raise SignatureBuildError(
            error_name  = "INVALID PARAMETER TYPE",
            value_label = value_name,
            value       = value,
            expected    = "an instance of inspect.Parameter",
            problem     = f"Expected a proper inspect.Parameter object, but got {type(value).__name__!r}.",
            how_to_fix  = (
                "Ensure you are passing a valid 'inspect.Parameter' instance.",
                "Use 'inspect.Parameter(...)' or helper functions to create it.",
                "If you are iterating over an existing signature, use 'signature.parameters.values()'.",
            ),
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_inspect_parameter

## Purpose
Ensures that the input is a valid `inspect.Parameter` object. 
Prevents the collector from breaking when trying to access attributes like `.name`, `.kind` or `.default`.

## Where it is used
- `AddParamMixin.add_param()` — first line of the primary entry point.

## Validation Method
Simple `isinstance` check.

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