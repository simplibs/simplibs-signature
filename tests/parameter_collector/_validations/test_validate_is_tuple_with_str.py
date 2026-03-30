"""
Tests for validate_is_tuple_with_str — valid values, invalid container types, invalid items, and error fields.
"""
import pytest
from simplibs.signature.parameter_collector._validations.validate_is_tuple_with_str import validate_is_tuple_with_str
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_tuple_of_strings_passes():
    """A tuple of strings must pass without raising."""
    validate_is_tuple_with_str(("self", "cls"), "excluded_names")


def test_empty_tuple_passes():
    """An empty tuple must pass without raising."""
    validate_is_tuple_with_str((), "excluded_names")


def test_single_item_tuple_passes():
    """A one-element tuple with a string must pass without raising."""
    validate_is_tuple_with_str(("self",), "excluded_names")


# -----------------------------------------------------------------------------
# Invalid container types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [["self", "cls"], {"self", "cls"}, "self", None, 42])
def test_non_tuple_raises(value):
    """Any non-tuple container must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_tuple_with_str(value, "excluded_names")


# -----------------------------------------------------------------------------
# Invalid items
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [(1, "cls"), ("self", None), ("self", 42, "cls")])
def test_non_string_item_raises(value):
    """A tuple containing any non-string item must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_tuple_with_str(value, "excluded_names")


# -----------------------------------------------------------------------------
# Error fields — invalid container
# -----------------------------------------------------------------------------

def test_error_fields_for_invalid_container():
    """The raised exception for a non-tuple must have correctly populated fields."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_tuple_with_str(["self"], "excluded_names")

    e = exc_info.value
    assert e.value == ["self"]
    assert e.value_label == "excluded_names"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)


# -----------------------------------------------------------------------------
# Error fields — invalid item
# -----------------------------------------------------------------------------

def test_error_fields_for_invalid_item():
    """The raised exception for an invalid item must report the correct index and value."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_tuple_with_str(("self", 42), "excluded_names")

    e = exc_info.value
    assert e.value == 42
    assert e.value_label == "excluded_names[1]"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)