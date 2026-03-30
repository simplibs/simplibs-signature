from typing import Self, Callable
from simplibs.sentinels import UNSET
# Commons
from ...utils import get_signature


class ProcessFuncMixin:
    """Mixin for extracting parameters and return type from a callable."""

    def _process_func(
        self: Self,
        func: Callable,
        is_base_func: bool = False
    ) -> None:
        """
        Processes a callable's parameters and optionally resolves the return type.

        The return type is set if `func` is explicitly passed as `return_type`,
        or if it is the `base_func` and no `return_type` was provided.
        """

        # 1. Retrieve the signature
        signature = get_signature(func)

        # 2. Add all parameters
        for param in signature.parameters.values():
            self._param_list.add(param)

        # 3. Check whether this function should also provide the return type
        if (
            # 3.1 The function is explicitly set as the return type source
            self._return_type is func
            # 3.2 No return type was set, but this is base_func — inherit its return type
            or (is_base_func and self._return_type is UNSET)
        ):
            # 3.3 Inherit the return type from the function's signature
            self._return_type = signature.return_annotation


_DESIGN_NOTES = """
# ProcessFuncMixin

## Purpose
Provides `_process_func()` for `SignatureCreator` — extracts parameters from
a callable and optionally resolves the return type from its signature.
Called for both `base_func` and items in `sources` that are callables.

## Two responsibilities in one method
The method handles parameters and return type in a single pass over the
signature — retrieving the signature twice would be wasteful, and splitting
into two methods would require passing the signature between them. One method
with a clear two-part flow is the natural solution here.

## Return type resolution logic
The return type is inherited from the function in two cases:

- `self._return_type is func` — the user explicitly passed a callable as
  `return_type` in `SignatureCreator.__init__()`. This signals: "use the
  return annotation of this specific function."
- `is_base_func and self._return_type is UNSET` — no return type was
  provided at all, and this is the `base_func`. The base function's return
  annotation becomes the default.

In all other cases the return type is left unchanged.

## Why is_base_func is a parameter
The same method handles both `base_func` and `sources` callables — `is_base_func`
distinguishes between them without needing a separate method. Only `base_func`
triggers the UNSET inheritance logic.

## Notes
- `get_signature()` is called with default `validate=True` — the callable
  has already been validated upstream in `SignatureCreator.__init__()`, but
  `get_signature` is cheap and the safety is worth it.
- Parameters are added via `self._param_list.add()` — all exclusion and
  duplicate handling is delegated to `ParameterCollector`.
"""