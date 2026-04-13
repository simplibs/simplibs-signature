VARIADIC_NAMES = ("args", "kwargs")


_DESIGN_NOTES = """
# VARIADIC_NAMES

## Purpose
A tuple of parameter names that represent variadic parameters — `*args` and
`**kwargs`. Used as a canonical source of truth to identify and filter these
parameters when processing signatures.

## When it is used
- `validate_param_sources()` — checks that variadic parameters are not used
  as parameter sources (sources must be concrete parameters with defaults).
- `SignatureCreator` — ensures variadic names are handled consistently across
  signature building operations.

## Why tuple
`tuple` is immutable and matches the convention used in `BINDING_NAMES`.
Membership checks (`in` operator) are simple and readable for this small set.

## Notes
- These names represent the *actual names* of variadic parameters in Python
  (`*args` is a parameter named `args` with `kind=VAR_POSITIONAL`).
- User code should not reference this constant directly — it is an internal
  implementation detail.
- Complements `BINDING_NAMES` — together they form the set of "special"
  parameters that receive automated handling.
"""