import inspect
from typing import Self
# Outers
from ...validators import (
    SignatureBuildError,
    validate_is_inspect_parameter,
    validate_accept_double,
)


class AddParamMixin:
    """Mixin for adding parameters to internal storage with validation, exclusion, and order handling."""

    def add_param(
        self: Self,
        param: inspect.Parameter
    ) -> None:
        """
        Adds a parameter to internal storage with strict validation and duplicate handling.

        Acts as the primary gatekeeper for signature construction, ensuring that
        every parameter maintains Python's structural integrity rules.

        Args:
            param: The inspect.Parameter instance to add.

        Raises:
            SignatureBuildError (TypeError): If the input is not an inspect.Parameter.
            SignatureBuildError (ValueError): If a duplicate is found and accept_double=False.
            SignatureBuildError (SyntaxError): If a non-default parameter follows a default one.
            SignatureBuildError (TypeError): If the parameter kind is unrecognized.
        """

        # 1. Validation (Ensures input is a valid inspect.Parameter.)
        validate_is_inspect_parameter(param)

        # 2. Exclusion Check
        # Skips parameters that are explicitly ignored (e.g., self, cls, or custom exclusions).
        if param.name in self._excluded_names:
            return

        # 3. Flat Mode Handling
        # If flat_mode is enabled, the parameter is transformed into a KEYWORD_ONLY
        # parameter via a specialized mixin. This process short-circuits add_param.
        if self._flat_to_kwargs:
            self._flat_params_to_kwargs(param)
            return

        # 4. Duplicate and Replacement Strategy Handling
        if param.name in self._seen_names:

            # 4.1 Strict duplicate check (Raises error if policies forbid doubles)
            validate_accept_double(param, self._accept_double)

            # 4.2 Skip if replacement is disabled (Keep the original parameter)
            if not self._replace_double:
                return

            # 4.3 Execute Replacement: Remove old instance from its specific category
            kind_key, default_key = self._seen_names[param.name]
            self._params_map[kind_key][default_key] = [
                p for p in self._params_map[kind_key][default_key] if p.name != param.name
            ]

        # 5. Positional Parameter Order Validation
        # Enforces that mandatory positional parameters cannot follow optional ones.
        self._positional_empty_order_check(param)

        # 6. Determine Internal Storage Key
        # Categorizes parameters by whether they have a default value or not.
        inner_key = self._WITHOUT_DEFAULT if param.default is self.EMPTY else self._CONTAIN_DEFAULT

        # 7. Routing to Internal Storage
        try:
            self._params_map[param.kind][inner_key].append(param)
        except KeyError:
            raise SignatureBuildError(
                error_name="INVALID PARAMETER KIND ERROR",
                value_label="param.kind",
                value=param.kind,
                expected="a valid inspect._ParameterKind enum value",
                problem=f"Parameter '{param.name}' has an unsupported kind: {param.kind!r}.",
                how_to_fix="Ensure you are using standard Python parameter kinds.",
                context="AddParamMixin.add_param() — kind routing",
                exception=TypeError,
            ) from None

        # 8. Index Mapping Update
        # Updates the tracking dictionary for O(1) duplicate lookups and removals.
        self._seen_names[param.name] = (param.kind, inner_key)


_DESIGN_NOTES = """
# AddParamMixin

## Purpose
The primary orchestrator for populating the `ParameterCollector`. It ensures 
every added parameter is valid individually and maintains a legal relationship 
with existing parameters. By isolating this logic, the main collector class 
remains focused on storage rather than validation rules.

## Architecture: Logic Separation
To maintain high readability and a "dyslexia-friendly" code structure, complex 
sub-tasks and branching paths are delegated to specialized components:
- **`_flat_params_to_kwargs`**: Handles the heavy transformation and renaming 
  logic when the collector is in flat mode.
- **`_positional_empty_order_check`**: Enforces strict Python syntax rules 
  regarding the sequence of mandatory and optional positional arguments.
- **External Validators**: Perform reusable checks like type validation and 
  policy enforcement (e.g., checking for duplicate names).

## Process Flow
The `add_param` method follows a strict linear sequence to ensure safety:
1. **Entry Validation**: Immediate rejection if input is not an `inspect.Parameter`.
2. **Exclusion Gate**: Checks the `_excluded_names` set. If a match is found 
   (like 'self' or 'cls'), the process ends silently.
3. **Mode Branching**: If `flat_mode` is active, control is handed over to 
   `_flat_params_to_kwargs` and the standard flow is short-circuited.
4. **Collision Detection**: 
   - If the name exists, `validate_accept_double` checks if overwriting is allowed.
   - If allowed but `replace_double` is False, the new parameter is discarded.
   - If allowed and `replace_double` is True, the old parameter is surgically 
     removed from its specific sub-list in `_params_map`.
5. **Semantic Validation**: `_positional_empty_order_check` ensures that 
   adding this parameter won't break Python's "non-default after default" rule.
6. **Categorization**: The parameter is assigned a key (`_WITHOUT_DEFAULT` or 
   `_CONTAIN_DEFAULT`) based on its `default` attribute.
7. **Storage & Indexing**: The parameter is appended to the appropriate list 
   in `_params_map`, and the `_seen_names` registry is updated with its 
   new location (kind and category).

## Internal Storage Architecture
We use a two-tiered dictionary structure: `kind -> {_WITHOUT_DEFAULT | _CONTAIN_DEFAULT}`.
This design allows:
1. **Simplified Iteration**: When building the final signature, we can easily 
   yield non-defaults before defaults for each kind without complex sorting.
2. **Unified Handling**: All parameter kinds share the same structure for 
   consistency. Note that variadic parameters (*args, **kwargs) inherently 
   cannot have defaults (enforced by the `inspect` module itself), meaning 
   their `_CONTAIN_DEFAULT` list will always remain empty.

## Order Integrity
Python defines signatures as a contract. This mixin refuses to "auto-fix" 
illegal sequences (like mandatory params after optional ones) unless 
explicitly requested via `flat_mode`. Instead, it raises an explicit 
`SyntaxError` (wrapped in `SignatureBuildError`) to force the developer 
to maintain a clean and valid API design.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- **Variadic Safety**: No explicit validation is needed to check if `*args` or `**kwargs` 
  have default values. The `inspect.Parameter` class itself raises a `ValueError` 
  during instantiation if a variadic kind is paired with a default value. Therefore, 
  any `Parameter` object reaching this mixin is guaranteed to be syntactically 
  valid in this regard.
"""