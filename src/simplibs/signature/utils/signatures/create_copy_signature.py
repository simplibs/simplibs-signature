import inspect
from typing import Callable
from simplibs.sentinels import UNSET, UnsetType
# Commons
from .._validations import validate_is_type
from ..constants import EXCLUDED, KWARGS
# Inners
from .get_signature import get_signature


def create_copy_signature(
    base_func: Callable,
    *,
    return_type: type | None | UnsetType = UNSET,
    normalize: bool = True,
    validate: bool = True
) -> inspect.Signature:
    """
    Creates a copy of inspect.Signature from the provided function or method.

    Optionally normalises the signature — removes self/cls and appends **kwargs.
    Optionally overrides or sets the return type.

    Args:
        base_func:   The function or method whose signature is to be copied.
        return_type: The return type of the signature. If UNSET, the original is preserved.
                     If None, the return annotation is removed.
        normalize:   If True, removes self/cls and appends **kwargs (default: True).
        validate:    If True, validates the input arguments (default: True).

    Returns:
        A copied and optionally modified inspect.Signature.

    Raises:
        SignatureParameterError(TypeError): If `base_func` is not callable.
        SignatureParameterError(TypeError): If `return_type` is not a type.
        SignatureBuildError(ValueError):    If the function's signature cannot be introspected.
    """

    # 1. Retrieve the signature from the function
    signature = get_signature(base_func, validate)

    # 2. Early return if no modifications are needed
    if not normalize and return_type is UNSET:
        return signature

    # 3. Prepare the parameter list
    parameters = list(signature.parameters.values())

    # 4. Remove the binding parameter if present
    if normalize and parameters and parameters[0].name in EXCLUDED:
        parameters = parameters[1:]

    # 5. Append **kwargs at the end
    if normalize:
        parameters.append(KWARGS)

    # 6. Process the return type
    # 6.1 If return_type is UNSET, return the signature with updated parameters only
    if return_type is UNSET:
        return signature.replace(parameters=parameters)

    # 6.2 If return_type is None, remove the return annotation (set to Signature.empty)
    if return_type is None:
        return_annotation = inspect.Signature.empty

    # 6.3 If return_type is a type, validate it and use it as the return annotation
    else:
        validate_is_type(return_type, "return_type")
        return_annotation = return_type

    # 7. Return the signature with updated parameters and return type
    return signature.replace(
        parameters=parameters,
        return_annotation=return_annotation,
    )


_DESIGN_NOTES = """
# create_copy_signature

## Purpose
Creates a modified copy of an `inspect.Signature` from a callable — the
central transformation step used when copying a signature from one function
to another. Handles three concerns in one pass: parameter extraction,
normalisation, and return type override.

## When it is called
- `signature_copy()` decorator — copies the signature of a method onto
  a wrapper, normalising it for external use.
- `create_signature_decorator()` — builds the signature applied to a
  decorated function.

## Processing flow
1. Retrieve the signature via `get_signature()` — all introspection errors
   are handled there and re-raised as `SignatureBuildError`.
2. Early return if neither normalisation nor return type override is needed.
3. Extract parameters as a mutable list.
4. Remove the binding parameter (`self` / `cls`) if present and `normalize=True`.
5. Append `**kwargs` at the end if `normalize=True`.
6. Process the return type — three cases:
   - `UNSET` → preserve the original return annotation.
   - `None`  → remove the return annotation (set to `inspect.Signature.empty`).
   - type    → validate and apply the new return annotation.
7. Return the updated signature with modified parameters and return annotation.

## What normalisation does
Normalisation strips the binding parameter (`self` or `cls`) and appends
`**kwargs`. This transforms a method signature into one suitable for a
standalone wrapper function — the caller does not need to pass `self`,
and `**kwargs` ensures extra arguments are always accepted.

## Why None is not validated in step 6.2
`None` is an explicit signal to remove the return annotation — it is a
valid intentional value, not a type error. Only actual type values need
to be validated.

## Notes
- `validate=False` is passed through to `get_signature()` — consistent with
  the library-wide pattern where internal calls skip redundant validation.
- The `EXCLUDED` constant defines which binding parameter names are recognised
  (`self`, `cls`). The `KWARGS` constant is the pre-built `**kwargs` parameter.
"""