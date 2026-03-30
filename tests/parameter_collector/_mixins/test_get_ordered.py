"""
Tests for GetOrderedMixin — order, empty state, and multi-kind ordering.
"""
import inspect
import pytest
from simplibs.signature.parameter_collector.ParameterCollector import ParameterCollector


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


@pytest.fixture
def collector():
    return ParameterCollector()


# -----------------------------------------------------------------------------
# Empty state
# -----------------------------------------------------------------------------

def test_empty_collector_returns_empty_list(collector):
    """get_ordered() must return an empty list when no parameters have been added."""
    assert collector.get_ordered() == []


# -----------------------------------------------------------------------------
# Return type
# -----------------------------------------------------------------------------

def test_returns_list(collector):
    """get_ordered() must return a list."""
    assert isinstance(collector.get_ordered(), list)


def test_returns_inspect_parameters(collector):
    """All items in the returned list must be inspect.Parameter instances."""
    collector.add(make_param("x"))
    assert all(isinstance(p, inspect.Parameter) for p in collector.get_ordered())


# -----------------------------------------------------------------------------
# Ordering
# -----------------------------------------------------------------------------

def test_parameters_are_returned_in_kind_order(collector):
    """Parameters must be returned in inspect-defined kind order regardless of insertion order."""
    collector.add(make_param("kw",  inspect.Parameter.KEYWORD_ONLY))
    collector.add(make_param("pos", inspect.Parameter.POSITIONAL_ONLY))
    collector.add(make_param("x",   inspect.Parameter.POSITIONAL_OR_KEYWORD))

    ordered = collector.get_ordered()
    kinds = [p.kind for p in ordered]

    assert kinds == sorted(kinds, key=lambda k: k.value)


def test_all_five_kinds_are_ordered_correctly(collector):
    """All five parameter kinds must appear in the correct inspect-defined order."""
    collector.add(make_param("vk",  inspect.Parameter.VAR_KEYWORD))
    collector.add(make_param("kw",  inspect.Parameter.KEYWORD_ONLY))
    collector.add(make_param("vp",  inspect.Parameter.VAR_POSITIONAL))
    collector.add(make_param("pk",  inspect.Parameter.POSITIONAL_OR_KEYWORD))
    collector.add(make_param("po",  inspect.Parameter.POSITIONAL_ONLY))

    names = [p.name for p in collector.get_ordered()]
    assert names == ["po", "pk", "vp", "kw", "vk"]