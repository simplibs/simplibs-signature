from typing import Any, Iterable
# Outers
from ..exceptions import SignatureParameterError


def validate_excluded_names(
    value: Any,
    value_name: str = "excluded_names"
) -> tuple[str, ...]:
    """
    Validates that excluded_names is an iterable of strings and returns it as a tuple.

    Args:
        value:      The value to verify (expected Iterable[str]).
        value_name: The name of the parameter for error messages.

    Returns:
        A tuple of strings.

    Raises:
        SignatureParameterError(TypeError): If input is not iterable, is a string,
                                            or contains non-strings.
    """

    # 1. Check for basic iterable type, but EXCLUDE strings
    # We exclude strings because iterating over a string 'abc' yields ['a', 'b', 'c']
    if isinstance(value, str) or not isinstance(value, Iterable):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = f"{value_name}",
            value       = value,
            expected    = "an iterable of strings (e.g. list, tuple, or set)",
            problem     = (
                f"'{value_name}' must be an iterable of strings, "
                f"but got {type(value).__name__!r}."
            ),
            how_to_fix  = (
                f"Pass a collection of parameter names: {value_name}=['param1', 'param2']",
                "If you have only one name, wrap it in a list or tuple: ['name']",
                "To exclude nothing, pass an empty collection or None (if handled by caller).",
            ),
            exception    = TypeError,
        )

    # 2. Materialize to tuple and check each item type
    temp_list = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise SignatureParameterError(
                error_name  = "INVALID ARGUMENT ERROR",
                value_label = f"{value_name}[{i}]",
                value       = item,
                expected    = "a string (parameter name)",
                problem     = (
                    f"All items in {value_name} must be strings. "
                    f"Item at index {i} is {type(item).__name__!r}."
                ),
                how_to_fix  = (
                    "Ensure every item in the collection is a string.",
                    f"Correct the item at index {i}: {item!r}",
                ),
                exception    = TypeError,
            )
        temp_list.append(item)

    return tuple(temp_list)


_DESIGN_NOTES = """
# validate_excluded_names

## Purpose
Validates the `excluded_names` argument. Ensures the input is an iterable 
collection of strings and converts it into a stable `tuple`.

## Input Flexibility (Iterable Support)
The function now accepts any `Iterable` (list, set, tuple, generator) except 
for raw strings. This prevents the common "String Trap" where passing "abc" 
would be interpreted as three separate parameters ['a', 'b', 'c'].

## Why Materialize to Tuple?
1. **Stability**: Ensures that if a generator is passed, it is exhausted and 
   stored during validation, making the data safe for multiple downstream passes.
2. **Predictability**: The rest of the library can rely on a consistent `tuple` type.
3. **Immutability**: A tuple signals that these names are fixed configuration.

## Validation Steps
1. **Container Check**: Rejects non-iterables and raw strings.
2. **Item Check**: Iterates through the collection, verifying each item is a `str`.
3. **Conversion**: Returns a clean `tuple[str, ...]`.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- Explicitly handles the "String Trap" by checking `isinstance(value, str)`.
"""