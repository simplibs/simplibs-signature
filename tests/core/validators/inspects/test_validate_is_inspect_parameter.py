"""
Tests for validate_is_inspect_parameter — type validation and error details.
"""
import pytest
import inspect

from simplibs.signature.core.validators._inspects.validate_is_inspect_parameter import (
    validate_is_inspect_parameter,
)
from simplibs.signature.core.validators.exceptions import SignatureBuildError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_valid_inspect_parameter_passes():
    """A valid inspect.Parameter instance must pass."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    validate_is_inspect_parameter(param)


# -----------------------------------------------------------------------------
# Invalid values
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    42,
    "string",
    None,
    object(),
    lambda x: x,
    inspect.Signature(),  # similar but wrong type
])
def test_invalid_values_raise(value):
    """Non-Parameter values must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError):
        validate_is_inspect_parameter(value)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must contain correct metadata."""
    bad_value = "not_a_parameter"

    with pytest.raises(SignatureBuildError) as exc_info:
        validate_is_inspect_parameter(bad_value)

    e = exc_info.value

    assert e.value == bad_value
    assert e.value_label == "param"
    assert e.error_name == "INVALID PARAMETER TYPE"
    assert "inspect.parameter" in str(e.expected).lower()
    assert isinstance(e, TypeError)


# -----------------------------------------------------------------------------
# Custom value_name
# -----------------------------------------------------------------------------

def test_custom_value_name_is_used():
    """Custom value_name must be reflected in the error."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_is_inspect_parameter(123, value_name="my_param")

    e = exc_info.value
    assert e.value_label == "my_param"