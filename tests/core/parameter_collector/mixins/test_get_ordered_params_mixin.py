"""
Tests for GetOrderedParamsMixin.get_ordered_params() — ordering, flattening, and tiered storage.
"""
import pytest
import inspect
from simplibs.signature.core.parameter_collector._mixins import GetOrderedParamsMixin


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

class MockOrderedCollector(GetOrderedParamsMixin):
    """Minimal implementation of a collector for testing the ordering mixin."""

    _WITHOUT_DEFAULT = "no_default"
    _CONTAIN_DEFAULT = "default"

    def __init__(self):
        # Initialized in the strict legal order as defined in ParameterCollector
        # BUT with the new tiered category structure
        self._params_map = {
            kind: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []}
            for kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.VAR_KEYWORD
            )
        }

def make_p(name, kind, has_default=False):
    """Short helper to create parameters."""
    default = "value" if has_default else inspect.Parameter.empty
    return inspect.Parameter(name, kind, default=default)

@pytest.fixture
def ordered_collector():
    return MockOrderedCollector()


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

def test_get_ordered_params_empty(ordered_collector):
    """Should return an empty tuple if no parameters are stored."""
    result = ordered_collector.get_ordered_params()
    assert isinstance(result, tuple)
    assert len(result) == 0


def test_get_ordered_params_correct_kind_sequence(ordered_collector):
    """
    Should return parameters in the strict Python order of KINDS.
    """
    p_kwarg = make_p("kwargs", inspect.Parameter.VAR_KEYWORD)
    p_arg = make_p("args", inspect.Parameter.VAR_POSITIONAL)
    p_pos = make_p("pos", inspect.Parameter.POSITIONAL_ONLY)

    # Manually fill the map in 'wrong' order (routing to correct categories)
    ordered_collector._params_map[inspect.Parameter.VAR_KEYWORD][ordered_collector._WITHOUT_DEFAULT].append(p_kwarg)
    ordered_collector._params_map[inspect.Parameter.VAR_POSITIONAL][ordered_collector._WITHOUT_DEFAULT].append(p_arg)
    ordered_collector._params_map[inspect.Parameter.POSITIONAL_ONLY][ordered_collector._WITHOUT_DEFAULT].append(p_pos)

    result = ordered_collector.get_ordered_params()

    # Expected order: POS_ONLY -> VAR_POS -> VAR_KW
    assert result == (p_pos, p_arg, p_kwarg)


def test_get_ordered_params_tier_ordering(ordered_collector):
    """
    Within the same kind, MUST return 'no_default' parameters before 'default' parameters.
    """
    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    p_mand = make_p("mandatory", kind, has_default=False)
    p_opt = make_p("optional", kind, has_default=True)

    # Even if we "accidentally" fill the default list first
    ordered_collector._params_map[kind][ordered_collector._CONTAIN_DEFAULT].append(p_opt)
    ordered_collector._params_map[kind][ordered_collector._WITHOUT_DEFAULT].append(p_mand)

    result = ordered_collector.get_ordered_params()

    # The logic must ensure mandatory comes BEFORE optional
    assert result == (p_mand, p_opt)


def test_get_ordered_params_preserves_insertion_order_within_tier(ordered_collector):
    """Within the same tier (category), the insertion order must be preserved."""
    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    p1 = make_p("a", kind)
    p2 = make_p("b", kind)

    ordered_collector._params_map[kind][ordered_collector._WITHOUT_DEFAULT].extend([p1, p2])

    result = ordered_collector.get_ordered_params()
    assert result == (p1, p2)


def test_get_ordered_params_returns_tuple_snapshot(ordered_collector):
    """The returned value must be an immutable tuple snapshot."""
    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    p1 = make_p("x", kind)
    ordered_collector._params_map[kind][ordered_collector._WITHOUT_DEFAULT].append(p1)

    result = ordered_collector.get_ordered_params()
    assert isinstance(result, tuple)

    # Modify internal state after getting result
    p2 = make_p("y", kind)
    ordered_collector._params_map[kind][ordered_collector._WITHOUT_DEFAULT].append(p2)

    assert len(result) == 1
    assert p2 not in result