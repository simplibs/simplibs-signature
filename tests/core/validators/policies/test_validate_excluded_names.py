"""
Tests for validate_excluded_names — validation of iterables, string items,
tuple conversion, and error metadata.
"""
import pytest
from simplibs.signature.core.validators._policies.validate_excluded_names import validate_excluded_names
from simplibs.signature.core.validators.exceptions import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values and Iterables
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value, expected_list", [
    ((), []),
    ([], []),
    (set(), []),
    (("param1",), ["param1"]),
    (["a", "b", "c"], ["a", "b", "c"]),
    ({"x", "y", "z"}, ["x", "y", "z"]),
    ((name for name in ["p1", "p2"]), ["p1", "p2"]),  # Generator
])
def test_valid_excluded_names_pass_and_return_tuple(value, expected_list):
    """Various iterables of strings must pass and return a tuple."""
    # Call validation first (it materializes the generator if needed)
    result = validate_excluded_names(value)

    assert isinstance(result, tuple)

    # Check length and content
    assert len(result) == len(expected_list)
    # Using sorted() for sets because order isn't guaranteed
    if isinstance(value, set):
        assert sorted(list(result)) == sorted(expected_list)
    else:
        assert list(result) == expected_list


# -----------------------------------------------------------------------------
# Invalid container types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    "param1",              # string (the "string trap")
    42,                    # int
    None,                  # None
    object(),              # object
])
def test_non_iterable_or_string_container_raises(value):
    """Non-iterables and raw strings must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_excluded_names(value)

    assert isinstance(exc_info.value, TypeError)
    assert "must be an iterable of strings" in str(exc_info.value.problem)


# -----------------------------------------------------------------------------
# Invalid item types within iterable
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    ("param1", 42, "param3"),
    ["param1", None],
    {"param1", 3.14},
    (item for item in ["valid", []]),
])
def test_invalid_item_type_raises(value):
    """An iterable containing any non-string item must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_excluded_names(value)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_container_error_fields_are_correct_for_non_iterables():
    """The raised exception for non-iterables must have correct metadata."""
    invalid_input = 123
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_excluded_names(invalid_input, "my_excludes")

    e = exc_info.value
    assert e.value == invalid_input
    assert e.value_label == "my_excludes"
    assert e.error_name == "INVALID ARGUMENT ERROR"


def test_item_error_fields_include_index():
    """The raised exception for bad item must include the index in value_label."""
    # Test fail-fast on index 1 (using a list)
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_excluded_names(["valid", 123, "next_invalid"], "excluded")

    e = exc_info.value
    assert e.value == 123
    assert e.value_label == "excluded[1]"
    assert "Item at index 1" in e.problem


def test_default_value_name_is_excluded_names():
    """When value_name is not provided, it should default to 'excluded_names'."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_excluded_names(None)

    assert exc_info.value.value_label == "excluded_names"