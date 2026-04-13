import inspect

# A pre-built inspect.Parameter representing *args
ARGS = inspect.Parameter(
    name="args",
    kind=inspect.Parameter.VAR_POSITIONAL,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty
)

_DESIGN_NOTES = """
# ARGS

## Purpose
A pre-built `inspect.Parameter` representing `*args` — captures any number
of positional arguments. Used as a ready-made constant wherever a VAR_POSITIONAL
parameter is needed in a signature.

## Technical Details
- **Kind**: `VAR_POSITIONAL` (the `*` prefix in Python).
- **Default**: Must always be `inspect.Parameter.empty`. Variadic parameters 
  cannot have default values in Python.
- **Annotation**: Set to `empty` by default. If annotated, it represents 
  the type of individual elements within the tuple.

## Position in a signature
Parameters must appear in this order for `inspect.Signature` to be valid:
    positional → *args → keyword-only → **kwargs

## Notes
- Import and use directly — no need to construct `inspect.Parameter` manually.
- The name `args` follows the Python convention for VAR_POSITIONAL parameters.
"""