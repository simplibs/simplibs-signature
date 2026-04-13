import inspect
from inspect import isclass
from typing import Self, Any
from simplibs.sentinels import UNSET
# Outers
from ...utils import get_signature


class ProcessReturnSourceMixin:
    """Mixin for finalizing the return type into a form suitable for inspect.Signature."""

    def _process_return_source(
        self: Self,
        return_source: Any
    ) -> None:
        """
        Finalizes `_return_annotation` into a form suitable for inspect.Signature.

        Resolves the return source into a valid annotation. Since Python allows
        almost any object to be used as a type hint/annotation, this process
        is designed to be permissive and fail-safe.

        Logic:
        1. If UNSET: Defaults to inspect.Signature.empty.
        2. If Callable (and not a Type/Typing construct): Extracts return_annotation.
        3. Else: Treats the source as a direct annotation (Type, None, String, etc.).

        Args:
            return_source: The source to extract the return annotation from.
        """

        # 1. Process UNSET (No source provided)
        if return_source is UNSET:
            self._return_annotation = inspect.Signature.empty

        # 2. Process callable, but ONLY if it's NOT a class AND NOT a typing object
        # In modern Python, classes and typing constructs (Union, Optional) can be
        # callable, but they do not provide a meaningful signature for extraction.
        # We check for __origin__ to identify generic typing aliases.
        elif (
            callable(return_source)
            and not isclass(return_source)
            and not hasattr(return_source, "__origin__")
        ):
            signature = get_signature(return_source, validate=False)
            self._return_annotation = signature.return_annotation

        # 3. Fallback for types, typing constructs (Union, Optional), and strings
        # This branch accepts the source as the final annotation directly.
        else:
            self._return_annotation = return_source


_DESIGN_NOTES = """
# ProcessReturnSourceMixin

## Purpose
Resolves the final `return_annotation` for `SignatureCreator`. Provides a
flexible interface where users can pass a type directly, or a function to
automatically mirror its return type.

## Where it is used
- Called during `SignatureCreator.__init__()` to finalize return type resolution.
- Executes after `_process_param_sources()` if the return annotation wasn't
  captured during parameter extraction.

## The "Everything is an Annotation" Philosophy
In Python's `inspect.Signature`, the `return_annotation` is not strictly
validated to be a `type`. It can be:
- A type object: `int`, `str`, `MyClass`
- A string (forward reference): `"MyClass"`
- Special values: `None`, `inspect.Signature.empty`
- A typing construct: `list[str]`, `Union[int, str]`, `Optional[Any]`
- Even arbitrary custom objects

Because of this flexibility, the `else` branch acts as a universal sink that
accepts any value that is not `UNSET` or a signature-providing callable.

## Handling Callable Ambiguity
Python types (classes) and `typing` constructs (like `Union[int, str]`) are 
technically callable but should be treated as direct annotations, not sources 
for signature extraction. 
The mixin uses a three-tier check:
1. `callable()`: Must be callable to be a signature source.
2. `not isclass()`: Excludes standard types/classes (e.g., `int`).
3. `not hasattr(..., "__origin__")`: Excludes `typing` aliases (e.g., `Optional`).

## Processing Steps
1. **UNSET Detection**: User did not provide a return annotation — default to empty.
2. **Signature Extraction**: If a genuine function/method is provided, its 
   return hint is extracted.
3. **Direct Annotation**: Fallback for types, strings, and complex typing objects.

## Exception Safety & Performance
This method is exception-free under normal operation:
1. `UNSET` is a controlled internal sentinel.
2. `callable()` and `hasattr()` are robust and never raise.
3. `get_signature()` carries its own internal error handling.
4. The `else` branch is a simple assignment.

## Compatibility with typing Module
By filtering out objects with `__origin__`, we ensure that `Union`, `List`, 
`Optional`, etc., are preserved as annotations rather than being introspected 
for non-existent signatures. This ensures full compatibility with PEP 484/585.

## Relationship with SignatureCreator
This mixin is the final step in return type resolution. It executes after
`_process_param_sources()` to ensure the signature always has a valid (possibly
empty) return annotation, regardless of the input path taken.

## Notes
- `_return_annotation` is initialized to `UNSET` in `SignatureCreator.__init__()`.
- If already set during parameter extraction (optimization), this method is skipped.
- The result is always a valid annotation for `inspect.Signature`.
"""