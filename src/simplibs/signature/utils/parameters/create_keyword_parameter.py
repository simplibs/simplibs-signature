import inspect
from typing import Any
# Commons
from .._validations import validate_is_string, validate_is_type


def create_keyword_parameter(
    name: str,
    annotation: type = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    *,
    validate: bool = True
) -> inspect.Parameter:
    """
    Creates an inspect.Parameter for a keyword argument.

    A KEYWORD_ONLY parameter can only be passed by name —
    it is placed after *args in the signature.

    Args:
        name:       The parameter name.
        annotation: Type annotation. If not provided, the parameter has no annotation.
        default:    Default value. If not provided, the parameter has no default.
        validate:   If True, validates the input arguments (default: True).

    Returns:
        inspect.Parameter with kind KEYWORD_ONLY.

    Raises:
        SignatureParameterError(TypeError): If `name` is not a str.
        SignatureParameterError(TypeError): If `annotation` is not a type.
    """

    # 1. Validate input values
    if validate:
        validate_is_string(name, "name")
        if annotation is not inspect.Parameter.empty:
            validate_is_type(annotation, "annotation")

    # 2. Create and return the parameter
    return inspect.Parameter(
        name = name,
        kind = inspect.Parameter.KEYWORD_ONLY,
        default = default,
        annotation = annotation,
    )


_DESIGN_NOTES = """
# create_keyword_parameter

## Purpose
A convenience factory for creating `KEYWORD_ONLY` `inspect.Parameter` instances.
The keyword-only counterpart to `create_positional_parameter()` — together they
cover all parameter kinds needed for programmatic signature construction.

## When it is called
Used wherever a keyword-only parameter needs to be created programmatically —
for example when building a signature from scratch via `SignatureCreator`.

## Parameter kind
- `KEYWORD_ONLY` — can only be passed by name, never positionally.
  Equivalent to parameters after `*` or `*args` in a function signature.

## Why annotation is only validated when provided
`inspect.Parameter.empty` is a sentinel — it signals the absence of an
annotation, not a type. Validating it as a type would incorrectly reject
a legitimate "no annotation" call. The check is therefore skipped when
the default sentinel is passed.

## Notes
- Simpler than `create_positional_parameter()` — no `kind` resolution needed,
  always produces `KEYWORD_ONLY`.
- `validate=False` skips both input checks — used for internal calls where
  inputs are already known to be valid.
- `default` is passed through without validation — `inspect.Parameter`
  accepts any value as a default.
"""