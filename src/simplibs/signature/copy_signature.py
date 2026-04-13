import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
# Outers
from .core.parameter_collector import ParameterCollector
from .core.utils import get_signature, compose_signature
from .core.validators import (
    validate_excluded_names,
    validate_parameters_collection,
    validate_is_bool
)


def copy_signature(
    function: Callable,
    *,
    return_annotation: Any = UNSET,
    extra_params: Iterable[inspect.Parameter] = (),
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    validate: bool = True
) -> inspect.Signature:
    """
    Creates a modified copy of a function's signature.

    Allows selective parameter removal, addition, and return type modification
    of an existing callable's signature in a single operation.

    Args:
        function:          The source function or callable to copy the signature from.
        return_annotation: New return type hint. If UNSET, keeps the original.
        extra_params:      An iterable of inspect.Parameter instances to add or update.
        excluded_names:    An iterable of parameter names (strings) to remove.
        accept_double:     If False, name collisions between original and extra raise error.
        replace_double:    If True, extra_params replace original parameters with the same name.
        include_variadic:  If False, removes *args and **kwargs from the result.
        include_binding:   If False, removes 'self' and 'cls' from the result.
        flat_to_kwargs:    If True, transforms all parameters into KEYWORD_ONLY.
        validate:          If True, performs strict type checking and sanitizes inputs.

    Returns:
        A new inspect.Signature instance reflecting all requested changes.

    Raises:
        SignatureParameterError(TypeError): If input arguments are of invalid types.
        SignatureBuildError(ValueError):    If the resulting signature structure is invalid.
    """

    # 1. Validations and Sanitization
    if validate:
        # We sanitize iterables into tuples to prevent exhaustion and ensure stability
        extra_params = validate_parameters_collection(extra_params, "extra_params")
        excluded_names = validate_excluded_names(excluded_names)
        validate_is_bool(accept_double, "accept_double")
        validate_is_bool(replace_double, "replace_double")
        validate_is_bool(include_variadic, "include_variadic")
        validate_is_bool(include_binding, "include_binding")
        validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

    # 2. Get base signature from the function
    signature = get_signature(function, validate=False)

    # 3. Initialize parameter collector with configuration
    param_collector = ParameterCollector(
        excluded_names=excluded_names,
        include_variadic=include_variadic,
        include_binding=include_binding,
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        validate=False  # Arguments already validated or sanitized in step 1
    )

    # 4. Load original signature parameters into the collector
    for param in signature.parameters.values():
        param_collector.add_param(param)

    # 5. Add extra parameters to the collector
    for param in extra_params:
        param_collector.add_param(param)

    # 6. Determine final return annotation
    final_return = (
        return_annotation
        if return_annotation is not UNSET
        else signature.return_annotation
    )

    # 7. Compose the final signature
    return compose_signature(
        parameters=param_collector.get_ordered_params(),
        return_annotation=final_return,
        validate=False  # Optimization: Components already validated
    )


_DESIGN_NOTES = """
# copy_signature

## Purpose
The primary tool for signature transformation and cloning. Allows developers
to "clone and tweak" any callable's signature using a declarative, single-call interface.

## Input Flexibility (Iterable Support)
Both `extra_params` and `excluded_names` now accept any `Iterable`. This 
alignment with the library-wide standard ensures that users can pass lists, 
sets, or generator expressions directly without manual casting to tuples.

## Implementation: The Collector Pattern
Instead of manual list filtering and splicing, the function delegates all parameter
logic to `ParameterCollector`:
- **Sanitization**: When `validate=True`, input iterables are materialized into 
  tuples. This prevents issues with one-time iterators (like generators) being 
  exhausted during validation or collection.
- **Single-Pass Processing**: All parameters collected, ordered once at the end.
- **Centralized Rules**: Exclusion logic (names, bindings, variadics) is unified.
- **Duplication Strategy**: Both `accept_double` and `replace_double` are delegated.

## Using the UNSET Sentinel
Standard `None` can be a valid return annotation (e.g., `def f() -> None`).
Using the `UNSET` sentinel allows us to distinguish between "Keep original" 
(UNSET) and "Explicitly set to None" (None).

## Parameter Interaction
- `extra_params` are added after original parameters, allowing replacement based
  on `replace_double` configuration.
- `excluded_names` are applied before `extra_params` are added, ensuring proper
  filtering and deduplication.

## Performance Optimization
The function performs only one `compose_signature()` call at the end, avoiding
the overhead of creating multiple intermediate signature objects.

## Error Handling
- Input validation (step 1) catches type errors early.
- `ParameterCollector` handles logical parameter merging.
- `compose_signature()` ensures final structural integrity.
"""