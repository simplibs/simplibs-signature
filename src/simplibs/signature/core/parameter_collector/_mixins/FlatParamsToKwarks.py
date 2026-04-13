import inspect
from typing import Self
# Outers
from ...constants import KWARGS
from ...validators import validate_accept_double


class FlatParamsToKwarksMixin:
    """Mixin providing logic to flatten all parameters into keyword-only arguments."""

    def _flat_params_to_kwargs(
        self: Self,
        param: inspect.Parameter
    ) -> None:
        """
        Transforms a parameter into a KEYWORD_ONLY kind and handles its storage.

        This method is the heart of 'flat_mode'. It bypasses standard positional
        rules by converting everything to keyword-only. It also handles smart
        renaming if duplicates are found and replacement is disabled.

        Variadic keyword parameters (**kwargs) are unified into a single
        standardized placeholder to prevent annotation conflicts.

        Args:
            param: The parameter to be flattened or unified.

        Raises:
            SignatureBuildError (ValueError): If names collide and accept_double is False.
        """

        # 1. Handle Variadic Parameters
        # Variadic positional (*args) is dropped as it has no place in a flat signature.
        if param.kind is self.VAR_POSITIONAL:
            return

        # Variadic keyword (**kwargs) is unified into a single clean placeholder.
        # This prevents issues where multiple sources have different **kwargs
        # names or type annotations that would conflict.
        if param.kind is self.VAR_KEYWORD:
            if not self._params_map[self.VAR_KEYWORD][self._WITHOUT_DEFAULT]:
                # We use the standardized KWARGS constant for consistency
                self._params_map[self.VAR_KEYWORD][self._WITHOUT_DEFAULT].append(KWARGS)
                self._seen_names[KWARGS.name] = (self.VAR_KEYWORD, self._WITHOUT_DEFAULT)
            return

        # 2. Transform regular parameters to KEYWORD_ONLY
        param = param.replace(kind=self.KEYWORD_ONLY)

        # 3. Handle Name Collisions and Replacement Strategy
        if param.name in self._seen_names:

            # 3.1 Strict Duplicate Check
            validate_accept_double(param, self._accept_double)

            # 3.2 Replacement Strategy: Overwrite existing
            if self._replace_double:
                kind_key, default_key = self._seen_names[param.name]
                self._params_map[kind_key][default_key] = [
                    p for p in self._params_map[kind_key][default_key]
                    if p.name != param.name
                ]

            # 3.3 Replacement Strategy: Keep & Rename (Smart Renaming)
            else:
                original_name = param.name
                counter = 1
                while param.name in self._seen_names:
                    param = param.replace(name=f"{original_name}_{counter}")
                    counter += 1

        # 4. Routing to Internal Storage
        # In flat mode, transformed parameters are always stored in the
        # KEYWORD_ONLY / _CONTAIN_DEFAULT bucket to ensure valid ordering.
        self._params_map[self.KEYWORD_ONLY][self._CONTAIN_DEFAULT].append(param)

        # 5. Index Mapping Update
        self._seen_names[param.name] = (self.KEYWORD_ONLY, self._CONTAIN_DEFAULT)


_DESIGN_NOTES = """
# FlatParamsToKwarksMixin

## Purpose
This mixin implements the 'Flat Mode' logic for the `ParameterCollector`. 
Its primary goal is to allow merging signatures from diverse sources without 
triggering Python's strict positional argument ordering errors.

## Why Flat Mode?
When building decorators or adapters that merge multiple functions, you often 
encounter conflicting positional-only or positional-or-keyword arguments. 
By converting everything to `KEYWORD_ONLY`, we eliminate these conflicts 
entirely, creating a robust and flexible resulting signature that can handle 
"rough treatment" during merging.

## Process Flow
1. **Positional Variadic Filtering**: `VAR_POSITIONAL` (*args) is discarded 
   because a flat keyword-only signature cannot conceptually support it.
2. **Keyword Variadic Unification**: To prevent type-hint pollution or 
   naming conflicts between multiple `**kwargs` sources, we detect any 
   `VAR_KEYWORD` and replace it with a single, clean `KWARGS` placeholder 
   (defined in constants). This ensures the final signature has exactly 
   one standard `**kwargs` if any were present. The placeholder is also 
   registered in `_seen_names` to keep the index synchronized and prevent 
   naming collisions with subsequent parameters.
3. **Transformation**: All other parameters are forcefully changed to 
   `KEYWORD_ONLY` using `param.replace()`.
4. **Collision Handling**:
   - If `accept_double` is False: Raises an error via `validate_accept_double`.
   - If `replace_double` is True: Removes the existing parameter.
   - If `replace_double` is False: Triggers **Smart Renaming**.
5. **Smart Renaming**: If a name collision occurs and overwriting is disabled, 
   the mixin appends a numeric suffix (e.g., `name_1`, `name_2`) until a 
   unique name is found.
6. **Unified Storage**: All transformed parameters are stored in the 
   `KEYWORD_ONLY` category to maintain the sequence in which they were added.

## Notes
- This mixin is a specialized tool for `AddParamMixin` and short-circuits 
  the standard flow.
- The unification of `**kwargs` is a safety feature specific to `flat_mode`. 
  In standard mode, the library respects the user's specific variadic 
  definitions, but `flat_mode` prioritizes a working, conflict-free output.
"""