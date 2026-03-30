"""
Tests for ARGS — type, name, and kind of the pre-built VAR_POSITIONAL parameter.
"""
import inspect
from simplibs.signature.utils.constants.ARGS import ARGS


# -----------------------------------------------------------------------------
# Type
# -----------------------------------------------------------------------------

def test_args_is_inspect_parameter():
    """ARGS must be an instance of inspect.Parameter."""
    assert isinstance(ARGS, inspect.Parameter)


# -----------------------------------------------------------------------------
# Name and kind
# -----------------------------------------------------------------------------

def test_args_name_is_args():
    """ARGS must have the name 'args'."""
    assert ARGS.name == "args"


def test_args_kind_is_var_positional():
    """ARGS must be a VAR_POSITIONAL parameter."""
    assert ARGS.kind == inspect.Parameter.VAR_POSITIONAL