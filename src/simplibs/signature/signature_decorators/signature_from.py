import inspect
from typing import Callable
from simplibs.sentinels import UNSET, UnsetType
# Commons
from ..signature_creator import create_signature
from ..utils import validate_is_callable
# Inners
from .utils import apply_signature_to_wraps


def signature_from(
    *sources: inspect.Parameter | Callable,
    excluded_names: tuple[str, ...] = None,
    return_type: type | Callable | None | UnsetType = UNSET,
    base_func_first: bool = True,
    accept_double: bool = True,
) -> Callable:
    """
    Decorator that assembles an inspect.Signature from the provided parameter sources.

    The decorated function is used as base_func — its parameters form the
    base of the signature, to which parameters from `sources` are appended.
    Order depends on `base_func_first`.

    Args:
        *sources:           Parameters or functions to add to the signature.
        excluded_names:  Parameter names to be excluded from the signature.
        return_type:     The return type of the signature. If UNSET and a base_func
                         is provided, its return type is used.
        base_func_first: If True, the decorated function's parameters come before
                         those from sources (default: True).
        accept_double:   If True, allows parameters with the same name (default: True).

    Returns:
        A decorator that applies the assembled signature to a function.

    Raises:
        SignatureParameterError(TypeError): If the decorated object is not callable.
        SignatureBuildError(ValueError):    If SignatureCreator cannot assemble the signature.

    Example:
        @signature_from(my_param, base_func_first=False)
        def my_func(*args, **kwargs):
            ...
    """

    # 1. Define the decorator
    def decorator(function: Callable) -> Callable:

        # 1.1 Validate the function
        validate_is_callable(function, "function")

        # 1.2 Assemble the signature
        signature = create_signature(
            *sources,
            excluded_names  = excluded_names,
            return_type     = return_type,
            base_func       = function,
            base_func_first = base_func_first,
            accept_double   = accept_double,
        )

        # 1.3 Create and return the wrapper
        return apply_signature_to_wraps(
            function  = function,
            signature = signature,
            validate  = False,
        )

    # 2. Return the decorator
    return decorator


_DESIGN_NOTES = """
# signature_from

## Purpose
The flagship decorator of the library — assembles a complete `inspect.Signature`
from multiple parameter sources and applies it to the decorated function in a
single step. A high-level interface over `SignatureCreator` and
`apply_signature_to_wraps()`.

## How it works
The decorated function itself becomes `base_func` — its parameters form the
foundation of the signature. Additional parameters from `sources` are merged in,
with order controlled by `base_func_first`. The assembled signature is then
applied to a wrapper that preserves the original function's metadata.

## Typical use case
```python
@signature_from(my_param, base_func_first=False)
def my_func(*args, **kwargs):
    ...
```
Equivalent to manually creating a `SignatureCreator`, calling `create_signature()`,
and wrapping the function — but expressed as a single decorator.

## Parameter sources (sources)
Each item in `sources` can be:
- `inspect.Parameter` — added directly to the signature.
- `Callable`          — its parameters are extracted and merged in.

## base_func_first
Controls the merge order:
- `True`  (default) — decorated function's parameters come first, then `sources`.
- `False`           — `sources` parameters come first, then the decorated function's.

## Why validate=False in step 1.3
The signature produced by `create_signature()` in step 1.2 is already a
valid `inspect.Signature` — re-validating it inside `apply_signature_to_wraps()`
would be redundant. `validate=False` is an intentional optimisation.

## signature_copy vs signature_from
- `signature_copy` — copies an existing signature from another callable.
  Useful when the source signature already exists and only needs normalisation.
- `signature_from`  — assembles a new signature from scratch using
  `SignatureCreator`. Useful when combining parameters from multiple sources
  or when fine-grained control over the signature is needed.

## Notes
- Validation of `function` happens inside the decorator at decoration time —
  not at factory time when `signature_from(...)` is called.
- All parameter merging and ordering logic lives in `SignatureCreator` —
  `signature_from` is purely an orchestrator.
"""