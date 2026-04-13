import inspect
from typing import Any
# Outers
from ..exceptions import SignatureBuildError


def validate_accept_double(
    param: inspect.Parameter,
    accept_double: bool
) -> None:
    """
    Validates that a parameter name is not duplicated if duplicates are not allowed.

    Args:
        param: The inspect.Parameter instance being added.
        accept_double: Configuration flag indicating if duplicates are permitted.

    Raises:
        SignatureBuildError(ValueError): If the name exists and accept_double is False.
    """
    if not accept_double:
        raise SignatureBuildError(
            error_name  = "DUPLICATE PARAMETER ERROR",
            value_label = "param.name",
            value       = param.name,
            expected    = "a unique parameter name",
            problem     = f"Parameter '{param.name}' is already defined in this signature.",
            how_to_fix  = (
                f"Ensure that the parameter name '{param.name}' is unique within the signature.",
                "If you intend to overwrite existing parameters, set 'accept_double=True' in the collector.",
                "Check if you are accidentally adding the same source or function multiple times.",
            ),
            exception    = ValueError,
        )


_DESIGN_NOTES = """
# validate_accept_double

## Purpose
Acts as a strict guard against naming collisions. 
It allows the user to enforce a "unique names only" policy during signature construction.

## Where it is used
- `AddParamMixin.add_param()` — standard duplicate handling branch.
- `AddParamMixin._flat_params_to_kwargs()` — duplicate handling within the flat-to-kwargs transformation.

## Validation Method
Checks the `accept_double` flag. If `False`, it triggers an error because the caller 
already determined that `param.name` is present in `_seen_names`.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- This function is only called when a duplicate is actually detected.
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
"""