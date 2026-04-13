import inspect
from typing import Any
# Outers
from ..exceptions import SignatureBuildError


def validate_param_sources(
    value: Any,
    value_name: str = "param_sources"
) -> None:
    """
    Validates that SignatureCreator received at least one valid parameter source.

    Parameter sources can be:
    - inspect.Parameter instances
    - callable objects (functions, methods, lambdas)

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

    Raises:
        SignatureBuildError(ValueError, TypeError):
            - If `param_sources` is empty
            - If any item is not a valid parameter source
    """

    # 1. Check non-empty
    if not value:
        raise SignatureBuildError(
            error_name  = "SIGNATURE CREATOR ERROR",
            value_label = f"{value_name}",
            value       = value,
            expected    = "at least one parameter source (Parameter or callable)",
            problem     = "SignatureCreator cannot build a signature — no parameter source was provided.",
            how_to_fix  = (
                "Pass one or more sources:",
                "  • SignatureCreator(my_param)",
                "  • SignatureCreator(my_func)",
                "  • SignatureCreator(my_param, my_func, another_param)",
            ),
            context      = "SignatureCreator.__init__() — parameter sources presence check",
            exception    = ValueError,
        )

    # 2. Validate each item type
    for index, item in enumerate(value):
        if not (isinstance(item, inspect.Parameter) or callable(item)):
            raise SignatureBuildError(
                error_name  = "INVALID PARAMETER SOURCE",
                value_label = f"{value_name}[{index}]",
                value       = item,
                expected    = "inspect.Parameter or callable",
                problem     = (
                    f"Item at index {index} is not a valid parameter source, "
                    f"but {type(item).__name__!r}."
                ),
                how_to_fix  = (
                    "Ensure all items are either:",
                    "  • inspect.Parameter instances",
                    "  • callable objects (functions, methods, lambdas)",
                ),
                context      = "SignatureCreator.__init__() — parameter source type check",
                exception    = TypeError,
            )


_DESIGN_NOTES = """
# validate_param_sources

## Purpose
Ensures that SignatureCreator receives at least one valid parameter source.
Without any source, the signature cannot be built.

A parameter source is either:
- `inspect.Parameter` — a parameter to include directly
- `callable` — a function/method whose parameters will be extracted

## Where it is used
- `SignatureCreator.__init__()` — at the very start of initialization,
  before any signature construction begins.

## Validation Steps
1. Non-empty check: Rejects empty input immediately (fail-fast).
2. Type check: Validates that each item is either `inspect.Parameter` or `callable`.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- Input always arrives as a tuple (from `*param_sources`), so no stabilization needed.
- `context` field identifies the exact validation point in the initialization flow.
- Callables are intentionally not introspected during validation — that happens later
  in `SignatureCreator.process()` when full error context is available.
"""