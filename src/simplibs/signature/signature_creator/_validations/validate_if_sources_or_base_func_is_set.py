# Commons
from ...utils import SignatureBuildError


def validate_if_sources_or_base_func_is_set(sources, base_func) -> None:
    """
    Validates that SignatureCreator received at least one parameter source.

    Usage:
        - SignatureCreator.__init__() — called before signature construction begins

    Raises:
        SignatureBuildError(ValueError): If neither `base_func` nor any `sources` were provided.
    """
    if not sources and base_func is None:
        raise SignatureBuildError(
            error_name  = "SIGNATURE CREATOR ERROR",
            value_label = "sources / base_func",
            value       = None,
            expected    = "at least one parameter source: `base_func` (callable) or one or more `sources` (Parameter, callable)",
            problem     = "SignatureCreator cannot build a signature — no parameter source was provided.",
            how_to_fix  = (
                "Pass a base function: SignatureCreator(base_func=my_func).",
                "Pass one or more sources: SignatureCreator(my_param) or SignatureCreator(my_func).",
                "Or combine both: SignatureCreator(my_param, base_func=my_func).",
            ),
            get_location = 2,
            context      = "SignatureCreator.__init__() — parameter source presence check",
            exception    = ValueError,
        )


_DESIGN_NOTES = """
# validate_if_sources_or_base_func_is_set

## Purpose
Validates that at least one parameter source was provided to `SignatureCreator`
— either a `base_func` or one or more `sources`. Without either, the signature
cannot be built at all.

## When it is called
- `SignatureCreator.__init__()` — called at the very start, before any
  signature construction begins.

## Notes
- `context` is kept — it identifies the exact class and the moment in the
  construction flow where the check occurs.
- `get_location=2` points the error to the caller's call site.
"""