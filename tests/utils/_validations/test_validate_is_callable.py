"""
Tests for validate_is_callable — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.utils._validations.validate_is_callable import validate_is_callable
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_function_passes():
    """A regular function must pass without raising."""
    def my_func(): ...
    validate_is_callable(my_func, "my_param")


def test_lambda_passes():
    """A lambda must pass without raising."""
    validate_is_callable(lambda x: x, "my_param")


def test_class_passes():
    """A class must pass without raising — classes are callable."""
    validate_is_callable(int, "my_param")


def test_callable_object_passes():
    """An object with __call__ must pass without raising."""
    class MyCallable:
        def __call__(self): ...
    validate_is_callable(MyCallable(), "my_param")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, "func", None, [], {}])
def test_invalid_type_raises(value):
    """Any non-callable value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_callable(value, "my_param")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_callable(42, "function")

    e = exc_info.value
    assert e.value == 42
    assert e.value_label == "function"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)