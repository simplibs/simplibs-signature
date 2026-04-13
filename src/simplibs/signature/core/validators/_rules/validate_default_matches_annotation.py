from typing import Any
import inspect
# Outers
from ..exceptions import SignatureParameterError


def validate_default_matches_annotation(
    default_value: Any,
    annotation: Any,
) -> None:
    """
    Light validation of a default value against its annotation.

    This validation is **only performed for deterministic cases**:
        - `default_value` is provided and is not None
        - `annotation` is a concrete type (class)
        - Skips complex typing hints like Union, Any, Optional, etc.

    Args:
        default_value: The value to verify.
        annotation: Annotation against which verification will be performed.

    Raises:
        SignatureParameterError(TypeError): if the default value does not match
            the type annotation in deterministic cases.
    """

    # 1. Skip validation if nothing to check or annotation not suitable
    if (
        default_value in (inspect.Parameter.empty, None)
        or annotation in (inspect.Parameter.empty, Any)
    ):
        return  # Nothing deterministic to validate

    if isinstance(annotation, type):
        if not isinstance(default_value, annotation):
            raise SignatureParameterError(
                error_name  = "INVALID DEFAULT VALUE",
                value_label = "default for parameter",
                value       = default_value,
                expected    = f"value of type {annotation.__name__}",
                problem     = f"The default value does not match its annotation {annotation.__name__!r}.",
                how_to_fix  = (
                    f"Provide a default value of type {annotation.__name__}.",
                    "If unsure, remove the default or adjust the annotation.",
                ),
                exception    = TypeError,
            )


_DESIGN_NOTES = """
# validate_default_matches_annotation

## Purpose
Provides lightweight validation of default values in parameter creation utilities.
Only performs checks in deterministic cases where both a type and value are
concrete enough to be safely validated.

## Where it is used
- `create_positional_parameter()` — validates defaults before creating positional params.
- `create_keyword_parameter()` — validates defaults before creating keyword params.

## Scope
- This validation does **not aim to validate all possible defaults**.
- It is complementary, meant to catch clear mismatches where the user provides
  both a concrete type annotation and a default value.
- Complex type hints (`Union`, `Any`, `Optional`), `None`, or missing values
  are intentionally ignored.

## Why This Approach?
1. **Avoid false positives** for generic typing hints.
2. **Keep parameter creation fast and flexible**.
3. **Provide helpful feedback** for obvious mismatches without restricting
   valid but complex Python typing patterns.

## Validation Flow
1. Skip checks if default is None or empty, or if annotation is empty or Any.
2. Check type only if annotation is a concrete class (via `isinstance(annotation, type)`).
3. Raise `SignatureParameterError` with detailed message if mismatch is found.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- This function is intentionally permissive — it validates only when confident.
- Used internally by parameter factories, can be reused elsewhere for light validation.
"""