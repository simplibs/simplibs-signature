import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET

# Outers
from ..create_signature import create_signature
from ..core.validators import (
    validate_is_callable,
    validate_excluded_names,
    validate_is_bool
)
# Inners
from .builders import apply_signature_to_wraps


def signature(
    *params: inspect.Parameter | Callable,
    returns: Any = UNSET,
    excepts: Iterable[str] = (),
    use_func: bool = True,
    func_first: bool = True,
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    validate: bool = True
) -> Callable:
    """
    A powerful decorator for defining, merging, or transforming function signatures.

    Can build a completely new signature or modify the decorated function's
    existing signature by adding, removing, or replacing parameters with
    full control over composition order and conflict resolution.

    Args:
        *params:          Extra parameters or functions to merge into the signature.
        returns:          Source for the return annotation.
        excepts:          An iterable of parameter names (strings) to remove.
        use_func:         If True, includes the decorated function's signature
                          in the assembly process.
        func_first:       If True, the decorated function's parameters come before
                          the `*params` sources in the merge order.
        accept_double:    If False, raises error on duplicate parameter names.
        replace_double:   If True, later sources overwrite earlier ones.
        include_variadic: If False, filters out *args and **kwargs.
        include_binding:  If False, filters out 'self' and 'cls'.
        flat_to_kwargs:   If True, transforms all parameters into KEYWORD_ONLY.
        validate:         If True, performs validation and sanitization.

    Returns:
        A decorator that applies the assembled signature to the target function.

    Raises:
        SignatureParameterError(TypeError): If inputs are of invalid types.
        SignatureBuildError(ValueError):    If the resulting signature is invalid.
    """

    # 1. Define the decorator
    def decorator(function: Callable) -> Callable:

        # 1.1 Validations and Sanitization (performed at decoration time)
        local_excepts = excepts

        if validate:
            validate_is_callable(function)
            # Sanitizing into a stable tuple to support generators and prevent exhaustion
            local_excepts = validate_excluded_names(local_excepts, "excepts")
            validate_is_bool(use_func, "use_func")
            validate_is_bool(func_first, "func_first")
            validate_is_bool(accept_double, "accept_double")
            validate_is_bool(replace_double, "replace_double")
            validate_is_bool(include_variadic, "include_variadic")
            validate_is_bool(include_binding, "include_binding")
            validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

        # 1.2 Build the parameter sources list (accounting for use_func)
        param_sources = params
        if use_func:
            param_sources = (
                (function,) + param_sources if func_first
                else param_sources + (function,)
            )

        # 1.3 Assemble the signature from all sources
        new_signature = create_signature(
            *param_sources,
            return_source    = returns,
            excluded_names   = local_excepts,
            accept_double    = accept_double,
            replace_double   = replace_double,
            include_variadic = include_variadic,
            include_binding  = include_binding,
            flat_to_kwargs   = flat_to_kwargs,
            validate         = False  # Already validated and sanitized above
        )

        # 1.4 Wrap the function and apply the assembled signature
        return apply_signature_to_wraps(
            function  = function,
            signature = new_signature,
            validate  = False  # Already validated above
        )

    # 2. Return the decorator
    return decorator


_DESIGN_NOTES = """
# @signature (The Master Decorator)

## Purpose
The most powerful and flexible decorator in the library. It acts as a
"Swiss Army Knife" for function signature transformation, enabling complex
signature surgery using a single, declarative decorator.

## Input Flexibility (Iterable Support)
In alignment with the library-wide standard, the `excepts` parameter now 
accepts any `Iterable[str]`. This allows users to provide lists, sets, or 
even generator expressions directly. 

## Sanitization and Stability
When `validate=True`, the `excepts` iterable is materialized into a `tuple`.
This is critical for late-binding decorators, as it ensures that if a generator 
is passed to the decorator factory, it is correctly consumed and its values 
are preserved for every application of the decorator.

## Architecture: Late-Binding Decorator Pattern
Unlike `signature_copy` which pre-computes the signature, this decorator
uses a "late-binding" pattern:
1. The decorator is created with source parameters.
2. At decoration time, the decorated function is incorporated.
3. The combined signature is assembled and applied.

This pattern allows the decorated function's identity to influence the final
signature, enabling dynamic composition.

## Parameter Composition Logic
The key innovation is the interaction between `use_func` and `func_first`:

**use_func=True, func_first=True (default)**:
```
param_sources = (decorated_function,) + (*params)
```
The decorated function's parameters form the foundation; `*params` are updates.

**use_func=True, func_first=False**:
```
param_sources = (*params) + (decorated_function,)
```
The `*params` form the foundation; decorated function's params update them.

**use_func=False**:
```
param_sources = (*params)
```
Only the provided parameters are used; decorated function's signature is ignored.

## Merge Semantics (replace_double Control)
- `replace_double=True` (default): Later sources overwrite earlier ones
  with the same name. Useful for "patch" patterns.
- `replace_double=False`: Earlier sources take precedence; later ones are
  ignored. Useful for "base + fallback" patterns.

## Real-World Usage Examples
```python
# Example 1: Signature from another function
@signature(other_func, excepts=('internal_id',), returns=int)
def my_wrapper(*args, **kwargs):
    return 42

# Example 2: Augment the decorated function with extra parameters
custom_param = create_keyword_parameter('context', annotation=Context)
@signature(custom_param)  # use_func=True by default
def enhanced_function(a, b):
    # Signature is now (a, b, context)
    pass

# Example 3: Complete signature override
new_sig_params = (param1, param2, param3)
@signature(*new_sig_params, use_func=False)
def wrapper(*args, **kwargs):
    # Signature is (param1, param2, param3), ignoring original
    pass

# Example 4: Merge with controlled ordering
@signature(helper_func, params, func_first=False)
def combined(*args, **kwargs):
    # helper_func params are foundation, function's params added after
    pass
```

## Integration: Async Safety and Validation
Because this decorator delegates to `create_signature()` (logic) and
`apply_signature_to_wraps()` (wrapping), it automatically inherits:
1. **Async Compatibility**: Works with both `async def` and regular functions.
2. **Structural Integrity**: Parameters always in valid Python order.
3. **Advanced Filtering**: Can remove `self`, `*args`, `**kwargs` on the fly.
4. **Error Recovery**: Clear error messages at decoration time.

## Validation Strategy
Validation occurs in two phases:
1. **Factory Time**: Arguments passed to `@signature()` are validated (if any
   are callable, we defer their validation).
2. **Decoration Time** (step 1.1): When applied to a function, all configuration
   is validated to ensure a valid assembly.

Errors during decoration point to the decorator application, providing clear
context for debugging.

## Performance Characteristics
- **Time Complexity**: O(M × N) where M = number of sources, N = average
  parameters per source (due to parameter extraction from each).
- **Space Complexity**: O(M × N) for intermediate collections.
- **Optimization**: Validation is skipped in steps 1.3-1.4 since inputs are
  already trusted from 1.1.

## Parameter Naming: Decorator Context
Like `signature_copy`, this decorator uses abbreviated parameter names:
- `returns` (not `return_source`) — concise for decorator style
- `excepts` (not `excluded_names`) — familiar abbreviation
- `use_func` (not `use_decorated_function`) — shorter for readability

These abbreviated names are specific to the decorator API and don't affect
the underlying `create_signature()` function.

## Comparison with Lower-Level Tools
| Tool | Use Case | Flexibility |
|------|----------|-------------|
| `signature_copy()` | Transform one function's signature | Low |
| `@signature_copy` | Copy signature in decorator | Low |
| `create_signature()` | Build from scratch or multiple sources | High |
| `@signature` | Compose and merge at decoration time | Very High |

## Notes
- The resulting wrapper preserves function metadata via `functools.wraps`.
- The signature is applied via `__signature__` attribute assignment.
- Parameter order is always valid Python order, guaranteed by `ParameterCollector`.
- Async functions remain async; sync functions remain sync.
- The decorator can be composed with other decorators for advanced patterns.
- Late validation at decoration time ensures errors are caught during import,
  not at runtime.
"""