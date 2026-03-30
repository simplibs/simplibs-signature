import inspect
# Commons
from ..utils import EXCLUDED, validate_is_bool
# Inners
from ._mixins import AddMixin, GetOrderedMixin
from ._validations import validate_is_tuple_with_str


class ParameterCollector(
    AddMixin,        # def add(self, param: inspect.Parameter) -> None
    GetOrderedMixin, # def get_ordered(self) -> list[inspect.Parameter]
):
    """
    Stores and manages function parameters grouped by their kind.

    Respects the excluded names list and duplicate rules when adding parameters.
    Parameters are internally ordered by `inspect._ParameterKind` and returned
    in the correct sequence.
    """

    # Attributes
    _excluded_names: set[str]
    _seen_names: set[str]
    _accept_double: bool
    _param_list: dict[inspect._ParameterKind, list[inspect.Parameter]]


    def __init__(
        self,
        excluded_names: tuple[str] | None = None,
        accept_double: bool = True,
    ):
        """
        Args:
            excluded_names: Parameter names to ignore in addition to the
                            defaults `self` and `cls`.
            accept_double:  If True, duplicate parameters are silently skipped.
                            If False, a duplicate raises SignatureBuildError.

        Raises:
            SignatureParameterError(TypeError): If `excluded_names` is not a
                                                tuple of strings.
            SignatureParameterError(TypeError): If `accept_double` is not a bool.
        """

        # 1. Build the set of names to skip — always starts with EXCLUDED defaults
        self._excluded_names = set(EXCLUDED)
        if excluded_names:
            validate_is_tuple_with_str(excluded_names, "excluded_names")
            self._excluded_names.update(excluded_names)

        # 2. Store the duplicate handling flag
        validate_is_bool(accept_double, "accept_double")
        self._accept_double = accept_double

        # 3. Initialise the parameter storage — one list per kind, in correct order
        self._param_list = {
            inspect.Parameter.POSITIONAL_ONLY: [],
            inspect.Parameter.POSITIONAL_OR_KEYWORD: [],
            inspect.Parameter.VAR_POSITIONAL: [],
            inspect.Parameter.KEYWORD_ONLY: [],
            inspect.Parameter.VAR_KEYWORD: [],
        }

        # 4. Initialise the set of already-seen parameter names
        self._seen_names: set[str] = set()


_DESIGN_NOTES = """
# ParameterCollector

## Purpose
An internal helper class used by `SignatureCreator` to collect, deduplicate,
and order `inspect.Parameter` instances during signature construction.
Not intended for direct use — instantiated in step 6 of
`SignatureCreator.__init__()`.

## Composition
| Mixin            | Provides                                              |
|------------------|-------------------------------------------------------|
| `AddMixin`       | `add()` — sources a parameter with exclusion and duplicate handling |
| `GetOrderedMixin`| `get_ordered()` — returns all parameters as a flat ordered list  |

## Attributes
| Attribute        | Description                                                      |
|------------------|------------------------------------------------------------------|
| `_excluded_names`| Set of parameter names to always skip (defaults + user-defined) |
| `_seen_names`    | Set of names already added — used for duplicate detection        |
| `_accept_double` | If False, duplicate parameter names raise `SignatureBuildError`  |
| `_param_list`    | Dict keyed by `inspect._ParameterKind` — one list per kind      |

## Why _param_list is a dict keyed by kind
Parameters must be returned in a specific order defined by
`inspect._ParameterKind` — positional first, keyword-only last.
Storing them in separate lists keyed by kind, inserted in the correct
order at init time, guarantees this order without any sorting at
retrieval time. `get_ordered()` simply flattens the dict values.

## Why EXCLUDED is the default starting point
`self` and `cls` are meaningless in a standalone signature — they are
always excluded by default. User-provided `excluded_names` extend this
set rather than replace it, so the defaults can never be accidentally removed.

## Notes
- `_seen_names` is a set — duplicate detection is O(1).
- `excluded_names` validation happens only when a value is provided —
  `None` is a valid "no extra exclusions" signal and is silently accepted.
"""