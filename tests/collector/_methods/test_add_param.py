import inspect
from types import SimpleNamespace

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature.collector._constants.kinds import (
    EMPTY,
    KEYWORD_ONLY,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT
from simplibs.signature.collector._methods import add_param
from simplibs.signature.constants import KWARGS

OPTIONS = dict(
    excluded_names=set(),
    include_variadic=True,
    flat_to_kwargs=False,
    accept_double=True,
    replace_double=True,
)


def _add(storage, param, **overrides):
    seen, params_map = storage
    add_param(param=param, seen_names=seen, params_map=params_map, **{**OPTIONS, **overrides})


def _names(storage, kind, tier):
    return [p.name for p in storage[1][kind][tier]]


def test_stores_a_required_parameter_in_its_kind_and_tier(storage, make_param):
    _add(storage, make_param("x"))

    assert _names(storage, POSITIONAL_OR_KEYWORD, WITHOUT_DEFAULT) == ["x"]
    assert storage[0]["x"] == (POSITIONAL_OR_KEYWORD, WITHOUT_DEFAULT)


def test_stores_an_optional_parameter_in_the_default_tier(storage, make_param):
    _add(storage, make_param("x", default=None))

    assert _names(storage, POSITIONAL_OR_KEYWORD, CONTAIN_DEFAULT) == ["x"]
    assert storage[0]["x"] == (POSITIONAL_OR_KEYWORD, CONTAIN_DEFAULT)


@pytest.mark.parametrize("kind", [POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, KEYWORD_ONLY])
def test_every_regular_kind_has_a_slot(storage, make_param, kind):
    _add(storage, make_param("x", kind))

    assert _names(storage, kind, WITHOUT_DEFAULT) == ["x"]


@pytest.mark.parametrize("kind", [VAR_POSITIONAL, VAR_KEYWORD])
def test_variadics_go_to_the_required_tier(storage, make_param, kind):
    _add(storage, make_param("v", kind))

    assert _names(storage, kind, WITHOUT_DEFAULT) == ["v"]


def test_excluded_name_leaves_no_trace(storage, make_param):
    _add(storage, make_param("self"), excluded_names={"self"})

    assert storage[0] == {}
    assert all(not tier for tiers in storage[1].values() for tier in tiers.values())


def test_excluded_name_is_not_even_a_collision(storage, make_param):
    _add(storage, make_param("x"))
    _add(storage, make_param("x"), excluded_names={"x"}, accept_double=False)

    assert _names(storage, POSITIONAL_OR_KEYWORD, WITHOUT_DEFAULT) == ["x"]


@pytest.mark.parametrize("name, kind", [
    ("args", VAR_POSITIONAL),
    ("a", VAR_POSITIONAL),
    ("kwargs", VAR_KEYWORD),
    ("options", VAR_KEYWORD),
])
def test_variadics_are_left_out_by_kind_not_by_name(storage, make_param, name, kind):
    _add(storage, make_param(name, kind), include_variadic=False)

    assert storage[0] == {}


def test_include_variadic_false_keeps_regular_parameters(storage, make_param):
    _add(storage, make_param("x"), include_variadic=False)

    assert list(storage[0]) == ["x"]


def test_a_regular_parameter_named_args_is_not_a_variadic(storage, make_param):
    _add(storage, make_param("args", KEYWORD_ONLY), include_variadic=False)

    assert list(storage[0]) == ["args"]


def test_flat_mode_hands_over_to_the_flat_rules(storage, make_param):
    _add(storage, make_param("x"), flat_to_kwargs=True)
    _add(storage, make_param("args", VAR_POSITIONAL), flat_to_kwargs=True)
    _add(storage, make_param("kw", VAR_KEYWORD), flat_to_kwargs=True)

    assert _names(storage, KEYWORD_ONLY, CONTAIN_DEFAULT) == ["x"]
    assert storage[1][VAR_KEYWORD][WITHOUT_DEFAULT] == [KWARGS]
    assert storage[1][VAR_POSITIONAL][WITHOUT_DEFAULT] == []


def test_excluded_variadic_is_dropped_before_flat_mode_sees_it(storage, make_param):
    _add(storage, make_param("kw", VAR_KEYWORD), flat_to_kwargs=True, include_variadic=False)

    assert storage[1][VAR_KEYWORD][WITHOUT_DEFAULT] == []


# --- collisions --------------------------------------------------------------

def test_collision_is_refused_without_accept_double(subtests, storage, make_param):
    _add(storage, make_param("x"))
    seen, params_map = storage

    exc = assert_exception_function(
        subtests,
        add_param,
        exception_type=ParamError,
        invalid_params=Kwargs(
            param=make_param("x"), seen_names=seen, params_map=params_map,
            **{**OPTIONS, "accept_double": False},
        ),
        error_name="DUPLICATE PARAMETER ERROR",
        value="x",
        problem="already defined",
    )

    assert isinstance(exc, ValueError)


def test_the_later_parameter_replaces_by_default(storage, make_param):
    _add(storage, make_param("x", default=1))
    _add(storage, make_param("x", default=2))

    [stored] = storage[1][POSITIONAL_OR_KEYWORD][CONTAIN_DEFAULT]
    assert stored.default == 2


def test_the_earlier_parameter_stays_without_replace_double(storage, make_param):
    _add(storage, make_param("x", default=1))
    _add(storage, make_param("x", default=2), replace_double=False)

    [stored] = storage[1][POSITIONAL_OR_KEYWORD][CONTAIN_DEFAULT]
    assert stored.default == 1


def test_a_replacement_may_change_the_kind_and_the_tier(storage, make_param):
    _add(storage, make_param("x"))
    _add(storage, make_param("x", KEYWORD_ONLY, default=3))

    assert _names(storage, POSITIONAL_OR_KEYWORD, WITHOUT_DEFAULT) == []
    assert _names(storage, KEYWORD_ONLY, CONTAIN_DEFAULT) == ["x"]
    assert storage[0]["x"] == (KEYWORD_ONLY, CONTAIN_DEFAULT)


# --- the variadic slot ---------------------------------------------------------

def test_a_second_args_replaces_the_first_by_default(storage, make_param):
    _add(storage, make_param("a", VAR_POSITIONAL))
    _add(storage, make_param("b", VAR_POSITIONAL))

    assert _names(storage, VAR_POSITIONAL, WITHOUT_DEFAULT) == ["b"]
    assert list(storage[0]) == ["b"]


def test_a_second_args_is_dropped_without_replace_double(storage, make_param):
    _add(storage, make_param("a", VAR_POSITIONAL))
    _add(storage, make_param("b", VAR_POSITIONAL), replace_double=False)

    assert _names(storage, VAR_POSITIONAL, WITHOUT_DEFAULT) == ["a"]
    assert list(storage[0]) == ["a"]


def test_a_second_kwargs_replaces_the_first_by_default(storage, make_param):
    _add(storage, make_param("kw", VAR_KEYWORD))
    _add(storage, make_param("options", VAR_KEYWORD))

    assert _names(storage, VAR_KEYWORD, WITHOUT_DEFAULT) == ["options"]


def test_a_second_variadic_is_refused_without_accept_double(subtests, storage, make_param):
    _add(storage, make_param("a", VAR_POSITIONAL))
    seen, params_map = storage

    assert_exception_function(
        subtests,
        add_param,
        exception_type=ParamError,
        invalid_params=Kwargs(
            param=make_param("b", VAR_POSITIONAL), seen_names=seen, params_map=params_map,
            **{**OPTIONS, "accept_double": False},
        ),
        error_name="DUPLICATE PARAMETER ERROR",
        problem="collides with the already defined variadic positional parameter 'a'",
    )


def test_args_and_kwargs_live_side_by_side(storage, make_param):
    _add(storage, make_param("a", VAR_POSITIONAL), accept_double=False)
    _add(storage, make_param("kw", VAR_KEYWORD), accept_double=False)

    assert list(storage[0]) == ["a", "kw"]


def test_a_replaced_variadic_frees_its_name(storage, make_param):
    _add(storage, make_param("a", VAR_POSITIONAL))
    _add(storage, make_param("b", VAR_POSITIONAL))
    _add(storage, make_param("a", KEYWORD_ONLY), accept_double=False)

    assert _names(storage, KEYWORD_ONLY, WITHOUT_DEFAULT) == ["a"]
    assert _names(storage, VAR_POSITIONAL, WITHOUT_DEFAULT) == ["b"]


# --- order and kinds -----------------------------------------------------------

def test_required_positional_after_optional_is_refused(subtests, storage, make_param):
    _add(storage, make_param("a", default=1))
    seen, params_map = storage

    exc = assert_exception_function(
        subtests,
        add_param,
        exception_type=ParamError,
        invalid_params=Kwargs(param=make_param("b"), seen_names=seen, params_map=params_map, **OPTIONS),
        error_name="INVALID PARAMETER ORDER",
        value="b",
    )

    assert isinstance(exc, SyntaxError)


def test_a_replaced_parameter_is_not_judged_against_itself(storage, make_param):
    _add(storage, make_param("a", default=1))
    _add(storage, make_param("a"))

    assert _names(storage, POSITIONAL_OR_KEYWORD, WITHOUT_DEFAULT) == ["a"]


def test_an_unknown_kind_is_refused(subtests, storage):
    fake = SimpleNamespace(name="x", kind="weird", default=EMPTY)
    seen, params_map = storage

    exc = assert_exception_function(
        subtests,
        add_param,
        exception_type=ParamError,
        invalid_params=Kwargs(param=fake, seen_names=seen, params_map=params_map, **OPTIONS),
        error_name="INVALID PARAMETER KIND ERROR",
        value="weird",
    )

    assert isinstance(exc, KeyError)
    assert seen == {}
