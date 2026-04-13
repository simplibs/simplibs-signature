import inspect
from typing import Iterable
# Outers
from ...parameter_collector import ParameterCollector
from ...validators import (
    SignatureBuildError,
    validate_is_inspect_signature,
    validate_parameters_collection,
    validate_is_bool
)


def add_params_to_signature(
    signature: inspect.Signature,
    params_to_add: Iterable[inspect.Parameter],
    *,
    accept_double: bool = True,
    replace_double: bool = True,
    flat_to_kwargs: bool = False,
    validate: bool = True
) -> inspect.Signature:
    """
    Creates a new signature by adding parameters to an existing one.

    The function maintains valid Python parameter order regardless of input order,
    utilizing ParameterCollector's internal logic.

    Args:
        signature:      The base signature to modify.
        params_to_add:  An iterable collection of inspect.Parameter instances to add.
        accept_double:  If False, name collisions raise SignatureBuildError.
        replace_double: If True, new parameters replace existing ones with the same name.
                        If False, existing parameters are kept.
        flat_to_kwargs: If True, transforms all parameters into KEYWORD_ONLY.
        validate:       If True, validates input types and converts params_to_add to a tuple.

    Returns:
        A new inspect.Signature instance with merged and ordered parameters.

    Raises:
        SignatureParameterError(TypeError): If inputs are of invalid types.
        SignatureBuildError(ValueError):    If the resulting signature structure is invalid.
        SignatureBuildError(TypeError):     If an unexpected type error occurs during reconstruction.
    """

    # 1. Validations and Sanitization
    if validate:
        validate_is_inspect_signature(signature)
        # We overwrite params_to_add with the sanitized tuple from validation
        params_to_add = validate_parameters_collection(params_to_add, "params_to_add")
        validate_is_bool(accept_double, "accept_double")
        validate_is_bool(replace_double, "replace_double")
        validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

    # 2. Initialize collector with duplicate handling rules
    params_collector = ParameterCollector(
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        validate=False,  # Parameters already validated or trusted
    )

    # 3. Load existing signature parameters into the collector
    for param in signature.parameters.values():
        params_collector.add_param(param)

    # 4. Add new parameters to the collector
    for param in params_to_add:
        params_collector.add_param(param)

    # 5. Get ordered parameters
    ordered_params = params_collector.get_ordered_params()

    # 6. Construct the new signature from ordered parameters
    try:
        return signature.replace(parameters=ordered_params)

    except ValueError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE STRUCTURE ERROR",
            value_label = "params_to_add",
            value       = params_to_add,
            expected    = "parameters that form a valid Python signature",
            problem     = "The resulting signature structure is invalid (e.g. duplicate variadic parameters or invalid order).",
            how_to_fix  = (
                "Ensure you are not adding a second *args or **kwargs parameter.",
                "Check if the combination of existing and new parameters violates Python rules.",
                "Verify parameter order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
            ),
            context      = "inspect.Signature.replace() — structural validation",
            exception    = e,
        ) from e

    except TypeError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE TYPE ERROR",
            value_label = "parameters",
            value       = ordered_params,
            expected    = "valid inspect.Parameter objects",
            problem     = "An unexpected type error occurred during signature reconstruction.",
            how_to_fix  = "Verify that all objects in params_to_add are proper inspect.Parameter instances.",
            context      = "inspect.Signature.replace() — type validation",
            exception    = e,
        ) from e


_DESIGN_NOTES = """
# add_params_to_signature

## Purpose
A high-level converter that extends an existing `inspect.Signature` with
new parameters while maintaining valid Python parameter ordering. Handles
parameter merging, deduplication, and structural validation transparently.

## Input Flexibility (Iterable Support)
Following the library-wide standard, `params_to_add` now accepts any `Iterable`. 
This allows passing lists, generators, or results from other signatures 
without manual casting.

## Implementation: The Collector Pattern
Delegates all parameter management to `ParameterCollector`:
1. Existing signature parameters are loaded first.
2. New parameters are merged according to `accept_double` and `replace_double` rules.
3. If `validate=True`, `params_to_add` is materialized into a tuple during 
   the validation phase to prevent iterator exhaustion.
4. Collector returns a flattened, correctly sorted tuple.
5. `signature.replace()` constructs the new signature from ordered parameters.

## Duplicate Handling
Two flags control name collisions during the merge:
- `accept_double=False` → Any name collision raises `SignatureBuildError`.
- `replace_double=True` (default) → New parameters overwrite existing ones.
- `replace_double=False` → New parameters are skipped; originals are kept.

## Parameter Ordering Guarantee
By routing all parameters through `ParameterCollector`, the function guarantees
that the resulting signature always respects Python's valid parameter order.

## Exception Handling
Specifically catches `ValueError` (structural issues) and `TypeError` (type issues)
from `signature.replace()`, wrapping them in `SignatureBuildError` for consistency.

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