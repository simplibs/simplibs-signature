"""
Tests for validate_is_bool — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.utils._validations.validate_is_bool import validate_is_bool
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_true_passes():
    """True must pass without raising."""
    validate_is_bool(True, "my_param")


def test_false_passes():
    """False must pass without raising."""
    validate_is_bool(False, "my_param")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [1, 0, "true", "false", None, [], {}])
def test_invalid_type_raises(value):
    """Any non-bool value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_bool(value, "my_param")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_bool("true", "base_func_first")

    e = exc_info.value
    assert e.value == "true"
    assert e.value_label == "base_func_first"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)