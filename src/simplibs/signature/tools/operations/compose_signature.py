from typing import Any, Iterable
import inspect
from simplibs.validate import validate_call
# Inners
from ._validations import (
    raise_signature_composition_value_error,
    raise_signature_composition_attribute_error,
    raise_signature_composition_type_error
)


@validate_call(materialize_iterators=True)
def compose_signature(
    parameters: Iterable[inspect.Parameter],
    return_annotation: Any = inspect.Signature.empty,
    *,
    _validate_call: bool = True,
) -> inspect.Signature:
    """Create an `inspect.Signature` from parameters and a return annotation.

    The structure of the result is always checked by `inspect`: order of kinds,
    duplicate names, defaults.

    Args:
        parameters: The parameters, in the order they are to appear.
        return_annotation: The return annotation. Default: none.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        The new signature.

    Raises:
        ParamError: If `parameters` is not an iterable (also catchable as
            `TypeError`), contains something that is not a parameter (also
            `AttributeError`) or does not form a valid signature (also
            `ValueError`).
    """

    # 1. Read the parameters once: a generator would be empty for the error message
    try:
        params = tuple(parameters)
    except TypeError as e:
        raise_signature_composition_type_error(parameters, e)

    # 2. Signature composition (inspect validates the structure)
    try:
        return inspect.Signature(
            parameters=params,
            return_annotation=return_annotation,
        )

    # 3. Handle structural issues
    except ValueError as e:
        raise_signature_composition_value_error(params, e)

    # 4. Handle duck-typing failures
    except AttributeError as e:
        raise_signature_composition_attribute_error(params, e)

    # 5. Handle invalid types in the parameters or annotations
    except TypeError as e:
        raise_signature_composition_type_error(params, e)


_DESIGN_NOTES = """
# compose_signature — The One Place a Signature Is Built

## Purpose
Every operation of the library that ends in an `inspect.Signature` ends here, so
there is one set of errors for "these parameters do not form a signature".

## Always Validated
`inspect.Signature(..., __validate_parameters__=False)` is an undocumented
CPython argument. It would save a loop over a handful of parameters, and in
return a duplicate name would be merged silently and the three error branches
below would never run. `_validate_call` therefore controls only `@validate_call`;
the structure is checked every time.

## Materialised Once
`parameters` may be a generator. The first pass would empty it, and the error
would then show an empty collection instead of the parameters that failed. They
are read into a tuple first and that tuple is used for both the signature and
the message.

## Three Failures, Three Errors
| Raised by `inspect`  | Meaning                                    | Error raised                             |
| :------------------- | :----------------------------------------- | :--------------------------------------- |
| `ValueError`         | Wrong order, duplicate name, bad default   | `raise_signature_composition_value_error`|
| `AttributeError`     | An item has no `.name` (not a Parameter)   | `raise_signature_composition_attribute_error` |
| `TypeError`          | Not iterable, or unusable types            | `raise_signature_composition_type_error` |

## What It Does Not Catch
`(*a, *b)`: `inspect` accepts two variadics of one kind. `ParameterCollector`
prevents it before this function is reached.
"""
