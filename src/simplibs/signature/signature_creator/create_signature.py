import inspect
from typing import Callable
from simplibs.sentinels import UNSET, UnsetType
# Inners
from .SignatureCreator import SignatureCreator


def create_signature(
    *sources: inspect.Parameter | Callable,
    excluded_names: tuple[str, ...] = None,
    return_type: type | Callable | None | UnsetType = UNSET,
    base_func: Callable | None = None,
    base_func_first: bool = True,
    accept_double: bool = True,
) -> inspect.Signature:
    """
    Creates an inspect.Signature using SignatureCreator.

    A direct functional interface for SignatureCreator — accepts identical
    parameters and returns the assembled signature.

    Args:
        *sources:           Parameters or functions to add to the signature.
        excluded_names:  Parameter names to exclude from the signature.
        return_type:     The return type of the signature. If UNSET and
                         `base_func` is provided, its return type is used.
        base_func:       The base function whose parameters and return type
                         serve as the starting point.
        base_func_first: If True, `base_func` parameters come before `sources`.
        accept_double:   If True, duplicate parameter names are silently skipped.

    Returns:
        inspect.Signature assembled from the provided arguments.

    Raises:
        SignatureBuildError(ValueError): If neither `base_func` nor any
                                         `sources` were provided.
    """

    # 1. Create a SignatureCreator instance
    signature_instance = SignatureCreator(
        *sources,
        excluded_names = excluded_names,
        return_type = return_type,
        base_func = base_func,
        base_func_first = base_func_first,
        accept_double = accept_double,
    )

    # 2. Return the assembled signature
    return signature_instance.signature


_DESIGN_NOTES = """
# create_signature

## Purpose
A thin functional wrapper over `SignatureCreator` — accepts identical
parameters and returns the assembled `inspect.Signature` directly.
Exists for cases where the caller needs only the signature and has no
use for the `SignatureCreator` instance itself.

## Relationship to SignatureCreator
`create_signature` and `SignatureCreator` are two interfaces to the same
logic — choose based on what the call site needs:

| Use                  | When                                                    |
|----------------------|---------------------------------------------------------|
| `create_signature()` | Only the signature is needed — discard the builder      |
| `SignatureCreator`   | The instance is passed around or inspected further      |

## Why this function exists
The functional style is more natural at call sites where the signature
is consumed immediately — for example inside decorators or factory
functions. It also serves as a demonstration of how the library itself
eliminates parameter duplication: `create_signature` has no logic of
its own, it simply delegates.

## Notes
- All validation and error handling lives in `SignatureCreator` — this
  function sources no additional checks.
- The intermediate `signature_instance` variable is intentional — it
  makes the two-step flow (create → extract) explicit and readable.
"""