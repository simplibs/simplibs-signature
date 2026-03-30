import inspect
from typing import Self
# Commons
from ...utils import get_signature


class ResolveReturnTypeMixin:
    """Mixin for finalising the return type into a form suitable for inspect.Signature."""

    def _resolve_return_type(self: Self) -> None:
        """
        Finalises `_return_type` into a form suitable for inspect.Signature.

        If the return type is a callable, replaces it with its return annotation.
        If no return type was provided at all, sets inspect.Signature.empty.
        """

        # 1. Return type is a type or None — nothing to change
        if isinstance(self._return_type, type) or self._return_type is None:
            return

        # 2. Return type is a callable — extract its return annotation
        if callable(self._return_type):
            signature = get_signature(self._return_type)
            self._return_type = signature.return_annotation
            return

        # 3. Return type was not provided at all — set to empty
        self._return_type = inspect.Signature.empty


_DESIGN_NOTES = """
# ResolveReturnTypeMixin

## Purpose
Provides `_resolve_return_type()` for `SignatureCreator` — the final
normalisation step that converts `_return_type` into a value that
`inspect.Signature` can accept directly. Called as the last step before
the signature is assembled.

## The four states of _return_type entering this method
After `_process_parameters()` runs, `_return_type` can be in one of
four states — this method handles each:

| State                        | Handled by | Result                              |
|------------------------------|------------|-------------------------------------|
| A type (e.g. `int`, `MyClass`) | Step 1   | Passed through unchanged            |
| `None`                       | Step 1     | Passed through — sets annotation to None (-> None) |
| A callable                   | Step 2     | Replaced with its return annotation |
| `UNSET` with no base_func    | Step 3     | Set to `inspect.Signature.empty`    |

## Why UNSET reaches step 3
If no `return_type` was provided and no `base_func` was given (or `base_func`
had no return annotation), `_return_type` remains `UNSET` after
`_process_parameters()`. Step 3 converts this to `inspect.Signature.empty`
— the standard Python sentinel for "no return annotation".

## Why None is passed through in step 1
`None` is an explicit user signal: "set the return annotation to None (-> None)".
It is a valid intentional value, not a missing one — `-> None` is standard Python
for functions that return nothing. Treating it differently from a type would be incorrect.

## Notes
- `get_signature()` in step 2 is called with default `validate=True` —
  the callable has already been validated upstream, but the check is cheap
  and consistent with the library-wide pattern.
- Early returns in steps 1 and 2 keep the branches flat and readable —
  step 3 is reached only when neither condition matched.
"""