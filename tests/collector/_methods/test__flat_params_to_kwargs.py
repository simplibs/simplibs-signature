import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature.collector._constants.kinds import (
    KEYWORD_ONLY,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT
from simplibs.signature.collector._methods._flat_params_to_kwargs import _flat_params_to_kwargs
from simplibs.signature.constants import KWARGS


def _flat(storage, param, *, accept_double=True, replace_double=True):
    seen, params_map = storage
    _flat_params_to_kwargs(
        param=param,
        params_map=params_map,
        seen_names=seen,
        accept_double=accept_double,
        replace_double=replace_double,
    )


def _stored(storage):
    return storage[1][KEYWORD_ONLY][CONTAIN_DEFAULT]


@pytest.mark.parametrize("kind", [POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, KEYWORD_ONLY])
def test_regular_parameters_become_keyword_only(storage, make_param, kind):
    _flat(storage, make_param("x", kind))

    [stored] = _stored(storage)
    assert stored.name == "x" and stored.kind is KEYWORD_ONLY


def test_default_and_annotation_survive(storage, make_param):
    _flat(storage, make_param("x", default=5, annotation=int))

    [stored] = _stored(storage)
    assert stored.default == 5 and stored.annotation is int


def test_goes_to_one_tier_and_is_indexed(storage, make_param):
    _flat(storage, make_param("x"))

    seen, params_map = storage
    assert seen["x"] == (KEYWORD_ONLY, CONTAIN_DEFAULT)
    assert params_map[KEYWORD_ONLY][WITHOUT_DEFAULT] == []


def test_arrival_order_is_kept(storage, make_param):
    for name in ("c", "a", "b"):
        _flat(storage, make_param(name))

    assert [p.name for p in _stored(storage)] == ["c", "a", "b"]


def test_args_is_dropped(storage, make_param):
    _flat(storage, make_param("args", VAR_POSITIONAL))

    seen, params_map = storage
    assert seen == {}
    assert params_map[VAR_POSITIONAL][WITHOUT_DEFAULT] == []
    assert _stored(storage) == []


def test_kwargs_becomes_the_placeholder(storage, make_param):
    _flat(storage, make_param("options", VAR_KEYWORD))

    seen, params_map = storage
    assert params_map[VAR_KEYWORD][WITHOUT_DEFAULT] == [KWARGS]
    assert seen["kwargs"] == (VAR_KEYWORD, WITHOUT_DEFAULT)


def test_all_kwargs_merge_into_one(storage, make_param):
    _flat(storage, make_param("kw", VAR_KEYWORD))
    _flat(storage, make_param("options", VAR_KEYWORD))

    assert storage[1][VAR_KEYWORD][WITHOUT_DEFAULT] == [KWARGS]


def test_kwargs_ignores_accept_double(storage, make_param):
    _flat(storage, make_param("kw", VAR_KEYWORD), accept_double=False)
    _flat(storage, make_param("options", VAR_KEYWORD), accept_double=False)

    assert storage[1][VAR_KEYWORD][WITHOUT_DEFAULT] == [KWARGS]


def test_a_collision_is_refused_without_accept_double(subtests, storage, make_param):
    _flat(storage, make_param("x"))
    seen, params_map = storage

    exc = assert_exception_function(
        subtests,
        _flat_params_to_kwargs,
        exception_type=ParamError,
        invalid_params=Kwargs(
            param=make_param("x"), params_map=params_map, seen_names=seen,
            accept_double=False, replace_double=True,
        ),
        error_name="DUPLICATE PARAMETER ERROR",
        value="x",
    )

    assert isinstance(exc, ValueError)


def test_replace_double_replaces_the_stored_parameter(storage, make_param):
    _flat(storage, make_param("x", default=1))
    _flat(storage, make_param("x", default=2), replace_double=True)

    [stored] = _stored(storage)
    assert stored.default == 2


def test_without_replace_double_both_are_kept_and_the_later_is_renamed(storage, make_param):
    _flat(storage, make_param("x", default=1))
    _flat(storage, make_param("x", default=2), replace_double=False)

    assert [(p.name, p.default) for p in _stored(storage)] == [("x", 1), ("x_1", 2)]


def test_renaming_skips_names_that_are_taken(storage, make_param):
    _flat(storage, make_param("x"))
    _flat(storage, make_param("x_1"))
    _flat(storage, make_param("x"), replace_double=False)

    assert [p.name for p in _stored(storage)] == ["x", "x_1", "x_2"]


def test_a_replaced_name_is_still_indexed_once(storage, make_param):
    _flat(storage, make_param("x"))
    _flat(storage, make_param("x"), replace_double=True)

    assert list(storage[0]) == ["x"]
