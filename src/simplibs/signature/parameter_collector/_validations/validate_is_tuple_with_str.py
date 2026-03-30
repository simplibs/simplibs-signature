# Commons
from ...utils import SignatureParameterError


def validate_is_tuple_with_str(value, value_name: str) -> None:
    """
    Validates that the provided value is a tuple containing only strings.

    Usage:
        - ParameterCollector.__init__() — validates the `excluded_names` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not a tuple.
        SignatureParameterError(TypeError): If any item in the tuple is not a str.
    """
    if not isinstance(value, tuple):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a tuple of strings, e.g. ('self', 'cls', 'my_param')",
            problem     = f"'{value_name}' must be a tuple, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Wrap the value in a tuple: {value_name}=('param1', 'param2').",
                "If you have a single name, use a one-element tuple: ('param_name',).",
                "If you want to exclude nothing, pass None instead.",
            ),
            get_location = 2,
            context      = "ParameterCollector.__init__() — excluded_names type check",
            exception    = TypeError,
        )

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise SignatureParameterError(
                error_name  = "INVALID ARGUMENT ERROR",
                value_label = f"{value_name}[{i}]",
                value       = item,
                expected    = "a string (parameter name)",
                problem     = f"All items in '{value_name}' must be strings, but item at index {i} is {type(item).__name__!r}.",
                how_to_fix  = (
                    "Make sure every item in the tuple is a string (parameter name).",
                    f"Example: {value_name}=('self', 'cls', 'my_param')",
                    f"Got invalid item at index {i}: {item!r}",
                ),
                get_location = 2,
                context      = f"ParameterCollector.__init__() — excluded_names items type check",
                exception    = TypeError,
            )


_DESIGN_NOTES = """
# validate_is_tuple_with_str

## Purpose
Validates that the provided value is a tuple containing only strings.
Used in `ParameterCollector.__init__()` to guard the `excluded_names` parameter
— a list of parameter names that should be skipped during collection.

## When it is called
- `ParameterCollector.__init__()` — `excluded_names` parameter

## Checks
1. Verifies that the value is a `tuple` — fails fast if not.
2. Iterates over all items and checks each one individually — reports
   the exact index and value of the first invalid item found.

## Notes
- `context` is kept in both raises — it points to the exact location and
  parameter within `ParameterCollector.__init__()`, which is not obvious
  from the function name alone.
- `get_location=2` points the error to the caller's call site.
"""