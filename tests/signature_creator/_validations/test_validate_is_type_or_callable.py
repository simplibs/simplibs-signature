"""
Tests for validate_is_type_or_callable — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.signature_creator._validations.validate_is_type_or_callable import validate_is_type_or_callable
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_type_passes():
    """A plain type must pass without raising."""
    validate_is_type_or_callable(int, "return_type")


def test_custom_class_passes():
    """A custom class must pass without raising."""
    class MyClass: ...
    validate_is_type_or_callable(MyClass, "return_type")


def test_function_passes():
    """A regular function must pass without raising."""
    def my_func() -> int: ...
    validate_is_type_or_callable(my_func, "return_type")


def test_lambda_passes():
    """A lambda must pass without raising."""
    validate_is_type_or_callable(lambda: None, "return_type")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, "int", 3.14, [], {}])
def test_invalid_type_raises(value):
    """A non-type, non-callable value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_type_or_callable(value, "return_type")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_type_or_callable(42, "return_type")

    e = exc_info.value
    assert e.value == 42
    assert e.value_label == "return_type"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)