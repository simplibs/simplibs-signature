"""
Tests for validate_parameters_collection — verification of iterables,
Parameter items, tuple conversion, and error metadata.
"""
import pytest
import inspect
# Target function and exception
from simplibs.signature.core.validators._inspects.validate_parameters_collection import validate_parameters_collection
from simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values and Iterables
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("params", [
    (),  # Empty tuple
    [],  # Empty list
    (inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD),),
    [inspect.Parameter("y", inspect.Parameter.KEYWORD_ONLY)],
])
def test_valid_iterables_pass_and_return_tuple(params):
    """Any valid iterable of inspect.Parameter must pass and return a tuple."""
    result = validate_parameters_collection(params)

    assert isinstance(result, tuple)
    assert len(result) == len(params)
    for item in result:
        assert isinstance(item, inspect.Parameter)


def test_parameters_from_real_function_pass_directly():
    """
    Parameters extracted from a real function (dict_values) must pass
    without manual casting to tuple.
    """
    def my_func(a, b=10): pass
    sig = inspect.signature(my_func)

    # sig.parameters.values() is a 'dict_values' object, not a tuple
    result = validate_parameters_collection(sig.parameters.values())

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[0].name == "a"


def test_generator_exhaustion_is_handled():
    """
    A generator (one-time iterable) must be correctly materialized
    into a tuple and returned.
    """
    param = inspect.Parameter("gen", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    def my_gen():
        yield param

    result = validate_parameters_collection(my_gen())

    assert isinstance(result, tuple)
    assert result[0] == param


# -----------------------------------------------------------------------------
# Invalid container types (Non-iterables)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    42,             # int
    None,           # None
    object(),       # object
])
def test_non_iterable_raises(value):
    """Any non-iterable value must raise SignatureParameterError (TypeError)."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_parameters_collection(value)

    assert "must be iterable" in str(exc_info.value.problem)
    assert isinstance(exc_info.value, TypeError)


# -----------------------------------------------------------------------------
# Invalid item types within iterable
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("invalid_item", ["not_param", 42, None, {}, 3.14])
def test_invalid_item_type_raises(invalid_item):
    """An iterable containing any non-Parameter item must raise SignatureParameterError."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    # Testing with a list to ensure it's converted and then fails on item check
    with pytest.raises(SignatureParameterError):
        validate_parameters_collection([param, invalid_item])


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_container_error_fields_for_non_iterables():
    """The raised exception for non-iterables must have correct metadata."""
    invalid_input = 123
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_parameters_collection(invalid_input, "my_params")

    e = exc_info.value
    assert e.value == invalid_input
    assert e.value_label == "my_params"
    assert e.error_name == "INVALID ARGUMENT ERROR"


def test_item_error_fields_include_index_and_type():
    """The raised exception for bad item must include index and actual type name."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # Test fail-fast on index 2 (using a list)
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_parameters_collection([param, param, "invalid_item"], "params")

    e = exc_info.value
    assert e.value == "invalid_item"
    assert e.value_label == "params[2]"
    assert "str" in str(e.problem)
    assert e.error_name == "INVALID PARAMETER ITEM"


# -----------------------------------------------------------------------------
# Default parameter value
# -----------------------------------------------------------------------------

def test_default_value_name_is_parameters():
    """When value_name is not provided, it should default to 'parameters'."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_parameters_collection([1, 2, 3])

    assert exc_info.value.value_label == "parameters[0]"