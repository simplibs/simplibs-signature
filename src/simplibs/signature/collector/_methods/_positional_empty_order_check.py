import inspect
# Outers
from .._constants.strings import CONTAIN_DEFAULT
from .._constants.kinds import EMPTY, POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD
# Inners
from .validations import raise_invalid_parameter_order_error


def _positional_empty_order_check(
    param: inspect.Parameter,
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    """Refuse a required positional parameter that would follow an optional one.

    Args:
        param: The parameter that is about to be stored.
        params_map: The tiered storage, read only.

    Raises:
        ParamError: If `param` has no default and a stored parameter of an
            earlier or the same positional kind has one.
    """

    # 1. Skip check if the parameter has a default value
    if param.default is not EMPTY:
        return

    # 2. Validation Logic
    # 2.1 Check for POSITIONAL_ONLY violations
    if (
        param.kind is POSITIONAL_ONLY
        and params_map[POSITIONAL_ONLY][CONTAIN_DEFAULT]

        # 2.2 Check for POSITIONAL_OR_KEYWORD violations
    ) or (
        param.kind is POSITIONAL_OR_KEYWORD
        and (
            params_map[POSITIONAL_ONLY][CONTAIN_DEFAULT]
            or params_map[POSITIONAL_OR_KEYWORD][CONTAIN_DEFAULT]
        )
    ):
        # 2.3 Raise exception if a violation is detected
        raise_invalid_parameter_order_error(param)


_DESIGN_NOTES = """
# _positional_empty_order_check — The One Order Rule the Storage Cannot Keep

## Purpose
The tiers sort most of it: kinds come in the right order and, inside a kind,
required before optional. Only the two positional kinds cannot be sorted by
the storage. Python forbids `def f(a=1, b)`, and silently reordering would
change the meaning of a call, so the collector refuses instead.

## What Is Checked
| New parameter           | Refused if a stored parameter with a default is in      |
| :---------------------- | :------------------------------------------------------ |
| `POSITIONAL_ONLY`       | `POSITIONAL_ONLY`                                       |
| `POSITIONAL_OR_KEYWORD` | `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD`            |

A parameter with a default is always fine, and keyword-only parameters have no
such rule.

## Called After the Replacement
A replaced parameter has already been removed when the check runs, so it is
never judged against its own predecessor.
"""
