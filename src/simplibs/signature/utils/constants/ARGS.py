import inspect


ARGS = inspect.Parameter(
    name = "args",
    kind = inspect.Parameter.VAR_POSITIONAL,
)


_DESIGN_NOTES = """
# ARGS

## Purpose
A pre-built `inspect.Parameter` representing `*args` — captures any number
of positional arguments. Used as a ready-made constant wherever a VAR_POSITIONAL
parameter is needed in a signature.

## Position in a signature
Parameters must appear in this order for `inspect.Signature` to be valid:
    positional → *args → keyword-only → **kwargs

## Notes
- Import and use directly — no need to construct `inspect.Parameter` manually.
- The name `args` follows the Python convention for VAR_POSITIONAL parameters.
"""