import inspect


def _remove_param(
    name: str,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    """Remove a stored parameter, and forget its name.

    Args:
        name: The name of the stored parameter. An unknown name does nothing.
        seen_names: The name index of the collector (changed in place).
        params_map: The tiered storage of the collector (changed in place).
    """

    # 1. Unknown name, nothing to remove
    if name not in seen_names:
        return

    # 2. Forget the name, and take the parameter out of its tier
    kind_key, default_key = seen_names.pop(name)
    params_map[kind_key][default_key] = [
        p for p in params_map[kind_key][default_key]
        if p.name != name
    ]


_DESIGN_NOTES = """
# _remove_param — Take One Out of the Storage

## Purpose
The only place a stored parameter is removed. Used when a later parameter
replaces an earlier one.

## Why It Forgets the Name
The name index and the storage have to say the same thing. When a second
`*b` replaces a stored `*a`, the name `a` must stop being "seen", or a later
real parameter `a` would be taken for a duplicate. The index tells which tier
to look in, so removal never scans the whole map.
"""
