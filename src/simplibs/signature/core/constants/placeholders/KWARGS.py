import inspect

# A pre-built inspect.Parameter representing **kwargs
KWARGS = inspect.Parameter(
    name="kwargs",
    kind=inspect.Parameter.VAR_KEYWORD,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty
)

_DESIGN_NOTES = """
# KWARGS

## Purpose
A pre-built `inspect.Parameter` representing `**kwargs` — captures any number
of keyword arguments. Used as a ready-made constant wherever a VAR_KEYWORD
parameter is needed in a signature.

## Technical Details
- **Kind**: `VAR_KEYWORD` (the `**` prefix in Python).
- **Default**: Must always be `inspect.Parameter.empty`. Variadic parameters 
  cannot have default values in Python.
- **Annotation**: Set to `empty` by default. If annotated, it represents 
  the type of values within the dictionary.

## Position in a signature
`**kwargs` is always the last parameter in a valid signature:
    positional → *args → keyword-only → **kwargs

## Notes
- Import and use directly — no need to construct `inspect.Parameter` manually.
- The name `kwargs` follows the Python convention for VAR_KEYWORD parameters.
- Used internally by `create_copy_signature()` when `normalize=True` —
  appended automatically to normalised signatures.
- Typically exported alongside `ARGS` as the pair of built-in variadic placeholders.
"""