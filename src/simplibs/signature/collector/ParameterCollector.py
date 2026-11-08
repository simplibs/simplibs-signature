import inspect
from typing import Iterable
from simplibs.validate import validate_call
# Outers
# Inners
from ._methods import add_param as _add_param
from ._constants.groups import BINDING_NAMES
from ._constants.strings import WITHOUT_DEFAULT, CONTAIN_DEFAULT
from ._constants.kinds import (
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
    KEYWORD_ONLY,
    VAR_KEYWORD,
)


class ParameterCollector:
    """Collect parameters from any number of sources into one valid, ordered set.

    It applies the exclusion rules, settles name collisions, keeps the order that
    Python requires and, in flat mode, turns everything into one keyword-only API.
    Feed it with `add_param` / `add_params`, read the result with
    `get_ordered_params`.
    """

    # --- Attributes Type Annotations ---
    _excluded_names: set[str]
    _seen_names: dict[str, tuple[inspect._ParameterKind, str]]
    _accept_double: bool
    _replace_double: bool
    _include_variadic: bool
    _flat_to_kwargs: bool
    _params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]

    @validate_call(materialize_iterators=True)
    def __init__(
        self,
        *,
        excluded_names: Iterable[str] = (),
        accept_double: bool = True,
        replace_double: bool = True,
        include_variadic: bool = True,
        include_binding: bool = True,
        flat_to_kwargs: bool = False,
        _validate_call: bool = True
    ):
        """Create a collector with its exclusion, collision and mode rules.

        Args:
            excluded_names: Names to leave out (list, set, tuple or generator).
            accept_double: If False, a name collision raises `ParamError`. If True,
                `replace_double` decides who wins.
            replace_double: True: the later parameter replaces the earlier one.
                False: the earlier one stays. In flat mode the later one is kept as
                well, renamed to `name_1`, `name_2`, ...
            include_variadic: If False, every `*args` and `**kwargs` is left out,
                whatever it is called.
            include_binding: If False, parameters named `self` and `cls` are left out.
            flat_to_kwargs: If True, every parameter becomes keyword-only; `*args`
                is dropped and all `**kwargs` merge into one.
            _validate_call: Reserved switch of `@validate_call`. False skips the
                validation of the arguments; trusted internal callers pass it.
        """

        # 1. Build excluded names set (variadics are excluded by kind, not by name)
        self._excluded_names = set(excluded_names)
        if not include_binding:
            self._excluded_names.update(BINDING_NAMES)

        # 2. Store configuration
        self._include_variadic = include_variadic
        self._accept_double = accept_double
        self._replace_double = replace_double
        self._flat_to_kwargs = flat_to_kwargs

        # 3. Initialize name tracking (maps name to its location for O(1) replacement)
        self._seen_names = {}

        # 4. Initialize tiered storage map using constants
        self._params_map = {
            kind: {WITHOUT_DEFAULT: [], CONTAIN_DEFAULT: []}
            for kind in (
                POSITIONAL_ONLY,
                POSITIONAL_OR_KEYWORD,
                VAR_POSITIONAL,
                KEYWORD_ONLY,
                VAR_KEYWORD
            )
        }

    @validate_call
    def add_param(
        self,
        param: inspect.Parameter,
        *,
        _validate_call: bool = True
    ) -> None:
        """Add one parameter, subject to the exclusion, collision and order rules.

        Args:
            param: The parameter to add.
            _validate_call: Reserved switch of `@validate_call`. False skips the
                validation of the arguments; trusted internal callers pass it.

        Raises:
            ParamError: On a refused collision (`accept_double=False`), a required
                positional parameter after an optional one, or an unsupported kind.
        """
        _add_param(
            param=param,
            excluded_names=self._excluded_names,
            include_variadic=self._include_variadic,
            flat_to_kwargs=self._flat_to_kwargs,
            accept_double=self._accept_double,
            replace_double=self._replace_double,
            seen_names=self._seen_names,
            params_map=self._params_map,
        )

    @validate_call(materialize_iterators=True)
    def add_params(
        self,
        params: Iterable[inspect.Parameter],
        *,
        _validate_call: bool = True
    ) -> None:
        """Add several parameters, one after another.

        Args:
            params: The parameters to add, in the order they are given.
            _validate_call: Reserved switch of `@validate_call`. False skips the
                validation of the arguments; trusted internal callers pass it.

        Raises:
            ParamError: As `add_param`.
        """
        for param in params:
            self.add_param(param, _validate_call=False)

    def get_ordered_params(
        self
    ) -> tuple[inspect.Parameter, ...]:
        """Return the stored parameters in the order Python requires.

        Returns:
            A tuple ordered by kind (positional-only, ordinary, `*args`, keyword-only,
            `**kwargs`) and, inside each kind, required before optional.
        """
        return tuple(
            param
            for category_map in self._params_map.values()
            for param_list in category_map.values()
            for param in param_list
        )


_DESIGN_NOTES = """
# ParameterCollector — One Valid Parameter Set From Many Sources

## Purpose
Every operation that builds a signature (`create_signature`, `copy_signature`,
`add_params_to_signature`, `delete_params_from_signature`) has the same chore:
take parameters from several places, drop some, settle name collisions and end
with an order Python accepts. The collector is that chore, in one place.

## State

| Attribute           | Role                                                              |
| :------------------ | :---------------------------------------------------------------- |
| `_excluded_names`   | Names to skip: the caller's, plus `self` and `cls` if asked.      |
| `_include_variadic` | If False, every `*args` / `**kwargs` is skipped, by kind.         |
| `_accept_double`    | If False, a collision is an error.                                |
| `_replace_double`   | Who wins a collision: the later or the earlier parameter.         |
| `_flat_to_kwargs`   | Flat mode: everything keyword-only.                               |
| `_seen_names`       | Name -> (kind, tier). Collision lookup and removal in O(1).       |
| `_params_map`       | Kind -> tier -> list. The storage.                                |

## Tiered Storage
Each kind has two lists, `WITHOUT_DEFAULT` and `CONTAIN_DEFAULT`, and
`get_ordered_params` reads them in the order Python requires: positional-only,
ordinary, `*args`, keyword-only, `**kwargs`; required before optional inside a
kind. Because the order comes from the storage, sources can be loaded in any
order.

## Behaviour Lives in Plain Functions
`add_param` (and its private parts) is a function in `_methods`; the class only
holds the state and passes it in. The rules can then be tested without
building a collector.

## What It Refuses
A collision when `accept_double=False`, a required positional parameter after an
optional one, and a kind the storage has no slot for. It does not look at
annotations or default values.

## `include_variadic` and `include_binding`
Different mechanisms on purpose. Variadics have a kind of their own and are
excluded by it, so `*a` and `**options` go as well as `*args`. `self` and `cls`
are ordinary parameters recognised only by convention, so they are excluded by
name.

## Where an Error Points
Every error here is a `ParamError`; see the notes of the package root.
"""
