import inspect
from typing import Iterable, Self
# Outers
from ..constants import BINDING_NAMES, VARIADIC_NAMES
from ..validators import validate_is_bool, validate_excluded_names
# Inners
from ._mixins import (
    AddParamMixin,
    FlatParamsToKwarksMixin,
    PositionalEmptyOrderCheckMixin,
    GetOrderedParamsMixin
)


class ParameterCollector(
    AddParamMixin,                  # add_param(self, param: inspect.Parameter) -> None
    FlatParamsToKwarksMixin,        # _flat_params_to_kwargs(self, param: inspect.Parameter) -> None
    PositionalEmptyOrderCheckMixin, # _positional_empty_order_check(self, param: inspect.Parameter) -> None
    GetOrderedParamsMixin,          # get_ordered_params(self) -> tuple[inspect.Parameter, ...]
):
    """
    Orchestrates the storage, validation, and ordering of function parameters.

    It ensures that parameters are deduplicated, filtered based on exclusion rules,
    and correctly sequenced according to Python's structural integrity laws.
    Supports 'Flat Mode' for merging diverse signatures into a unified keyword-only API.
    """

    # --- Internal Constants & Aliases ---
    # Used to reduce visual noise and prevent string-literal errors in logic.
    _WITHOUT_DEFAULT = "no_default"
    _CONTAIN_DEFAULT = "default"

    # Shortcuts for inspect constants to improve code readability
    EMPTY = inspect.Parameter.empty
    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD

    # --- Attributes ---
    _excluded_names: set[str]
    _seen_names: dict[str, tuple[inspect._ParameterKind, str]]  # Name -> (Kind, Category)
    _accept_double: bool
    _replace_double: bool
    _flat_to_kwargs: bool
    _params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]

    def __init__(
        self,
        excluded_names: Iterable[str] = (),
        accept_double: bool = True,
        replace_double: bool = True,
        include_variadic: bool = True,
        include_binding: bool = True,
        flat_to_kwargs: bool = False,
        validate: bool = True
    ):
        """
        Initializes the collector with exclusion, duplicate handling, and mode rules.

        Args:
            excluded_names:   Names to ignore (e.g., list, set, or generator).
            accept_double:    If False, duplicate names raise SignatureBuildError.
            replace_double:   If True, new duplicates replace old ones.
                              If False, original is kept.
            include_variadic: If False, excludes *args and **kwargs.
            include_binding:  If False, excludes 'self' and 'cls'.
            flat_to_kwargs:   If True, transforms all parameters into KEYWORD_ONLY.
            validate:         If True, validates and sanitizes input arguments.

        Raises:
            SignatureParameterError (TypeError): If arguments are of invalid types.
        """

        # 1. Validate and Sanitize inputs
        if validate:
            excluded_names = validate_excluded_names(excluded_names)
            validate_is_bool(accept_double, "accept_double")
            validate_is_bool(replace_double, "replace_double")
            validate_is_bool(include_variadic, "include_variadic")
            validate_is_bool(include_binding, "include_binding")
            validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

        # 2. Build excluded names set
        self._excluded_names: set[str] = set(excluded_names)
        if not include_variadic:
            self._excluded_names.update(VARIADIC_NAMES)
        if not include_binding:
            self._excluded_names.update(BINDING_NAMES)

        # 3. Store configuration
        self._accept_double = accept_double
        self._replace_double = replace_double
        self._flat_to_kwargs = flat_to_kwargs

        # 4. Initialize name tracking (maps name to its location for O(1) replacement)
        self._seen_names: dict[str, tuple[inspect._ParameterKind, str]] = {}

        # 5. Initialize tiered storage map
        # Every kind uses a sub-dictionary with two categories: WITHOUT and CONTAIN default.
        self._params_map = {
            kind: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []}
            for kind in (
                self.POSITIONAL_ONLY,
                self.POSITIONAL_OR_KEYWORD,
                self.VAR_POSITIONAL,
                self.KEYWORD_ONLY,
                self.VAR_KEYWORD
            )
        }


_DESIGN_NOTES = """
# ParameterCollector

## Purpose
An internal manager for `inspect.Parameter` instances. It ensures that 
parameters are deduplicated, filtered (excluded), and correctly ordered 
according to Python's signature rules. It acts as the "source of truth" 
during the signature building process.

## Architecture: Shortcuts & Aliases
The class defines internal aliases for `inspect.Parameter` constants (e.g., 
`POSITIONAL_ONLY`). This serves two purposes:
1. **Readability**: Reduces long, repetitive lines of code.
2. **Maintenance**: Provides a single point of reference for constants used 
   across all inherited mixins.

## Tiered Storage Architecture
The `_params_map` uses a two-level dictionary: `Kind -> Category (Default status) -> List`.
```python
{ 
  POSITIONAL_OR_KEYWORD: { 
      "no_default": [...], 
      "default": [...] 
  }
}
```
### Why this structure?
- **Simplified Logic**: By giving every `kind` (including Variadics) the same 
  internal structure, the iteration logic in `GetOrderedParamsMixin` remains 
  universal and "dummy-proof".
- **Order Integrity**: This structure makes it trivial to ensure that 
  parameters without defaults are yielded before those with defaults, 
  preventing invalid Python signatures.
- **Variadic Safety**: While `VAR_POSITIONAL` and `VAR_KEYWORD` do not 
  support defaults, they share this structure for architectural symmetry. 
  Specific validators elsewhere ensure their "default" lists remain empty.

## Key Responsibilities
1. **Exclusion**: Filters names that must not appear (e.g., `self`, `cls`).
2. **Deduplication**: Handles name collisions via `accept_double` and 
   `replace_double` policies.
3. **Flat Mode**: When `flat_to_kwargs` is True, it delegates to 
   `FlatParamsToKwarksMixin` to unify all inputs into a Keyword-Only API.
4. **Ordering**: Guarantees a deterministic and syntactically legal sequence.

## Notes
- **O(1) Lookups**: `_seen_names` stores a tuple of `(kind, category)`, 
  allowing the collector to find and remove a parameter from its specific 
  list in the tiered map instantly during replacement.
- **Sanitization**: When `validate=True`, `excluded_names` is materialized 
  into a tuple. This prevents issues with exhausted generators and ensures 
  thread-safe initialization of the internal set.
- **Variadic Safety**: No explicit validation is needed to check if `*args` or `**kwargs` 
  have default values. The `inspect.Parameter` class itself raises a `ValueError` 
  during instantiation if a variadic kind is paired with a default value. Therefore, 
  any `Parameter` object reaching this mixin is guaranteed to be syntactically 
  valid in this regard.
"""