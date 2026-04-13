import inspect
from typing import Any, Iterable
# Outers
from ...validators import SignatureBuildError, validate_parameters_collection


def compose_signature(
    parameters: Iterable[inspect.Parameter],
    return_annotation: Any = inspect.Signature.empty,
    *,
    validate: bool = True,
) -> inspect.Signature:
    """
    Creates an inspect.Signature from a collection of parameters and a return annotation.

    Args:
        parameters:        An iterable collection of inspect.Parameter instances
                           (e.g., tuple, list, or dict_values).
        return_annotation: The return type annotation. Defaults to empty.
        validate:          If True, validates the input parameters and converts
                           them to a tuple before construction.

    Returns:
        inspect.Signature with the provided parameters and return annotation.

    Raises:
        SignatureParameterError(TypeError): If parameters are not iterable or
                                            contain non-Parameter objects (when validate=True).
        SignatureBuildError(ValueError):    If a parameter structure is invalid (e.g. duplicate names).
        SignatureBuildError(AttributeError): If items in the collection are missing required
                                             Parameter attributes.
        SignatureBuildError(TypeError):     If inspect.Signature fails for other type reasons.
    """

    # 1. Validations and Sanitization
    # If validation is enabled, we sanitize the input by converting the iterable
    # to a guaranteed tuple of validated Parameter objects.
    if validate:
        parameters = validate_parameters_collection(parameters)

    # 2. Signature composition
    try:
        return inspect.Signature(
            parameters=parameters,
            return_annotation=return_annotation,
            __validate_parameters__=validate,  # CPython flag to skip redundant validation
        )

    # 3. Catching structural exceptions from inspect.Signature
    except ValueError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE COMPOSITION ERROR",
            value_label = "parameters",
            value       = parameters,
            expected    = "a collection of valid, uniquely named inspect.Parameter instances",
            problem     = "One or more parameters are structurally invalid (e.g. duplicates or wrong order).",
            how_to_fix  = (
                "Ensure all parameter names are unique.",
                "Check that order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
                "Verify that each parameter is a valid inspect.Parameter instance.",
            ),
            context      = "inspect.Signature() — invalid parameter structure",
            exception    = e,
        ) from e

    except AttributeError as e:
        raise SignatureBuildError(
            error_name="SIGNATURE COMPOSITION ERROR",
            value_label="parameters",
            value=parameters,
            expected="a collection of inspect.Parameter instances",
            problem="One or more items in the parameters collection are not valid Parameter objects.",
            how_to_fix=(
                "Ensure all items are created via inspect.Parameter() or our factory functions.",
                "Verify that you are not accidentally passing strings or other objects.",
            ),
            context="inspect.Signature() — duck typing failed (missing .name)",
            exception=e,
        ) from e

    except TypeError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE COMPOSITION ERROR",
            value_label = "parameters",
            value       = parameters,
            expected    = "an iterable of inspect.Parameter instances",
            problem     = "The parameters collection or return_annotation is of an unsupported type.",
            how_to_fix  = (
                "Ensure all items in the parameters collection are inspect.Parameter instances.",
                "Use create_keyword_parameter() and create_positional_parameter() to construct parameters.",
                "If validate=False, ensure the input is a valid sequence or mapping.",
            ),
            context      = "inspect.Signature() — type mismatch during construction",
            exception    = e,
        ) from e


_DESIGN_NOTES = """
# compose_signature

## Purpose
A factory for creating `inspect.Signature` instances from scratch. Serves as
the primary entry point for signature construction within the library, providing
structured error handling and optional pre-validation.

## Input Flexibility (Iterable Support)
The function now accepts any `Iterable[inspect.Parameter]`. This allows users to 
pass lists, generators, or results from `sig.parameters.values()` directly. 

## The Validation Logic
- **validate=True**: The input is passed to `validate_parameters_collection()`, which 
  materializes any iterable into a `tuple` and verifies every item. The local 
  `parameters` variable is overwritten with this sanitized tuple.
- **validate=False**: No conversion or check is performed. The input is passed 
  directly to `inspect.Signature`. This is intended for internal library calls 
  where data is already known to be valid, or for power users who want to 
  avoid the performance overhead of re-validation.

## Failure Modes
- `ValueError` -> Structural issues (duplicates, invalid order) caught by `inspect`.
- `AttributeError` -> One or more items are not valid Parameter objects 
  (duck typing failed during internal initialization).
- `TypeError` -> Type issues (unsupported annotation types or collection mismatch).

## The __validate_parameters__ Flag
This is an undocumented but stable CPython parameter controlling whether
`inspect.Signature` performs structural validation:
- `validate=True` -> flag is `True` -> full structural checks run.
- `validate=False` -> flag is `False` -> skips redundant internal checks. 

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