import inspect
from typing import Self, Callable, Any
# Outers
from ...utils import get_signature
from ...validators import SignatureBuildError


class ProcessParamSourcesMixin:
    """
    Mixin for iterating over various parameter sources and routing
    each item to the ParameterCollector.
    """

    def _process_param_sources(
        self: Self,
        param_sources: tuple[inspect.Parameter | Callable, ...],
        return_source: Any
    ) -> None:
        """
        Iterates over all items in `param_sources` and adds them to the internal collector.

        If a source item is also identified as the `return_source`, its
        return annotation is automatically captured to avoid redundant processing.

        Args:
            param_sources: A tuple containing inspect.Parameter objects or callables.
            return_source: The source designated for the return annotation.

        Raises:
            SignatureBuildError(TypeError): If an item is neither a Parameter nor a callable.
        """

        # Iterate over all items in the variadic param_sources
        for index, item in enumerate(param_sources):

            # 1. Processing inspect.Parameter — add directly to collector
            if isinstance(item, inspect.Parameter):
                self._params_collector.add_param(item)

            # 2. Processing callable — extract and add all its parameters
            elif callable(item):

                # 2.1 Get signature from the callable
                # Using validate=False since get_signature is trusted here
                signature = get_signature(item, validate=False)

                # 2.2 Add all parameters from the callable to the collector
                for param in signature.parameters.values():
                    self._params_collector.add_param(param)

                # 2.3 Check if this callable should also provide the return type
                # (Optimization: avoids re-calling get_signature in ProcessReturnSourceMixin)
                if return_source is item:
                    self._return_annotation = signature.return_annotation

            # 3. Exceptions for unsupported types
            else:
                raise SignatureBuildError(
                    error_name  = "INVALID PARAMETER SOURCE",
                    value_label = f"param_sources[{index}]",
                    value       = item,
                    expected    = "an inspect.Parameter or a callable (function/method)",
                    problem     = (
                        f"Item at index {index} is of type {type(item).__name__!r}, "
                        "which is not a valid source for parameters."
                    ),
                    how_to_fix  = (
                        "Ensure all positional arguments are either Parameter instances or callables.",
                        "If you are passing a list of sources, remember to unpack it: SignatureCreator(*my_list).",
                        "Use create_keyword_parameter() or create_positional_parameter() to build parameters.",
                    ),
                    context      = "SignatureCreator._process_param_sources()",
                    exception    = TypeError,
                )


_DESIGN_NOTES = """
# ProcessParamSourcesMixin

## Purpose
Acts as the primary "ingestion engine" for `SignatureCreator`. It abstracts
the complexity of handling mixed input types (individual parameters versus
existing callables) during parameter collection.

## Where it is used
- Called during `SignatureCreator.__init__()` in the parameter processing phase.
- Iterates through all `*param_sources` to feed the internal `ParameterCollector`.
- Optimizes return type extraction when possible (see step 2.3).

## The Hybrid Source Approach
The mixin supports two complementary source types:
1. **Granular**: `inspect.Parameter` objects are added directly, allowing
   surgical precision in signature building.
2. **Bulk**: `Callables` (functions/methods) are introspected to extract all
   their parameters at once, streamlining common use cases.

## Integration with ParameterCollector
The mixin does NOT decide whether a parameter is valid or where it belongs
in the sequence. It simply "feeds" parameters to `self._params_collector`.
This separation ensures:
- Rules like `excluded_names`, `include_binding`, and `accept_double` are
  centralized in the Collector.
- The mixin remains simple and focused on source routing.
- Changes to deduplication or filtering logic only affect one place.

## Optimization: Return-Source Shortcut (Step 2.3)
If `return_source` is the same object as one of the callables in
`param_sources`, we capture its `return_annotation` immediately. This
optimization avoids an expensive `inspect.signature()` call later in
`ProcessReturnSourceMixin`, improving performance when the pattern is used.

## Error Reporting with Index Precision
By using `enumerate(param_sources)`, the `SignatureBuildError` can pinpoint
exactly which argument caused failure (e.g., `param_sources[2]`), drastically
improving the developer experience when debugging.

## Exception Details
The `else` branch catches any item type that is neither `inspect.Parameter`
nor callable. This includes common mistakes:
- Passing a string parameter name instead of a Parameter object.
- Accidentally passing a tuple or list instead of unpacking it.
- Passing built-in types or non-callable singletons.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- All items in `param_sources` are processed in iteration order.
- The Collector handles deduplication and ordering rules independently.
- This mixin is exception-free if all inputs are valid (caught by earlier validation).
"""