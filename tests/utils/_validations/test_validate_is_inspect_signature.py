"""
Tests for validate_is_inspect_signature — valid values, invalid types, and error fields.
"""
import inspect
import pytest
from simplibs.signature.utils._validations.validate_is_inspect_signature import validate_is_inspect_signature
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_inspect_signature_passes():
    """A proper inspect.Signature must pass without raising."""
    def my_func(x: int, y: str): ...
    validate_is_inspect_signature(inspect.signature(my_func), "signature")


def test_empty_signature_passes():
    """An empty inspect.Signature must pass without raising."""
    validate_is_inspect_signature(inspect.Signature(), "signature")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, "signature", None, [], {}])
def test_invalid_type_raises(value):
    """Any non-Signature value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_inspect_signature(value, "signature")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_inspect_signature("not_a_signature", "signature")

    e = exc_info.value
    assert e.value == "not_a_signature"
    assert e.value_label == "signature"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)