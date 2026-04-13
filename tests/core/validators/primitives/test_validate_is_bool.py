"""
Tests for validate_is_bool — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.core.validators._primitives.validate_is_bool import validate_is_bool
from simplibs.signature.core.validators.exceptions import SignatureParameterError


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
    """The raised exception must have correctly populated fields and inherit from TypeError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_bool("not_a_bool", "base_func_first")

    e = exc_info.value
    assert e.value == "not_a_bool"
    assert e.value_label == "base_func_first"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)  # Simplified check