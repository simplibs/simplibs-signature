import inspect
from typing import Any
# Outers
from ...validators import validate_is_string, validate_default_matches_annotation


def create_positional_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    positional_only: bool = False,
    validate: bool = True
) -> inspect.Parameter:
    """
    Creates an inspect.Parameter for a positional argument.

    Optionally as POSITIONAL_ONLY (cannot be passed by name)
    or POSITIONAL_OR_KEYWORD (can be passed both ways).

    Args:
        name:            The parameter name.
        annotation:      Type annotation or any metadata. Defaults to empty.
        default:         Default value. Defaults to empty.
        positional_only: If True, creates a POSITIONAL_ONLY parameter.
        validate:        If True, validates the 'name' argument.

    Returns:
        inspect.Parameter with kind POSITIONAL_ONLY or POSITIONAL_OR_KEYWORD.

    Raises:
        SignatureParameterError(TypeError): If `name` is not a str.
    """

    # 1. Validations
    if validate:
        validate_is_string(name)
        validate_default_matches_annotation(default, annotation)

    # 2. Resolve the parameter kind
    kind = (
        inspect.Parameter.POSITIONAL_ONLY
        if positional_only
        else inspect.Parameter.POSITIONAL_OR_KEYWORD
    )

    # 3. Create and return the parameter
    return inspect.Parameter(
        name = name,
        kind = kind,
        default = default,
        annotation = annotation,
    )


_DESIGN_NOTES = """
# create_positional_parameter

## Purpose
A convenience factory for creating positional `inspect.Parameter` instances.
Supports both `POSITIONAL_ONLY` and `POSITIONAL_OR_KEYWORD` kinds, allowing
flexible creation of positional parameters for signature construction.

## Parameter Kinds
- `POSITIONAL_OR_KEYWORD` (default) — can be passed both positionally and by name.
  Standard behavior for most Python parameters.
- `POSITIONAL_ONLY` — can only be passed positionally. Equivalent to parameters
  appearing before `/` in a function signature.

## Where it is used
- Direct user-facing utility for building custom signatures.
- Used internally by `SignatureCreator` when processing parameter sources.
- Commonly paired with `create_keyword_parameter()` for mixed-kind signatures.

## Validation Behavior
When `validate=True`:
1. `name` validation — ensures the parameter name is a string.
2. `default` validation — **only in deterministic cases** where both `default`
   and `annotation` are concrete types. Uses `isinstance` to verify the default
   matches the annotation.

Complex type hints (`Union`, `Any`, `Optional`), `None`, or missing values are
intentionally ignored. This validation is a lightweight safeguard meant to catch
obvious mismatches without restricting valid but complex Python typing patterns.

## Notes
- `validate=False` skips both `name` and default validation.
- `default` uses `inspect.Parameter.empty` as the sentinel for "no default".
- The `positional_only` flag elegantly maps to the appropriate `kind`,
  making the API user-friendly for both parameter types.
- All other values and annotations are passed directly to `inspect.Parameter`
  without additional validation.
"""