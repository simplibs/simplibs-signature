import inspect
from typing import Any
# Outers
from ..exceptions import SignatureParameterError


def validate_parameters_collection(
    value: Any,
    value_name: str = "parameters"
) -> tuple[inspect.Parameter, ...]:
    """
    Validates that the input is an iterable of inspect.Parameter objects
    and converts it into a tuple.

    Args:
        value:      The iterable collection of parameters to verify.
        value_name: The name of the argument used in error messages.

    Returns:
        A tuple containing only inspect.Parameter instances.

    Raises:
        SignatureParameterError(TypeError): If input is not iterable or
                                            contains non-Parameter objects.
    """

    # 1. Attempt conversion to tuple (Handling iterables/generators)
    try:
        params_tuple = tuple(value)
    except TypeError as e:
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "an iterable collection (list, tuple, etc.)",
            problem     = f"'{value_name}' must be iterable, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Ensure you are passing a collection of parameters: {value_name}=[p1, p2]",
                "Common sources include lists, tuples, or inspect.signature(f).parameters.values().",
            ),
            exception    = e,
        ) from e

    # 2. Check each item type within the materialized tuple
    for index, param in enumerate(params_tuple):
        if not isinstance(param, inspect.Parameter):
            raise SignatureParameterError(
                error_name  = "INVALID PARAMETER ITEM",
                value_label = f"{value_name}[{index}]",
                value       = param,
                expected    = "an instance of inspect.Parameter",
                problem     = (
                    f"Item at index {index} is not an inspect.Parameter object, "
                    f"but {type(param).__name__!r}."
                ),
                how_to_fix  = (
                    "Ensure all items in the collection are inspect.Parameter instances.",
                    "Use factory functions like create_keyword_parameter() to build them.",
                ),
                exception    = TypeError,
            )

    # 3. Return the sanitized tuple
    return params_tuple


_DESIGN_NOTES = """
# validate_parameters_collection

## Purpose
Acts as a "sanitizer" and validator at API boundaries. It ensures that any 
iterable input (lists, generators, dict_values) is safely converted into an 
immutable tuple of `inspect.Parameter` objects before entering the core logic.

## Why return a tuple?
1. **Safety against exhaustion**: If a user passes a generator or a map object, 
   iterating over it during validation would exhaust it. By converting to a 
   tuple first, we ensure the data is preserved for the actual signature construction.
2. **Immutability**: Once validated, the collection should not be modified by 
   external references (e.g., if a user passed a list and later appended to it).
3. **Compatibility**: `inspect.Signature` internally expects a sequence. Providing 
   a tuple is the most performant and stable way to interact with it.

## Design Shift (From Strict Tuple to Iterable)
We moved from requiring an explicit `tuple` to accepting any `Iterable`. This 
significantly reduces cognitive load for the user, as they no longer need to 
manually wrap `sig.parameters.values()` or list comprehensions in `tuple()`.

## Validation Steps
1. **Materialization**: Convert input to `tuple`. Catch `TypeError` if not iterable.
2. **Type Enforcement**: Loop through the tuple and verify `isinstance(param, Parameter)`.
3. **Return**: Pass the sanitized tuple back to the caller.

## Error Reporting
- **Contextual**: Uses `value_name` to make error messages specific to the call site.
- **Precise**: Identifies the exact index of a failing parameter.

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