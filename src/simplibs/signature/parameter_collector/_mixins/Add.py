import inspect
from typing import Self
# Commons
from ...utils import SignatureBuildError


class AddMixin:
    """Mixin for adding parameters to the internal storage with exclusion and duplicate handling."""

    def add(
        self: Self,
        param: inspect.Parameter
    ) -> None:
        """
        Sources a parameter to the storage.

        The parameter is skipped if its name is in `_excluded_names` or has
        already been added. On duplicate with `accept_double=False`, raises.

        Args:
            param: The parameter to add.

        Raises:
            SignatureBuildError(ValueError): If the parameter is a duplicate
                                             and `accept_double` is False.
            SignatureBuildError(TypeError):  If the parameter kind is unknown.
        """

        # 1. Check whether the parameter should be skipped
        if param.name in self._excluded_names:
            return

        # 2. Check for duplicates
        if param.name in self._seen_names:
            if not self._accept_double:
                raise SignatureBuildError(
                    error_name  = "DUPLICATE PARAMETER ERROR",
                    value_label = "param.name",
                    value       = param.name,
                    expected    = "a parameter with a unique name",
                    problem     = f"Parameter '{param.name}' was already added to the signature.",
                    how_to_fix  = (
                        "Make sure each parameter has a unique name.",
                        "If duplicate parameters are intentional, set accept_double=True.",
                    ),
                    get_location = 2,
                    context      = "ParameterCollector.add() — duplicate parameter check",
                    exception    = ValueError,
                )
            return

        # 3. Add the parameter to the appropriate list
        try:
            param: inspect.Parameter
            self._param_list[param.kind].append(param)
        except KeyError:
            raise SignatureBuildError(
                error_name  = "INVALID PARAMETER KIND ERROR",
                value_label = "param.kind",
                value       = param.kind,
                expected    = "a valid inspect._ParameterKind value",
                problem     = f"Parameter '{param.name}' has an unknown kind: {param.kind!r}.",
                how_to_fix  = (
                    "Use a valid inspect.Parameter kind:",
                    "  • inspect.Parameter.POSITIONAL_ONLY",
                    "  • inspect.Parameter.POSITIONAL_OR_KEYWORD",
                    "  • inspect.Parameter.VAR_POSITIONAL",
                    "  • inspect.Parameter.KEYWORD_ONLY",
                    "  • inspect.Parameter.VAR_KEYWORD",
                ),
                get_location = 2,
                context      = "ParameterCollector.add() — parameter kind check",
                exception    = TypeError,
            ) from None

        # 4. Record the parameter name as seen
        self._seen_names.add(param.name)


_DESIGN_NOTES = """
# AddMixin

## Purpose
Provides the `add()` method for `ParameterCollector` — the single entry point
for adding parameters to the internal storage. Handles three concerns in order:
exclusion, duplicate detection, and kind-based routing.

## Processing flow
1. **Exclusion check** — if the parameter name is in `_excluded_names`, the
   parameter is silently skipped. No error is raised.
2. **Duplicate check** — if the name was already seen:
   - `accept_double=True`  → silently skipped.
   - `accept_double=False` → raises `SignatureBuildError(ValueError)`.
3. **Kind routing** — the parameter is appended to the appropriate list in
   `_param_list`, keyed by `param.kind`. If the kind is not a recognised
   `inspect._ParameterKind` value, raises `SignatureBuildError(TypeError)`.
4. **Name recording** — the parameter name is added to `_seen_names` only
   after a successful insertion, ensuring the seen set stays consistent.

## Why from None in step 3
`from None` suppresses the original `KeyError` from the chained traceback —
the `SignatureBuildError` is the complete and sufficient error message.
Showing the `KeyError` alongside it would add noise without useful context.

## Notes
- `context` is kept in both raises — it identifies the exact method and check
  within `ParameterCollector` where the error occurred.
- `_excluded_names` and `_seen_names` are sets — membership checks are O(1).
- Step 4 is intentionally after step 3 — the name is recorded only on
  successful insertion, never on a skipped or failed add.
"""