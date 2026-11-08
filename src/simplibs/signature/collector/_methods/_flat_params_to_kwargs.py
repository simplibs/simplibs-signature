import inspect
# Outers
from ...constants import KWARGS
from .._constants.strings import WITHOUT_DEFAULT, CONTAIN_DEFAULT
from .._constants.kinds import VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD
# Inners
from ._remove_param import _remove_param
from .validations import raise_duplicate_parameter_error


def _flat_params_to_kwargs(
    param: inspect.Parameter,
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]],
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    accept_double: bool,
    replace_double: bool,
) -> None:
    """Store a parameter for flat mode: everything keyword-only.

    Args:
        param: The parameter to store.
        params_map: The tiered storage (changed in place).
        seen_names: The name index (changed in place).
        accept_double: If False, a name collision raises.
        replace_double: True: the new parameter replaces the stored one.
            False: both are kept, the new one renamed to `name_1`, `name_2`, ...

    Raises:
        ParamError: On a name collision when `accept_double` is False.
    """

    # 1. Variadic positional (*args) is dropped as it has no place in a flat signature.
    if param.kind is VAR_POSITIONAL:
        return

    # 2. Variadic keyword (**kwargs) is unified into a single clean placeholder.
    if param.kind is VAR_KEYWORD:
        if not params_map[VAR_KEYWORD][WITHOUT_DEFAULT]:
            params_map[VAR_KEYWORD][WITHOUT_DEFAULT].append(KWARGS)
            seen_names[KWARGS.name] = (VAR_KEYWORD, WITHOUT_DEFAULT)
        return

    # 3. Transform regular parameters to KEYWORD_ONLY
    param = param.replace(kind=KEYWORD_ONLY)

    # 4. Handle Name Collisions and Replacement Strategy
    if param.name in seen_names:

        # 4.1 Strict Duplicate Check
        if not accept_double:
            raise_duplicate_parameter_error(param)

        # 4.2 Replacement Strategy: Overwrite existing
        if replace_double:
            _remove_param(param.name, seen_names, params_map)

        # 4.3 Replacement Strategy: Keep & Rename (Smart Renaming)
        else:
            original_name = param.name
            counter = 1
            while param.name in seen_names:
                param = param.replace(name=f"{original_name}_{counter}")
                counter += 1

    # 5. Routing to Internal Storage
    params_map[KEYWORD_ONLY][CONTAIN_DEFAULT].append(param)

    # 6. Index Mapping Update
    seen_names[param.name] = (KEYWORD_ONLY, CONTAIN_DEFAULT)


_DESIGN_NOTES = """
# _flat_params_to_kwargs — Many Signatures, One Keyword-Only API

## Purpose
Merging unrelated signatures usually ends in clashes of kinds and defaults.
Flat mode removes the problem: every regular parameter becomes `KEYWORD_ONLY`.
Keyword-only parameters may follow each other in any order, with or without
defaults, so nothing can be in the wrong place.

## What Happens to Each Kind
| Kind                     | Result                                                |
| :----------------------- | :---------------------------------------------------- |
| `VAR_POSITIONAL`         | Dropped: a keyword-only API has no place for it.      |
| `VAR_KEYWORD`            | All merge into one `KWARGS` placeholder.              |
| Everything else          | Stored as `KEYWORD_ONLY`.                             |

## Smart Renaming
With `replace_double=False` the normal mode drops the later duplicate. Flat mode
exists to merge without losing anything, so it keeps both and renames the later
one to `name_1`, `name_2`, ... until the name is free. This difference is
intended and is documented on `replace_double` in every public function.

## One Tier
Every parameter goes into `CONTAIN_DEFAULT`, even one without a default. Keeping
a single list preserves the order in which the parameters arrived; the order
inside keyword-only parameters does not matter to Python.

## `**kwargs` Ignores `accept_double`
Two `**kwargs` are not a clash worth an error here: they are folded into one.
"""
