"""
Tests for PositionalEmptyOrderCheckMixin — verifying that mandatory
positional parameters cannot follow optional ones.
"""
import pytest
import inspect
from simplibs.signature.core.parameter_collector._mixins import PositionalEmptyOrderCheckMixin
from simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

class MockOrderCollector(PositionalEmptyOrderCheckMixin):
    """Minimal implementation for testing positional ordering rules."""

    _WITHOUT_DEFAULT = "no_default"
    _CONTAIN_DEFAULT = "default"
    EMPTY = inspect.Parameter.empty

    # Kind Aliases
    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD

    def __init__(self):
        # Initialize only what's needed for this mixin
        self._params_map = {
            self.POSITIONAL_ONLY: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []},
            self.POSITIONAL_OR_KEYWORD: {self._WITHOUT_DEFAULT: [], self._CONTAIN_DEFAULT: []},
        }


def make_p(name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, has_default=False):
    default = "some_value" if has_default else inspect.Parameter.empty
    return inspect.Parameter(name, kind, default=default)


@pytest.fixture
def order_collector():
    return MockOrderCollector()


# -----------------------------------------------------------------------------
# 1. Valid Sequences (No Exception)
# -----------------------------------------------------------------------------

def test_order_check_passes_for_param_with_default(order_collector):
    """If the new parameter has a default, the check must always pass."""
    # Pre-fill with a default parameter
    order_collector._params_map[order_collector.POSITIONAL_ONLY][order_collector._CONTAIN_DEFAULT].append(make_p("a", has_default=True))

    # Adding another one with default is always fine
    param = make_p("b", has_default=True)
    order_collector._positional_empty_order_check(param)


def test_order_check_passes_when_no_defaults_exist(order_collector):
    """Adding a mandatory parameter when no optional ones exist must pass."""
    param = make_p("a", has_default=False)
    order_collector._positional_empty_order_check(param)


# -----------------------------------------------------------------------------
# 2. Invalid Sequences (SyntaxError)
# -----------------------------------------------------------------------------

def test_positional_only_mandatory_after_optional_raises(order_collector):
    """POSITIONAL_ONLY without default cannot follow POSITIONAL_ONLY with default."""
    # 1. Add optional POSITIONAL_ONLY
    order_collector._params_map[order_collector.POSITIONAL_ONLY][order_collector._CONTAIN_DEFAULT].append(
        make_p("opt", kind=order_collector.POSITIONAL_ONLY, has_default=True)
    )

    # 2. Try to add mandatory POSITIONAL_ONLY
    param = make_p("mand", kind=order_collector.POSITIONAL_ONLY, has_default=False)

    with pytest.raises(SignatureBuildError) as exc_info:
        order_collector._positional_empty_order_check(param)

    assert exc_info.value.error_name == "INVALID PARAMETER ORDER"
    assert exc_info.value.exception is SyntaxError


def test_positional_or_keyword_mandatory_after_positional_only_optional_raises(order_collector):
    """POSITIONAL_OR_KEYWORD without default cannot follow ANY positional with default."""
    # 1. Add optional POSITIONAL_ONLY
    order_collector._params_map[order_collector.POSITIONAL_ONLY][order_collector._CONTAIN_DEFAULT].append(
        make_p("opt_pos", kind=order_collector.POSITIONAL_ONLY, has_default=True)
    )

    # 2. Try to add mandatory POSITIONAL_OR_KEYWORD
    param = make_p("mand_pk", kind=order_collector.POSITIONAL_OR_KEYWORD, has_default=False)

    with pytest.raises(SignatureBuildError):
        order_collector._positional_empty_order_check(param)


def test_positional_or_keyword_mandatory_after_its_own_optional_raises(order_collector):
    """POSITIONAL_OR_KEYWORD without default cannot follow its own optional category."""
    # 1. Add optional POSITIONAL_OR_KEYWORD
    order_collector._params_map[order_collector.POSITIONAL_OR_KEYWORD][order_collector._CONTAIN_DEFAULT].append(
        make_p("opt_pk", kind=order_collector.POSITIONAL_OR_KEYWORD, has_default=True)
    )

    # 2. Try to add mandatory POSITIONAL_OR_KEYWORD
    param = make_p("mand_pk", kind=order_collector.POSITIONAL_OR_KEYWORD, has_default=False)

    with pytest.raises(SignatureBuildError):
        order_collector._positional_empty_order_check(param)


# -----------------------------------------------------------------------------
# 3. Context & Metadata
# -----------------------------------------------------------------------------

def test_order_error_metadata_is_correct(order_collector):
    """Verify that error metadata contains helpful instructions."""
    order_collector._params_map[order_collector.POSITIONAL_ONLY][order_collector._CONTAIN_DEFAULT].append(make_p("a", has_default=True))

    param = make_p("bad_param", has_default=False)
    with pytest.raises(SignatureBuildError) as exc_info:
        order_collector._positional_empty_order_check(param)

    e = exc_info.value
    assert "bad_param" in e.problem
    assert any("before optional parameters" in advice for advice in e.how_to_fix)
    assert e.context == "AddParamMixin.add_param() — default value order check"