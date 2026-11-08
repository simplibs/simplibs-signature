import inspect
from typing import Any
from simplibs.validate import validate_call


@validate_call
def replace_return_annotation_in_signature(
    signature: inspect.Signature,
    new_return_annotation: Any,
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    """Create a new signature with another return annotation.

    Args:
        signature: The signature to start from.
        new_return_annotation: The new annotation: a type, a string, `None`, or
            `inspect.Signature.empty` to remove it.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A new `inspect.Signature` with the same parameters.
    """

    # 1. Same parameters, new return annotation
    return signature.replace(
        return_annotation=new_return_annotation
    )


_DESIGN_NOTES = """
# replace_return_annotation_in_signature — Change Only the Return Type

## Purpose
`signature.replace(return_annotation=...)` is one line, and this function is a
named one: it says what is being done, and it is the counterpart of
`add_params_to_signature` and `delete_params_from_signature` for the part of a
signature that is not a parameter.

## Any Annotation Goes
The value is not interpreted. `None` is a real annotation (a function that
returns nothing); `inspect.Signature.empty` is the way to say "no annotation".
"""
