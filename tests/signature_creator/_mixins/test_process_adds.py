"""
Tests for ProcessSourcesMixin — parameter routing, callable extraction, and error handling.
"""
import inspect
import pytest
from simplibs.signature.signature_creator.SignatureCreator import SignatureCreator
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


def func_with_x(x): ...
def func_with_y(y): ...
def func_with_xy(x, y): ...


# -----------------------------------------------------------------------------
# inspect.Parameter routing
# -----------------------------------------------------------------------------

def test_parameter_is_added_directly():
    """An inspect.Parameter in sources must be added directly to the signature."""
    param = make_param("x")
    sc = SignatureCreator(param)
    assert "x" in sc.signature.parameters


def test_multiple_parameters_are_all_added():
    """Multiple inspect.Parameter items must all appear in the signature."""
    sc = SignatureCreator(make_param("a"), make_param("b"), make_param("c"))
    names = list(sc.signature.parameters)
    assert names == ["a", "b", "c"]


# -----------------------------------------------------------------------------
# Callable routing
# -----------------------------------------------------------------------------

def test_callable_parameters_are_extracted():
    """A callable in sources must have its parameters extracted into the signature."""
    sc = SignatureCreator(func_with_x)
    assert "x" in sc.signature.parameters


def test_multiple_callables_are_all_extracted():
    """Parameters from multiple callables in sources must all appear in the signature."""
    sc = SignatureCreator(func_with_x, func_with_y)
    assert "x" in sc.signature.parameters
    assert "y" in sc.signature.parameters


def test_lambda_is_accepted_as_callable():
    """A lambda in sources must be treated as a callable and its parameters extracted."""
    sc = SignatureCreator(lambda z: None)
    assert "z" in sc.signature.parameters


# -----------------------------------------------------------------------------
# Mixed routing
# -----------------------------------------------------------------------------

def test_parameter_and_callable_combined():
    """A mix of inspect.Parameter and callable in sources must all be added to the signature."""
    sc = SignatureCreator(make_param("a"), func_with_y)
    assert "a" in sc.signature.parameters
    assert "y" in sc.signature.parameters


# -----------------------------------------------------------------------------
# Unsupported item type
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("bad_item", [42, "string", 3.14, True, None, [1, 2], {"k": "v"}])
def test_unsupported_item_raises(bad_item):
    """Any item that is neither inspect.Parameter nor callable must raise SignatureBuildError."""
    param = make_param("x")
    with pytest.raises(SignatureBuildError):
        SignatureCreator(param, bad_item)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_for_unsupported_item():
    """The raised exception for an unsupported item must have correctly populated fields."""
    bad = 99
    param = make_param("x")
    with pytest.raises(SignatureBuildError) as exc_info:
        SignatureCreator(param, bad)
    e = exc_info.value
    assert e.value == bad
    assert e.value_label == "sources"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)