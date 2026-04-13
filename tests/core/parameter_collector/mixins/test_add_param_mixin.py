"""
Tests for AddParamMixin.add_param() — primary parameter storage logic.
Focuses on: routing to tiered storage, exclusion, and replacement policies.
"""
import pytest
import inspect
from simplibs.signature.core.parameter_collector._mixins import AddParamMixin
from simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

class MockCollector(AddParamMixin):
    """Minimal implementation of a collector for testing the mixin."""

    # Tiered storage keys
    _WITHOUT_DEFAULT = "no_default"
    _CONTAIN_DEFAULT = "default"
    EMPTY = inspect.Parameter.empty

    def __init__(self, excluded=None, accept_double=True, replace_double=True):
        self._excluded_names = excluded or set()
        # Name -> (Kind, Category)
        self._seen_names = {}
        self._accept_double = accept_double
        self._replace_double = replace_double
        self._flat_to_kwargs = False  # Disabled for these tests

        # New tiered structure
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

    def _positional_empty_order_check(self, param):
        """Mocked order check - will be tested in its own mixin suite."""
        pass

    def _flat_params_to_kwargs(self, param):
        """Mocked flat logic - will be tested in its own mixin suite."""
        pass

def make_param(name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, default=inspect.Parameter.empty):
    return inspect.Parameter(name, kind, default=default)

@pytest.fixture
def collector():
    return MockCollector()

@pytest.fixture
def strict_collector():
    return MockCollector(accept_double=False)

@pytest.fixture
def excluding_collector():
    return MockCollector(excluded={"self", "cls"})


# -----------------------------------------------------------------------------
# Tiered Storage Routing
# -----------------------------------------------------------------------------

def test_add_param_without_default_routing(collector):
    """Parameter without default must go to WITHOUT_DEFAULT category."""
    param = make_param("x", default=inspect.Parameter.empty)
    collector.add_param(param)

    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    category = collector._WITHOUT_DEFAULT

    assert collector._seen_names["x"] == (kind, category)
    assert param in collector._params_map[kind][category]
    assert len(collector._params_map[kind][collector._CONTAIN_DEFAULT]) == 0


def test_add_param_with_default_routing(collector):
    """Parameter with default must go to CONTAIN_DEFAULT category."""
    param = make_param("y", default=100)
    collector.add_param(param)

    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    category = collector._CONTAIN_DEFAULT

    assert collector._seen_names["y"] == (kind, category)
    assert param in collector._params_map[kind][category]
    assert len(collector._params_map[kind][collector._WITHOUT_DEFAULT]) == 0


@pytest.mark.parametrize("kind", [
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
])
def test_variadic_routing_is_always_to_no_default(collector, kind):
    """Variadics (which cannot have defaults) must always end up in WITHOUT_DEFAULT."""
    param = make_param("args_or_kwargs", kind=kind)
    collector.add_param(param)

    assert collector._seen_names["args_or_kwargs"] == (kind, collector._WITHOUT_DEFAULT)


# -----------------------------------------------------------------------------
# Parameter exclusion
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["self", "cls"])
def test_excluded_names_are_silently_skipped(excluding_collector, name):
    """Parameters with names in _excluded_names must not be added to storage."""
    param = make_param(name)
    excluding_collector.add_param(param)

    assert name not in excluding_collector._seen_names
    # Check both tiered categories for the default kind
    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert len(excluding_collector._params_map[kind][excluding_collector._WITHOUT_DEFAULT]) == 0
    assert len(excluding_collector._params_map[kind][excluding_collector._CONTAIN_DEFAULT]) == 0


# -----------------------------------------------------------------------------
# Duplicate handling & Replacement
# -----------------------------------------------------------------------------

def test_duplicate_raises_when_accept_double_is_false(strict_collector):
    """If duplicates are forbidden, SignatureBuildError must be raised."""
    strict_collector.add_param(make_param("x"))

    with pytest.raises(SignatureBuildError) as exc_info:
        strict_collector.add_param(make_param("x"))

    assert exc_info.value.error_name == "DUPLICATE PARAMETER ERROR"


def test_duplicate_kept_when_replace_double_is_false(collector):
    """With replace_double=False, the first parameter wins and second is ignored."""
    collector._replace_double = False

    p1 = make_param("x", default=1)
    p2 = make_param("x", default=2)

    collector.add_param(p1)
    collector.add_param(p2)

    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    params = collector._params_map[kind][collector._CONTAIN_DEFAULT]

    assert len(params) == 1
    assert params[0].default == 1  # Original remains


def test_duplicate_replaced_and_moved_category(collector):
    """
    If replacement is True, the old param should be removed even if
    the new one belongs to a different default-category.
    """
    p_old = make_param("x", default=10) # CONTAIN_DEFAULT
    p_new = make_param("x", default=inspect.Parameter.empty) # WITHOUT_DEFAULT

    collector.add_param(p_old)
    collector.add_param(p_new)

    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

    # Old category should be empty
    assert len(collector._params_map[kind][collector._CONTAIN_DEFAULT]) == 0
    # New category should have the new param
    assert p_new in collector._params_map[kind][collector._WITHOUT_DEFAULT]
    # Index must point to the new category
    assert collector._seen_names["x"] == (kind, collector._WITHOUT_DEFAULT)


# -----------------------------------------------------------------------------
# Invalid input
# -----------------------------------------------------------------------------

def test_add_non_parameter_raises(collector):
    """Adding anything other than inspect.Parameter must raise SignatureBuildError (TypeError)."""
    with pytest.raises(SignatureBuildError) as exc_info:
        collector.add_param("not a param")

    assert isinstance(exc_info.value, TypeError)