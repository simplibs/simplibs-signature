EXCLUDED = frozenset({"self", "cls"})


_DESIGN_NOTES = """
# EXCLUDED

## Purpose
A frozenset of parameter names that are automatically skipped when collecting
or copying signatures. Contains the binding parameters `self` and `cls` —
specific to class methods and not meaningful in a standalone function signature.

## When it is used
- `create_copy_signature()` — removes the binding parameter during normalisation.
- `ParameterCollector.__init__()` — the default starting set of names to skip,
  always present regardless of user-provided `excluded_names`.

## Why frozenset
`frozenset` is immutable and supports O(1) membership checks — both properties
are desirable for a constant that is used as a default exclusion set.

## Notes
- User-provided `excluded_names` in `ParameterCollector` extend this set,
  never replace it — `self` and `cls` are always excluded.
"""