import inspect
from typing import Iterable
# Outers
from ...parameter_collector import ParameterCollector
from ...validators import validate_is_inspect_signature, validate_excluded_names


def delete_params_from_signature(
    signature: inspect.Signature,
    excluded_names: Iterable[str],
    *,
    validate: bool = True
) -> inspect.Signature:
    """
    Creates a new signature by removing specified parameters from an existing one.

    Uses ParameterCollector to ensure the remaining parameters maintain their
    valid Python ordering and to filter out the unwanted names.

    Args:
        signature:      The source signature to modify.
        excluded_names: An iterable of parameter names (strings) to be removed.
        validate:       If True, performs input validation and sanitization.

    Returns:
        A new inspect.Signature instance without the excluded parameters.

    Raises:
        SignatureParameterError(TypeError): If inputs are of invalid types.
    """

    # 1. Validations and Sanitization
    if validate:
        validate_is_inspect_signature(signature)
        # Sanitizing excluded_names into a stable tuple
        excluded_names = validate_excluded_names(excluded_names)

    # 2. Initialize collector with exclusion rules
    collector = ParameterCollector(
        excluded_names=excluded_names,
        validate=False,  # Names already validated or sanitized above
    )

    # 3. Load signature parameters into the collector
    # The collector automatically skips any parameter with a name in excluded_names
    for param in signature.parameters.values():
        collector.add_param(param)

    # 4. Retrieve the filtered and ordered parameters
    new_params = collector.get_ordered_params()

    # 5. Construct and return the new signature
    # We use replace() to keep the original return_annotation and other metadata
    return signature.replace(parameters=new_params)


_DESIGN_NOTES = """
# delete_params_from_signature

## Purpose
A high-level utility designed to prune a signature by removing specific
parameters by their names. Maintains parameter ordering and structural validity.

## Input Flexibility (Iterable Support)
In line with the library-wide standard, `excluded_names` now accepts any 
`Iterable[str]`. Users can pass lists, sets, or even generators of names. 
The input is materialized into a `tuple` during validation to ensure 
stability when passed to the `ParameterCollector`.

## Implementation: Leveraging the Collector Pattern
Rather than manual list filtering, we reuse `ParameterCollector`. This brings
several architectural advantages:
1. **Consistency**: The logic for "excluded names" is centralized, ensuring 
   uniform behavior across the entire library.
2. **Safety**: The Collector ensures remaining parameters are returned in valid
   Python order, even after deletion.
3. **Simplicity**: The function remains a thin, maintainable wrapper.

## Behavior on Missing Names
If a name in `excluded_names` does not exist in the source signature, it is
silently ignored — providing a robust "ensure these are gone" semantic.

## Performance Note
Using a Collector guarantees structural integrity. For typical function
signatures, the overhead is negligible compared to the reliability gains 
of centralized parameter management.

## Notes
- The original `signature` is never modified — immutability is preserved.
- `validate=False` can be used for performance-critical internal loops where
  types are already guaranteed.
- Parameter order is always preserved in the output.
"""