"""
Tests for FlatParamsToKwarksMixin — verifying transformation,
smart renaming, and variadic unification logic.
"""
import pytest
import inspect
from simplibs.signature.core.parameter_collector._mixins import FlatParamsToKwarksMixin
from simplibs.signature.core.constants import KWARGS
from simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

class MockFlatCollector(FlatParamsToKwarksMixin):
    """Minimal implementation for testing flat mode transformation."""

    _WITHOUT_DEFAULT = "no_default"
    _CONTAIN_DEFAULT = "default"

    # Kind Aliases (used by the mixin)
    VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY

    def __init__(self, accept_double=True, replace_double=True):
        self._accept_double = accept_double
        self._replace_double = replace_double
        self._seen_names = {}

        # Initialize tiered storage
        self._params_map = {
            self.VAR_POSITIONAL: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []},
            self.VAR_KEYWORD: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []},
            self.KEYWORD_ONLY: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []},
        }


def make_p(name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, default=inspect.Parameter.empty):
    return inspect.Parameter(name, kind, default=default)


@pytest.fixture
def flat_collector():
    return MockFlatCollector()


# -----------------------------------------------------------------------------
# 1. Variadic Handling
# -----------------------------------------------------------------------------

def test_flat_mode_drops_var_positional(flat_collector):
    """VAR_POSITIONAL (*args) must be completely ignored in flat mode."""
    param = make_p("args", kind=inspect.Parameter.VAR_POSITIONAL)
    flat_collector._flat_params_to_kwargs(param)

    assert "args" not in flat_collector._seen_names
    assert len(flat_collector._params_map[inspect.Parameter.VAR_POSITIONAL][flat_collector._WITHOUT_DEFAULT]) == 0


def test_flat_mode_unifies_var_keyword(flat_collector):
    """Multiple **kwargs must be unified into a single KWARGS placeholder."""
    kw1 = make_p("params", kind=inspect.Parameter.VAR_KEYWORD)
    kw2 = make_p("extra", kind=inspect.Parameter.VAR_KEYWORD)

    flat_collector._flat_params_to_kwargs(kw1)
    flat_collector._flat_params_to_kwargs(kw2)

    # Should only contain one entry, and it should be the KWARGS constant
    kwargs_list = flat_collector._params_map[inspect.Parameter.VAR_KEYWORD][flat_collector._WITHOUT_DEFAULT]
    assert len(kwargs_list) == 1
    assert kwargs_list[0] is KWARGS
    assert KWARGS.name in flat_collector._seen_names


# -----------------------------------------------------------------------------
# 2. Transformation to KEYWORD_ONLY
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("kind", [
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.KEYWORD_ONLY
])
def test_flat_mode_transforms_to_keyword_only(flat_collector, kind):
    """All regular parameters must be converted to KEYWORD_ONLY."""
    param = make_p("x", kind=kind)
    flat_collector._flat_params_to_kwargs(param)

    stored_param = flat_collector._params_map[inspect.Parameter.KEYWORD_ONLY][flat_collector._CONTAIN_DEFAULT][0]
    assert stored_param.kind == inspect.Parameter.KEYWORD_ONLY
    assert flat_collector._seen_names["x"] == (inspect.Parameter.KEYWORD_ONLY, flat_collector._CONTAIN_DEFAULT)


# -----------------------------------------------------------------------------
# 3. Collision & Replacement Strategies
# -----------------------------------------------------------------------------

def test_flat_mode_replace_double_true(flat_collector):
    """If replace_double=True, new parameter should overwrite existing one."""
    flat_collector._replace_double = True

    p1 = make_p("x", default=1)
    p2 = make_p("x", default=2)

    flat_collector._flat_params_to_kwargs(p1)
    flat_collector._flat_params_to_kwargs(p2)

    params = flat_collector._params_map[inspect.Parameter.KEYWORD_ONLY][flat_collector._CONTAIN_DEFAULT]
    assert len(params) == 1
    assert params[0].default == 2


def test_flat_mode_smart_renaming(flat_collector):
    """
    If replace_double=False, new parameter should be renamed (x -> x_1 -> x_2)
    to avoid collision while keeping both.
    """
    flat_collector._replace_double = False

    p1 = make_p("x", default=1)
    p2 = make_p("x", default=2)
    p3 = make_p("x", default=3)

    flat_collector._flat_params_to_kwargs(p1)
    flat_collector._flat_params_to_kwargs(p2)
    flat_collector._flat_params_to_kwargs(p3)

    # Check names in storage
    params = flat_collector._params_map[inspect.Parameter.KEYWORD_ONLY][flat_collector._CONTAIN_DEFAULT]
    names = [p.name for p in params]

    assert "x" in names
    assert "x_1" in names
    assert "x_2" in names
    assert len(params) == 3


def test_flat_mode_strict_duplicate_raises(flat_collector):
    """If accept_double=False, collisions must raise SignatureBuildError."""
    flat_collector._accept_double = False

    flat_collector._flat_params_to_kwargs(make_p("x"))

    with pytest.raises(SignatureBuildError) as exc_info:
        flat_collector._flat_params_to_kwargs(make_p("x"))

    assert exc_info.value.error_name == "DUPLICATE PARAMETER ERROR"


# -----------------------------------------------------------------------------
# 4. Storage Routing
# -----------------------------------------------------------------------------

def test_flat_mode_always_uses_contain_default_bucket(flat_collector):
    """
    In flat mode, even parameters WITHOUT default should be stored in 
    CONTAIN_DEFAULT bucket to ensure they can follow any other flattened param.
    """
    param = make_p("mandatory", default=inspect.Parameter.empty)
    flat_collector._flat_params_to_kwargs(param)

    # Verify it went to 'default' bucket, not 'no_default'
    assert len(flat_collector._params_map[inspect.Parameter.KEYWORD_ONLY][flat_collector._WITHOUT_DEFAULT]) == 0
    assert len(flat_collector._params_map[inspect.Parameter.KEYWORD_ONLY][flat_collector._CONTAIN_DEFAULT]) == 1