"""
Tests for validate_if_sources_or_base_func_is_set — valid combinations, missing sources, and error fields.
"""
import inspect
import pytest
from simplibs.signature.signature_creator._validations.validate_if_sources_or_base_func_is_set import validate_if_sources_or_base_func_is_set
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Valid combinations
# -----------------------------------------------------------------------------

def test_base_func_alone_passes():
    """A base_func without sources must pass without raising."""
    def my_func(): ...
    validate_if_sources_or_base_func_is_set((), my_func)


def test_sources_alone_passes():
    """At least one add without base_func must pass without raising."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    validate_if_sources_or_base_func_is_set((param,), None)


def test_both_sources_and_base_func_passes():
    """Both sources and base_func provided must pass without raising."""
    def my_func(): ...
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    validate_if_sources_or_base_func_is_set((param,), my_func)


# -----------------------------------------------------------------------------
# Missing sources
# -----------------------------------------------------------------------------

def test_neither_sources_nor_base_func_raises():
    """Neither sources nor base_func must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError):
        validate_if_sources_or_base_func_is_set((), None)


def test_empty_sources_and_no_base_func_raises():
    """Empty sources tuple and no base_func must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError):
        validate_if_sources_or_base_func_is_set([], None)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields."""
    with pytest.raises(SignatureBuildError) as exc_info:
        validate_if_sources_or_base_func_is_set((), None)

    e = exc_info.value
    assert e.error_name == "SIGNATURE CREATOR ERROR"
    assert e.value_label == "sources / base_func"
    assert e.value is None
    assert isinstance(e, ValueError)