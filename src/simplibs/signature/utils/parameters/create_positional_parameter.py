import inspect
from typing import Any
# Commons
from .._validations import validate_is_string, validate_is_type


def create_positional_parameter(
    name: str,
    annotation: type = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    *,
    positional_only: bool = False,
    validate: bool = True
) -> inspect.Parameter:
    """
    Creates an inspect.Parameter for a positional argument.

    Optionally as POSITIONAL_ONLY (cannot be passed by name)
    or POSITIONAL_OR_KEYWORD (can be passed both ways).

    Args:
        name:           The parameter name.
        annotation:     Type annotation. If not provided, the parameter has no annotation.
        default:        Default value. If not provided, the parameter has no default.
        positional_only: If True, creates a POSITIONAL_ONLY parameter (default: False).
        validate:       If True, validates the input arguments (default: True).

    Returns:
        inspect.Parameter with kind POSITIONAL_ONLY or POSITIONAL_OR_KEYWORD.

    Raises:
        SignatureParameterError(TypeError): If `name` is not a str.
        SignatureParameterError(TypeError): If `annotation` is not a type.
    """

    # 1. Validate input values
    if validate:
        validate_is_string(name, "name")
        if annotation is not inspect.Parameter.empty:
            validate_is_type(annotation, "annotation")

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
Covers two kinds — `POSITIONAL_ONLY` and `POSITIONAL_OR_KEYWORD` — controlled
by the `positional_only` flag.

## When it is called
Used wherever a positional parameter needs to be created programmatically —
for example when building a signature from scratch via `SignatureCreator`.

## Parameter kinds
- `POSITIONAL_OR_KEYWORD` (default) — can be passed both positionally and
  by name. The most common kind for regular function parameters.
- `POSITIONAL_ONLY` — can only be passed positionally, not by name.
  Equivalent to parameters before `/` in a function signature.

## Why annotation is only validated when provided
`inspect.Parameter.empty` is a sentinel — it signals the absence of an
annotation, not a type. Validating it as a type would incorrectly reject
a legitimate "no annotation" call. The check is therefore skipped when
the default sentinel is passed.

## Notes
- `validate=False` skips both input checks — used for internal calls where
  inputs are already known to be valid.
- `default` is passed through without validation — `inspect.Parameter`
  accepts any value as a default.
"""