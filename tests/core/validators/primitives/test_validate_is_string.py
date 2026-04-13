"""
Tests for validate_is_string — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.core.validators._primitives.validate_is_string import validate_is_string
from simplibs.signature.core.validators.exceptions import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["my_string", "", "name with spaces", "_private"])
def test_valid_strings_pass(value):
    """Any valid string (empty, with spaces or underscores) must pass."""
    validate_is_string(value, "my_param")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, 3.14, None, [], {}, True])
def test_invalid_type_raises(value):
    """Any non-string value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_string(value, "my_param")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields and inherit from TypeError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_string(123, "param_name")

    e = exc_info.value
    assert e.value == 123
    assert e.value_label == "param_name"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)


# -----------------------------------------------------------------------------
# Default parameter value
# -----------------------------------------------------------------------------

def test_default_value_name_is_name():
    """When value_name is not provided, it should default to 'name'."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_string(42)

    e = exc_info.value
    assert e.value_label == "name"