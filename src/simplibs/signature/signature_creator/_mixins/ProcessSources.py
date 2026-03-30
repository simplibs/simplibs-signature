import inspect
from typing import Self
# Commons
from ...utils import SignatureBuildError


class ProcessSourcesMixin:
    """Mixin for iterating over sources and routing each item to the correct processor."""

    def _process_sources(self: Self) -> None:
        """
        Iterates over all items in `_sources` and sources them to `_param_list`.

        Raises:
            SignatureBuildError(TypeError): If an item is neither an inspect.Parameter
                                            nor a callable.
        """

        # 1. Iterate over all items in sources
        for item in self._sources:

            # 1.1 Item is an inspect.Parameter — add directly
            if isinstance(item, inspect.Parameter):
                self._param_list.add(item)

            # 1.2 Item is a callable — extract its parameters
            elif callable(item):
                self._process_func(item)

            # 1.3 Unsupported item type
            else:
                raise SignatureBuildError(
                    error_name  = "INVALID ARGUMENT ERROR",
                    value_label = "sources",
                    value       = item,
                    expected    = "an inspect.Parameter instance or a callable (function, method, lambda)",
                    problem     = f"Item of type {type(item).__name__!r} is not a supported value for 'sources'.",
                    how_to_fix  = (
                        "Each item in 'sources' must be one of:",
                        "  • inspect.Parameter — created via inspect.Parameter(...) or create_keyword/positional_parameter()",
                        "  • callable          — a function, method, or lambda whose parameters will be extracted",
                        f"Got unsupported item: {item!r}",
                    ),
                    get_location = 2,
                    context      = "SignatureCreator._process_sources() — sources item type check",
                    exception    = TypeError,
                )


_DESIGN_NOTES = """
# ProcessSourcesMixin

## Purpose
Provides `_process_sources()` for `SignatureCreator` — iterates over all items
in `_sources` and routes each one to the correct handler. The entry point for
processing user-provided parameter sources.

## Routing logic
Each item in `_sources` is handled by one of three branches:
- `inspect.Parameter` — added directly to `_param_list` via `add()`.
- `callable`          — passed to `_process_func()` for parameter extraction.
- anything else       — raises `SignatureBuildError(TypeError)`.

The order of checks matters: `inspect.Parameter` is checked first because
it is also callable in some contexts — checking `callable()` first could
silently misroute a Parameter into `_process_func()`.

## Notes
- `context` is kept — it identifies the exact method and check within
  `SignatureCreator` where the error occurred.
- All parameter deduplication and exclusion logic is delegated to
  `ParameterCollector.add()` — this mixin only routes, it does not filter.
- The error message references `create_keyword/positional_parameter()` as
  the recommended way to create `inspect.Parameter` instances — corrected
  from the original which referenced a non-existent function name.
"""