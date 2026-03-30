"""
Tests for KWARGS — type, name, and kind of the pre-built VAR_KEYWORD parameter.
"""
import inspect
from simplibs.signature.utils.constants.KWARGS import KWARGS


# -----------------------------------------------------------------------------
# Type
# -----------------------------------------------------------------------------

def test_kwargs_is_inspect_parameter():
    """KWARGS must be an instance of inspect.Parameter."""
    assert isinstance(KWARGS, inspect.Parameter)


# -----------------------------------------------------------------------------
# Name and kind
# -----------------------------------------------------------------------------

def test_kwargs_name_is_kwargs():
    """KWARGS must have the name 'kwargs'."""
    assert KWARGS.name == "kwargs"


def test_kwargs_kind_is_var_keyword():
    """KWARGS must be a VAR_KEYWORD parameter."""
    assert KWARGS.kind == inspect.Parameter.VAR_KEYWORD