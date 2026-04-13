import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
# Inners
from .copy_signature import copy_signature
from .core.signature_creator import SignatureCreator
from .core.validators import (
    validate_param_sources,
    validate_excluded_names,
    validate_is_bool
)


def create_signature(
    *param_sources: inspect.Parameter | Callable,
    return_source: Any = UNSET,
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    validate: bool = True
) -> inspect.Signature:
    """
    The universal entry-point for creating or transforming function signatures.

    Intelligently dispatches between a fast signature copy (when a single
    callable is provided) and complex assembly (when mixing parameters
    and multiple sources).

    Args:
        *param_sources:    Variadic sources (Parameters or Callables) for signature building.
        return_source:     Source for return annotation (Type, Callable, or UNSET).
        excluded_names:    An iterable of parameter names (strings) to remove from the result.
        accept_double:     If False, name collisions raise an error.
        replace_double:    If True, later parameters overwrite earlier ones with the same name.
        include_variadic:  If False, removes *args and **kwargs.
        include_binding:   If False, removes 'self' and 'cls'.
        flat_to_kwargs:    If True, transforms all parameters into KEYWORD_ONLY.
        validate:          If True, performs strict type checking and sanitization.

    Returns:
        An inspect.Signature built from the provided sources and configuration.

    Raises:
        SignatureParameterError(ValueError): If param_sources is empty.
        SignatureParameterError(TypeError):  If inputs are of invalid types.
        SignatureBuildError(ValueError):     If the resulting signature structure is invalid.
    """

    # 1. Validations and Sanitization
    if validate:
        validate_param_sources(param_sources)
        # We sanitize the iterable into a stable tuple to prevent exhaustion
        # and ensure stability regardless of the internal path taken.
        excluded_names = validate_excluded_names(excluded_names)
        validate_is_bool(accept_double, "accept_double")
        validate_is_bool(replace_double, "replace_double")
        validate_is_bool(include_variadic, "include_variadic")
        validate_is_bool(include_binding, "include_binding")
        validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

    # 2. Fast Path: Single callable source
    # Dispatches to copy_signature for better performance
    if len(param_sources) == 1 and callable(param_sources[0]):
        return copy_signature(
            function          = param_sources[0],
            return_annotation = return_source,
            excluded_names    = excluded_names,
            accept_double     = accept_double,
            replace_double    = replace_double,
            include_variadic  = include_variadic,
            include_binding   = include_binding,
            flat_to_kwargs    = flat_to_kwargs,
            validate          = False  # Already validated and sanitized above
        )

    # 3. Standard Path: Multiple sources or Parameter objects
    # Uses SignatureCreator for complex merging and assembly
    return SignatureCreator(
        *param_sources,
        return_source    = return_source,
        excluded_names   = excluded_names,
        accept_double    = accept_double,
        replace_double   = replace_double,
        include_variadic = include_variadic,
        include_binding  = include_binding,
        flat_to_kwargs   = flat_to_kwargs,
        validate         = False  # Already validated and sanitized above
    ).signature


_DESIGN_NOTES = """
# create_signature

## Purpose
The primary public API of the library. Acts as a smart dispatcher that minimizes
overhead while providing maximum flexibility for signature creation and transformation.

## Where it is used
- Main entry point for all user-facing signature building workflows.
- Used by decorators as the foundation for signature application.
- Used internally by higher-level utilities for consistent behavior.

## Input Flexibility (Iterable Support)
Following the library-wide standard, `excluded_names` now accepts any `Iterable[str]`. 
This ensures that users can pass lists, sets, or generator expressions directly 
without manual casting. The input is sanitized into a `tuple` during the 
validation phase to ensure stability regardless of which internal path is taken.

## Intelligent Dispatch Strategy
The function uses two optimized paths:
1. **Fast Path** (Single Callable): When exactly one callable is provided
   (e.g., `create_signature(my_func)`), it delegates to `copy_signature()`.
   This avoids the overhead of `SignatureCreator`'s full object lifecycle.
2. **Standard Path** (Multiple Sources): When multiple sources are provided
   (e.g., `create_signature(func_a, param_b)` or when mixing Parameters and
   Callables), it initializes `SignatureCreator` to handle complex merging,
   ordering, and return type resolution.

## Performance Characteristics
- **Single callable**: O(N) where N is the number of parameters in the callable.
- **Multiple sources**: O(M × N) where M is the number of sources and N is average
  parameters per source (due to parameter collection from each source).
- **Overhead reduction**: The fast path avoids mixin method calls and return source
  processing overhead for the common single-callable case.

## Parameter Consistency
This function's signature is kept strictly in sync with:
- `copy_signature()` — for the fast path
- `SignatureCreator()` — for the standard path

Key parameters like `replace_double` and `excluded_names` are passed through
unchanged to ensure consistent behavior regardless of which path is taken.

## Using the UNSET Sentinel
The `return_source` parameter uses `UNSET` as its default, allowing:
- Distinction between "no return source provided" (UNSET) and "set to None" (None)
- `None` as a valid return annotation (e.g., `def f() -> None`)

## Design Philosophy
`create_signature` embodies the principle of "do the simple thing simply, and the
complex thing correctly":
- Simple case (one callable) → fast, direct path
- Complex case (multiple sources) → full orchestration via `SignatureCreator`

Users don't need to choose — the function automatically selects the optimal approach.

## Validation Consistency
All inputs are validated once (step 1) before any processing. The resulting
validation errors are consistent with the user's perspective (top-level function)
through sanitization (e.g. converting `Iterable` to `tuple`) we ensure stability
for subsequent internal calls without redundancy.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- `validate=False` in internal calls indicates "inputs are trusted" within
  the pipeline (already validated and sanitized in step 1).
- The resulting signature always maintains valid Python parameter order.
- Immutability is preserved — original callables are never modified.
- This function is the recommended entry point for all signature operations.
"""