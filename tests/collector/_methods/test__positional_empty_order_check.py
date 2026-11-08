import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.collector._constants.kinds import (
    KEYWORD_ONLY,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT
from simplibs.signature.collector._methods._positional_empty_order_check import _positional_empty_order_check


def _with_optional(storage, make_param, kind):
    """Storage that already holds one optional parameter of `kind`."""
    _, params_map = storage
    params_map[kind][CONTAIN_DEFAULT].append(make_param("stored", kind, default=1))
    return params_map


@pytest.mark.parametrize("stored_kind, new_kind", [
    (POSITIONAL_OR_KEYWORD, POSITIONAL_OR_KEYWORD),
    (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD),
    (POSITIONAL_ONLY, POSITIONAL_ONLY),
])
def test_required_after_optional_is_refused(subtests, storage, make_param, stored_kind, new_kind):
    params_map = _with_optional(storage, make_param, stored_kind)

    exc = assert_exception_function(
        subtests,
        _positional_empty_order_check,
        exception_type=ParamError,
        invalid_params=(make_param("late", new_kind), params_map),
        valid_params=(make_param("late", new_kind, default=2), params_map),
        error_name="INVALID PARAMETER ORDER",
        label="param.name",
        value="late",
        exception=SyntaxError,
    )

    assert isinstance(exc, SyntaxError)


@pytest.mark.parametrize("stored_kind, new_kind", [
    (POSITIONAL_OR_KEYWORD, POSITIONAL_ONLY),
    (POSITIONAL_OR_KEYWORD, KEYWORD_ONLY),
    (POSITIONAL_ONLY, KEYWORD_ONLY),
    (POSITIONAL_OR_KEYWORD, VAR_POSITIONAL),
    (POSITIONAL_OR_KEYWORD, VAR_KEYWORD),
    (KEYWORD_ONLY, POSITIONAL_OR_KEYWORD),
    (KEYWORD_ONLY, KEYWORD_ONLY),
])
def test_other_combinations_are_fine(storage, make_param, stored_kind, new_kind):
    params_map = _with_optional(storage, make_param, stored_kind)

    assert _positional_empty_order_check(make_param("late", new_kind), params_map) is None


def test_a_parameter_with_a_default_is_always_fine(storage, make_param):
    params_map = _with_optional(storage, make_param, POSITIONAL_OR_KEYWORD)

    assert _positional_empty_order_check(make_param("late", default=2), params_map) is None


def test_empty_storage_is_fine(storage, make_param):
    _, params_map = storage

    assert _positional_empty_order_check(make_param("x"), params_map) is None
