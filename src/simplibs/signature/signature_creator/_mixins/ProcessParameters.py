from typing import Self


class ProcessParametersMixin:
    """Mixin for orchestrating parameter processing from base_func and sources in the correct order."""

    def _process_parameters(self: Self) -> None:
        """
        Orchestrates parameter processing from `base_func` and `sources`
        in the correct order.

        Processing order depends on the value of `_base_func_first`.
        """

        # 1. Only sources provided — process them and return early
        if self._base_func is None:
            self._process_sources()
            return

        # 2. Only base_func provided — process it and return early
        if not self._sources:
            self._process_func(self._base_func, is_base_func=True)
            return

        # 3. Both provided — order depends on base_func_first
        if self._base_func_first:
            self._process_func(self._base_func, is_base_func=True)
            self._process_sources()
        else:
            self._process_sources()
            self._process_func(self._base_func, is_base_func=True)


_DESIGN_NOTES = """
# ProcessParametersMixin

## Purpose
Provides `_process_parameters()` for `SignatureCreator` — the orchestrator
that decides in which order `base_func` and `sources` are processed. Contains
no parameter logic itself; delegates entirely to `_process_func()` and
`_process_sources()`.

## Processing flow
Three mutually exclusive cases, handled with early returns:

1. **No base_func** — only `sources` were provided. Process sources and return.
2. **No sources** — only `base_func` was provided. Process it and return.
3. **Both provided** — order is controlled by `_base_func_first`:
   - `True`  → base_func first, then sources.
   - `False` → sources first, then base_func.

## Why order matters
Parameter order in a signature is significant — it determines how arguments
are matched at call time. `base_func_first=True` (the default) places the
base function's parameters at the front, which is the natural expectation
when extending an existing function's signature with additional parameters.

## Notes
- Early returns in cases 1 and 2 avoid unnecessary condition nesting —
  the common single-source cases are handled cleanly before reaching
  the two-source branching logic.
- This mixin is a pure orchestrator — all actual parameter collection,
  exclusion, and deduplication logic lives in `ProcessFuncMixin`,
  `ProcessSourcesMixin`, and `ParameterCollector`.
"""