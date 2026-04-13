import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
# Outers
from ..copy_signature import copy_signature
from ..core.validators import (
    validate_is_callable,
    validate_parameters_collection,
    validate_excluded_names,
    validate_is_bool
)
# Inners
from .builders import create_signature_decorator


def signature_copy(
    base_func: Callable,
    *,
    returns: Any = UNSET,
    extras: Iterable[inspect.Parameter] = (),
    excepts: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    validate: bool = True
) -> Callable:
    """
    A decorator factory that copies and transforms a signature from a base callable.

    Acts as a high-level wrapper around `copy_signature()`, allowing you to
    use its power directly as a decorator with concise parameter names.

    Args:
        base_func:        The function to copy the signature from.
        returns:          New return type. If UNSET, keeps the original.
        extras:           An iterable of new parameters to add/update during the copy.
        excepts:          An iterable of parameter names (strings) to remove from the copy.
        accept_double:    If False, raises error on name collisions.
        replace_double:   If True, extra_params overwrite original parameters.
        include_variadic: If False, removes *args and **kwargs.
        include_binding:  If False, removes 'self' or 'cls'.
        flat_to_kwargs:   If True, transforms all parameters into KEYWORD_ONLY.
        validate:         If True, performs strict validation and sanitization.

    Returns:
        A decorator that applies the transformed signature to the target function.

    Raises:
        SignatureParameterError(TypeError): If inputs are of invalid types.
        SignatureBuildError(ValueError):    If the resulting signature is invalid.
    """

    # 1. Validations and Sanitization
    if validate:
        validate_is_callable(base_func, "base_func")
        # Materialize iterables into stable tuples to support generators and ensure
        # consistency when the resulting decorator is applied multiple times.
        extras = validate_parameters_collection(extras, "extras")
        excepts = validate_excluded_names(excepts, "excepts")
        validate_is_bool(accept_double, "accept_double")
        validate_is_bool(replace_double, "replace_double")
        validate_is_bool(include_variadic, "include_variadic")
        validate_is_bool(include_binding, "include_binding")
        validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

    # 2. Create the transformed signature
    signature = copy_signature(
        function            = base_func,
        return_annotation   = returns,
        extra_params        = extras,
        excluded_names      = excepts,
        accept_double       = accept_double,
        replace_double      = replace_double,
        include_variadic    = include_variadic,
        include_binding     = include_binding,
        flat_to_kwargs      = flat_to_kwargs,
        validate            = False  # Already validated and sanitized above
    )

    # 3. Create and return the decorator
    return create_signature_decorator(signature, validate=False)


_DESIGN_NOTES = """
# signature_copy

## Purpose
The flagship decorator for signature copying. Provides a declarative way to
synchronize function signatures across an application (e.g., from a
`Class.__init__` to a factory function or wrapper).

## Input Flexibility (Iterable Support)
In alignment with the library-wide standard, the `extras` and `excepts` 
parameters now accept any `Iterable`. This allows users to provide lists, 
sets, or generator expressions. 

## Sanitization and Stability
During the validation phase (Step 1), any provided iterables are materialized 
into `tuples`. This is crucial for a decorator factory: it ensures that if 
 a generator is passed to `signature_copy`, it is consumed once and its 
values are preserved. This allows the resulting decorator to be safely 
applied to multiple functions without losing the configuration.

## Where it is used
- User-facing decorator for copying and modifying existing signatures.
- Common pattern: `@signature_copy(my_class.__init__, excepts=('self',))`
- Used to make wrapper/adapter functions appear as if they have the same
  signature as their underlying callables.

## Parameter Naming: Conciseness for Decorator Context
This decorator uses abbreviated parameter names compared to the lower-level
`copy_signature()`:
- `returns` (not `return_annotation`) — shorter, fits decorator style
- `extras` (not `extra_params`) — concise for decorator contexts
- `excepts` (not `excluded_names`) — familiar abbreviation

This naming convention acknowledges that decorators are used inline and
verbosity matters less in function calls than in large parameter lists.

## Two-Stage Orchestration
1. **Transformation** (step 2): `copy_signature()` handles complex parameter
   merging, filtering, and ordering using `ParameterCollector`.
2. **Application** (step 3): `create_signature_decorator()` converts the
   result into a reusable decorator, including async/sync detection.

## Default Behavior: include_binding=True at API Level
Unlike some other decorators, `signature_copy` defaults `include_binding=True`.
However, the typical use case excludes binding parameters explicitly via the
`excepts` parameter (e.g., `excepts=('self',)`), giving users full control.

## Return Annotation Handling
Using the `UNSET` sentinel allows the decorator to distinguish between:
- No change: keep the original return annotation (UNSET)
- Set to None: explicitly `-> None`
- Set to a type: `-> int`, `-> Optional[str]`, etc.

## Validation Strategy
1. **Factory Validation** (step 1): All arguments are validated and sanitized 
   using specialized validators.
2. **Signature Creation** (step 2): `copy_signature()` performs additional
   structural validation during parameter collection.
3. **Decoration Time** (step 3): `create_signature_decorator()` validates
   the function being decorated.

Errors at any stage produce clear, user-friendly messages pinpointing the problem.

## Usage Examples
```python
# Copy a class constructor's signature to a factory function
@signature_copy(MyClass.__init__, excepts=('self',))
def create_instance(**kwargs):
    return MyClass(**kwargs)

# Add a parameter to an existing signature
new_param = create_keyword_parameter('context', annotation=Context)
@signature_copy(original_func, extras=(new_param,))
def wrapper(*args, **kwargs):
    return original_func(*args, **kwargs)

# Replace the return type while keeping everything else
@signature_copy(async_fetch, returns=dict)
def sync_wrapper(url):
    return asyncio.run(async_fetch(url))
```

## Integration with Library Ecosystem
- Works with both sync and async functions (via `apply_signature_to_wraps`).
- Parameter ordering is always guaranteed valid (via `ParameterCollector`).
- Can be composed with other decorators for advanced patterns.

## Performance Characteristics
- **Time Complexity**: O(N) where N is the number of parameters being processed.
- **Space Complexity**: O(N) for the intermediate signature and decorator storage.
- **Optimization**: Skips redundant validation in steps 2-3 since inputs are
  already trusted from step 1.

## Notes
- The resulting decorator is a true Python decorator — can be applied to
  multiple functions for the same signature transformation.
- Metadata is preserved via `functools.wraps` in the underlying wrapper.
- The signature is applied via `__signature__` attribute assignment.
- Parameter order is always maintained as valid Python order.
"""