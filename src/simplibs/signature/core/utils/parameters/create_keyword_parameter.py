import inspect
from typing import Any
# Outers
from ...validators import validate_is_string, validate_default_matches_annotation


def create_keyword_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    validate: bool = True
) -> inspect.Parameter:
    """
    Creates an inspect.Parameter for a keyword-only argument.

    A KEYWORD_ONLY parameter can only be passed by name —
    it is placed after *args in the signature.

    Args:
        name:       The parameter name.
        annotation: Type annotation or any metadata. Defaults to empty.
        default:    Default value. Defaults to empty.
        validate:   If True, validates the 'name' argument.

    Returns:
        inspect.Parameter with kind KEYWORD_ONLY.

    Raises:
        SignatureParameterError(TypeError): If `name` is not a str.
    """

    # 1. Validations
    if validate:
        validate_is_string(name)
        validate_default_matches_annotation(default, annotation)

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
Used for building signatures programmatically, especially for parameters that
must be passed by name only.

## Parameter Kind
- `KEYWORD_ONLY` — can only be passed by name. Equivalent to parameters
  appearing after `*` or `*args` in a function signature (Python 3+).

## Where it is used
- Direct user-facing utility for building custom signatures.
- Used internally by `SignatureCreator` when processing parameter sources.
- Commonly paired with `create_positional_parameter()` for mixed-kind signatures.

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
- Unlike `create_positional_parameter()`, there is no configuration flag — the
  kind is always `KEYWORD_ONLY`.
- All other values and annotations are passed directly to `inspect.Parameter`
  without additional validation.
"""