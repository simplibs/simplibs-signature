import inspect
# Outers
from .._constants.strings import WITHOUT_DEFAULT
from .._constants.kinds import VAR_POSITIONAL, VAR_KEYWORD


def _find_colliding_name(
    param: inspect.Parameter,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> str | None:
    """Find the stored parameter that a new parameter collides with.

    Args:
        param: The parameter that is about to be stored.
        seen_names: The name index of the collector.
        params_map: The tiered storage of the collector.

    Returns:
        The name of the stored parameter, or `None` if there is no collision.
        A collision is the same name, or a second `*args` / `**kwargs` under
        any other name.
    """

    # 1. The same name is always a collision
    if param.name in seen_names:
        return param.name

    # 2. A signature holds one variadic of each kind, whatever it is called
    if param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
        stored = params_map[param.kind][WITHOUT_DEFAULT]
        if stored:
            return stored[0].name

    # 3. Nothing in the way
    return None


_DESIGN_NOTES = """
# _find_colliding_name — Who Is Already Sitting There

## Purpose
`add_param` has one rule for "this parameter meets one that is already stored":
accept or refuse, keep or replace. This function decides *whether* they meet.

## Variadics Are One Slot Per Kind
`inspect.Signature` accepts `(*a, *b)` even with validation on, so nothing
downstream would catch it. Treating `*args` as one slot (and `**kwargs` as one)
gives the existing policy a meaning for them: refuse, keep the first, or let the
later one replace the earlier. Flat mode already behaves this way for `**kwargs`.

## Why the Stored Name Is Returned
The caller removes the stored parameter by name, and for a variadic that name
is not the name of the new parameter.
"""
