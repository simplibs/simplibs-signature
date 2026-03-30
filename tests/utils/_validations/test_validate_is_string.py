"""
Tests for validate_is_string — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.utils._validations.validate_is_string import validate_is_string
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_string_passes():
    """A regular string must pass without raising."""
    validate_is_string("my_param", "name")


def test_empty_string_passes():
    """An empty string must pass without raising."""
    validate_is_string("", "name")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, None, [], {}, True])
def test_invalid_type_raises(value):
    """Any non-string value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_string(value, "name")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_string(42, "name")

    e = exc_info.value
    assert e.value == 42
    assert e.value_label == "name"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)