"""
Tests for validate_is_callable — valid values, invalid types, and error fields.
"""
import pytest
from simplibs.signature.core.validators._primitives.validate_is_callable import validate_is_callable
from simplibs.signature.core.validators.exceptions import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

def test_function_passes():
    """A regular function must pass without raising."""
    def my_func(): ...
    validate_is_callable(my_func, "my_param")


def test_lambda_passes():
    """A lambda must pass without raising."""
    validate_is_callable(lambda x: x, "my_param")


def test_class_passes():
    """A class must pass without raising — classes are callable."""
    validate_is_callable(int, "my_param")


def test_callable_object_passes():
    """An object with __call__ must pass without raising."""
    class MyCallable:
        def __call__(self): ...
    validate_is_callable(MyCallable(), "my_param")


def test_builtin_function_passes():
    """Built-in functions must pass without raising."""
    validate_is_callable(len, "my_param")


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [42, "not_callable", None, [], {}])
def test_invalid_type_raises(value):
    """Any non-callable value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_callable(value, "my_param")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields and inherit from TypeError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_callable(42, "test_func")

    e = exc_info.value
    assert e.value == 42
    assert e.value_label == "test_func"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)


# -----------------------------------------------------------------------------
# Default parameter value
# -----------------------------------------------------------------------------

def test_default_value_name_is_function():
    """When value_name is not provided, it should default to 'function'."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_callable(123)

    e = exc_info.value
    assert e.value_label == "function"