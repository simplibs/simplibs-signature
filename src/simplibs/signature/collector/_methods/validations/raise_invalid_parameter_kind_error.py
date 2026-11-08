from typing import NoReturn
import inspect
from simplibs.exception import ParamError


def raise_invalid_parameter_kind_error(
    param: inspect.Parameter,
    e: KeyError
) -> NoReturn:
    """Raise the error for a parameter whose kind the collector cannot store.

    Args:
        param: The parameter that was being added.
        e: The `KeyError` raised by the storage lookup.

    Raises:
        ParamError: Always, with `e` as the intercepted exception.
    """

    raise ParamError(
        error_name="INVALID PARAMETER KIND ERROR",
        label="param.kind",
        value=param.kind,
        expected="a valid inspect._ParameterKind enum value",
        problem=f"Parameter '{param.name}' has an unsupported kind: {param.kind!r}.",
        how_to_fix="Ensure you are using standard Python parameter kinds.",
        exception=e,
    )


_DESIGN_NOTES = """
# raise_invalid_parameter_kind_error — A Kind Nobody Expected

## Purpose
`inspect` knows five kinds and the storage map has a slot for each. This is the
answer when a parameter brings a sixth, for example an object that only pretends
to be an `inspect.Parameter`. Raised by `add_param`.

## Intercepting the `KeyError`
`exception=e` hands over the original error, so it stays visible and
`except KeyError` still catches it.
"""
