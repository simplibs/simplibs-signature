import inspect
from typing import Self
# Outers
from ...validators.exceptions.SignatureBuildError import SignatureBuildError


class PositionalEmptyOrderCheckMixin:
    """Mixin providing specialized validation for positional parameter ordering."""

    def _positional_empty_order_check(
        self: Self,
        param: inspect.Parameter
    ) -> None:
        """
        Ensures that non-default parameters do not follow parameters with defaults.

        This check is strictly enforced for POSITIONAL_ONLY and POSITIONAL_OR_KEYWORD
        kinds to maintain valid Python syntax integrity.

        Args:
            param: The parameter instance currently being added.

        Raises:
            SignatureBuildError (SyntaxError): If the ordering rule is violated.
        """

        # 1. Skip check if the parameter has a default value
        if param.default is not self.EMPTY:
            return

        # 2. Validation Logic
        # 2.1 Check for POSITIONAL_ONLY violations
        if (
            param.kind is self.POSITIONAL_ONLY
            and self._params_map[self.POSITIONAL_ONLY][self._CONTAIN_DEFAULT]

        # 2.2 Check for POSITIONAL_OR_KEYWORD violations
        # These cannot follow defaults in either POSITIONAL_ONLY or their own category
        ) or (
            param.kind is self.POSITIONAL_OR_KEYWORD
            and (
                self._params_map[self.POSITIONAL_ONLY][self._CONTAIN_DEFAULT]
                or self._params_map[self.POSITIONAL_OR_KEYWORD][self._CONTAIN_DEFAULT]
            )

        # 2.3 Raise exception if a violation is detected
        ):
            raise SignatureBuildError(
                error_name="INVALID PARAMETER ORDER",
                value_label=f"param.{param.name}",
                value=param.name,
                expected="non-default parameters before default parameters",
                problem=(
                    f"Parameter '{param.name}' (no default value) cannot follow "
                    "parameters that already have default values."
                ),
                how_to_fix=(
                    "Ensure all mandatory parameters (without defaults) are added "
                    "before optional parameters (with defaults).",
                    "Check the order of your sources or extra_params."
                ),
                context="AddParamMixin.add_param() — default value order check",
                exception=SyntaxError,
            )


_DESIGN_NOTES = """
# PositionalEmptyOrderCheckMixin

## Purpose
This mixin isolates the complex logic required to enforce Python's strict 
parameter ordering rules. It specifically ensures that "non-default arguments 
do not follow default arguments" in positional contexts.

## Why Isolated?
This logic was moved out of the main `add_param` flow for two reasons:
1. **Noise Reduction**: The conditional logic for checking across different 
   parameter categories created significant visual noise, obscuring the primary 
   storage logic.
2. **Internal State Access**: Unlike general validators, this check requires 
   real-time access to the `_params_map` state. Using a mixin allows it to 
   remain "internal" to the collector without passing heavy state objects 
   around.

## Logic / Process Flow
The check only triggers if the incoming parameter has no default value (`self.EMPTY`).
- **POSITIONAL_ONLY**: Fails if any `POSITIONAL_ONLY` parameters with defaults 
  have already been stored.
- **POSITIONAL_OR_KEYWORD**: Fails if any `POSITIONAL_ONLY` OR 
  `POSITIONAL_OR_KEYWORD` parameters with defaults have already been stored.

This reflects how Python interprets function signatures where positional 
arguments must form a continuous block of mandatory parameters followed by 
a block of optional ones.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- This mixin is designed to be used exclusively by `AddParamMixin.add_param()`.
- It uses `SyntaxError` as the underlying exception type to accurately 
  reflect the nature of the violation (invalid Python signature semantics).
"""