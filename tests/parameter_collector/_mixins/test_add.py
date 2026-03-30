"""
Tests for AddMixin — exclusion, duplicate handling, kind routing, and error fields.
"""
import inspect
import pytest
from simplibs.signature.parameter_collector.ParameterCollector import ParameterCollector
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


@pytest.fixture
def collector():
    return ParameterCollector()


@pytest.fixture
def strict_collector():
    return ParameterCollector(accept_double=False)


# -----------------------------------------------------------------------------
# Exclusion
# -----------------------------------------------------------------------------

def test_excluded_name_is_skipped(collector):
    """A parameter whose name is in excluded_names must be silently skipped."""
    collector.add(make_param("self"))
    assert "self" not in [p.name for p in collector.get_ordered()]


def test_custom_excluded_name_is_skipped():
    """A custom excluded name must be silently skipped."""
    collector = ParameterCollector(excluded_names=("my_param",))
    collector.add(make_param("my_param"))
    assert "my_param" not in [p.name for p in collector.get_ordered()]


# -----------------------------------------------------------------------------
# Duplicate handling
# -----------------------------------------------------------------------------

def test_duplicate_with_accept_double_true_is_skipped(collector):
    """A duplicate parameter with accept_double=True must be silently skipped."""
    collector.add(make_param("x"))
    collector.add(make_param("x"))
    assert len([p for p in collector.get_ordered() if p.name == "x"]) == 1


def test_duplicate_with_accept_double_false_raises(strict_collector):
    """A duplicate parameter with accept_double=False must raise SignatureBuildError."""
    strict_collector.add(make_param("x"))
    with pytest.raises(SignatureBuildError) as exc_info:
        strict_collector.add(make_param("x"))
    e = exc_info.value
    assert e.value == "x"
    assert e.error_name == "DUPLICATE PARAMETER ERROR"
    assert isinstance(e, ValueError)


# -----------------------------------------------------------------------------
# Kind routing
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("kind", [
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.KEYWORD_ONLY,
    inspect.Parameter.VAR_KEYWORD,
])
def test_all_valid_kinds_are_accepted(collector, kind):
    """All valid inspect.Parameter kinds must be accepted without raising."""
    collector.add(make_param("x", kind))
    assert "x" in [p.name for p in collector.get_ordered()]


# -----------------------------------------------------------------------------
# Successful add
# -----------------------------------------------------------------------------

def test_parameter_is_added(collector):
    """A valid parameter must be added and retrievable."""
    collector.add(make_param("x"))
    assert "x" in [p.name for p in collector.get_ordered()]


def test_name_is_recorded_after_add(collector):
    """After a successful add, the name must be recorded in _seen_names."""
    collector.add(make_param("x"))
    assert "x" in collector._seen_names