"""
Tests for validate_param_sources — source types, emptiness, and error fields.
"""
import pytest
import inspect
from simplibs.signature.core.validators._rules.validate_param_sources import validate_param_sources
from simplibs.signature.core.validators.exceptions import SignatureBuildError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("source", [
    (inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD),),
    (lambda x: x,),
    (len,),
    (int,),  # Class
])
def test_single_valid_source_passes(source):
    """Single valid parameter sources (Parameter or callable) must pass."""
    validate_param_sources(source)


def test_mixed_valid_sources_pass():
    """Mix of parameters and various callables must pass."""
    class MyCallable:
        def __call__(self): ...

    sources = (
        inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        lambda y: y,
        MyCallable()
    )
    validate_param_sources(sources)


# -----------------------------------------------------------------------------
# Empty sources
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("empty_value", [(), []])
def test_empty_sources_raise(empty_value):
    """An empty container must raise SignatureBuildError (ValueError)."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_param_sources(empty_value)

    assert isinstance(exc_info.value, ValueError)


# -----------------------------------------------------------------------------
# Invalid item types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("invalid_item", [42, "not_a_source", None, {}, 3.14])
def test_invalid_item_type_raises(invalid_item):
    """Any item that is neither Parameter nor callable must raise SignatureBuildError (TypeError)."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_param_sources((invalid_item,))

    assert isinstance(exc_info.value, TypeError)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_empty_error_fields_are_correct():
    """The raised exception for empty sources must have correct metadata."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_param_sources((), "my_sources")

    e = exc_info.value
    assert e.value == ()
    assert e.value_label == "my_sources"
    assert e.error_name == "SIGNATURE CREATOR ERROR"


def test_invalid_item_error_fields_include_index_and_type():
    """The raised exception for bad item must include index and actual type name."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # Test fail-fast on index 1
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_param_sources((param, "invalid_string"), "sources")

    e = exc_info.value
    assert e.value == "invalid_string"
    assert e.value_label == "sources[1]"
    assert "str" in str(e.problem)
    assert e.error_name == "INVALID PARAMETER SOURCE"


# -----------------------------------------------------------------------------
# Default parameter value
# -----------------------------------------------------------------------------

def test_default_value_name_is_param_sources():
    """When value_name is not provided, it should default to 'param_sources'."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_param_sources(())

    assert exc_info.value.value_label == "param_sources"