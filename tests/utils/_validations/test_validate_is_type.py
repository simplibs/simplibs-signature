"""
Tests for validate_is_type — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.utils._validations.validate_is_type import validate_is_type
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_builtin_type_passes():
    """A built-in type must pass without raising."""
    validate_is_type(int, "annotation")


def test_custom_class_passes():
    """A custom class must pass without raising."""
    class MyClass: ...
    validate_is_type(MyClass, "annotation")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, "int", None, [], {}, True])
def test_invalid_type_raises(value):
    """Any non-type value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_type(value, "annotation")


def test_instance_raises():
    """An instance of a class must raise — only the class itself is valid."""
    with pytest.raises(SignatureParameterError):
        validate_is_type(int(), "annotation")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_type("int", "return_type")

    e = exc_info.value
    assert e.value == "int"
    assert e.value_label == "return_type"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)