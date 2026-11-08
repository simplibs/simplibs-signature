import inspect
from types import SimpleNamespace

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import ParameterCollector, add_params_to_signature

P = inspect.Parameter


def _base(a, b=1, *args, k, **kwargs) -> str:
    ...


def _kw(name, default=P.empty):
    return P(name, P.KEYWORD_ONLY, default=default)


def test_adds_a_keyword_only_parameter_in_its_place():
    result = add_params_to_signature(inspect.signature(_base), [_kw("extra", 2)])

    assert str(result) == "(a, b=1, *args, k, extra=2, **kwargs) -> str"


def test_a_required_keyword_only_parameter_goes_before_optional_ones(names_of):
    signature = inspect.Signature([P("a", P.POSITIONAL_OR_KEYWORD), _kw("opt", 1)])

    result = add_params_to_signature(signature, [_kw("req")])

    assert names_of(result) == ["a", "req", "opt"]


def test_keeps_the_return_annotation():
    result = add_params_to_signature(inspect.signature(_base), [_kw("extra")])

    assert result.return_annotation is str


def test_does_not_change_the_original():
    original = inspect.signature(_base)

    add_params_to_signature(original, [_kw("extra")])

    assert "extra" not in original.parameters


def test_accepts_a_generator(names_of):
    result = add_params_to_signature(inspect.signature(_base), (_kw(name) for name in ("x", "y")))

    assert names_of(result)[-3:] == ["x", "y", "kwargs"]


def test_adding_nothing_gives_an_equal_signature():
    original = inspect.signature(_base)

    assert add_params_to_signature(original, []) == original


def test_the_later_parameter_replaces_a_collision_by_default():
    result = add_params_to_signature(inspect.signature(_base), [P("b", P.POSITIONAL_OR_KEYWORD, default=99)])

    assert result.parameters["b"].default == 99


def test_the_earlier_parameter_stays_without_replace_double():
    result = add_params_to_signature(
        inspect.signature(_base), [P("b", P.POSITIONAL_OR_KEYWORD, default=99)], replace_double=False,
    )

    assert result.parameters["b"].default == 1


def test_a_new_args_replaces_the_existing_one(names_of):
    result = add_params_to_signature(inspect.signature(_base), [P("rest", P.VAR_POSITIONAL)])

    assert names_of(result) == ["a", "b", "rest", "k", "kwargs"]


def test_a_collision_is_refused_without_accept_double(subtests):
    signature = inspect.signature(_base)

    exc = assert_exception_function(
        subtests,
        add_params_to_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(signature=signature, params_to_add=[_kw("a")], accept_double=False),
        valid_params=Kwargs(signature=signature, params_to_add=[_kw("fresh")], accept_double=False),
        error_name="DUPLICATE PARAMETER ERROR",
        value="a",
    )

    assert isinstance(exc, ValueError)


def test_a_second_variadic_is_refused_without_accept_double(subtests):
    assert_exception_function(
        subtests,
        add_params_to_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(
            signature=inspect.signature(_base), params_to_add=[P("rest", P.VAR_POSITIONAL)], accept_double=False,
        ),
        problem="collides with the already defined variadic positional parameter 'args'",
    )


def test_a_required_positional_after_optional_ones_is_refused(subtests):
    assert_exception_function(
        subtests,
        add_params_to_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(
            signature=inspect.signature(_base), params_to_add=[P("late", P.POSITIONAL_OR_KEYWORD)],
        ),
        error_name="INVALID PARAMETER ORDER",
        value="late",
    )


def test_flat_mode_makes_everything_keyword_only(names_of):
    result = add_params_to_signature(inspect.signature(_base), [_kw("extra")], flat_to_kwargs=True)

    assert str(result) == "(*, a, b=1, k, extra, **kwargs) -> str"


# --- defensive branches --------------------------------------------------------
# The collector keeps the order and the names valid, so `inspect` never has anything
# left to refuse. These tests replace the collector's result to reach the safety nets.

def test_a_structure_that_inspect_refuses_is_reported(subtests, monkeypatch):
    duplicates = (_kw("x"), _kw("x"))
    monkeypatch.setattr(ParameterCollector, "get_ordered_params", lambda self: duplicates)

    exc = assert_exception_function(
        subtests,
        add_params_to_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(signature=inspect.signature(_base), params_to_add=[_kw("y")]),
        error_name="SIGNATURE STRUCTURE ERROR",
        label="params_to_add",
        value=(_kw("y"),),
        expected="parameters that form a valid Python signature",
    )

    assert isinstance(exc, ValueError)


def test_parameters_of_an_unusable_type_are_reported(subtests, monkeypatch):
    broken = (SimpleNamespace(name="x", kind="not-a-kind", default=P.empty),)
    monkeypatch.setattr(ParameterCollector, "get_ordered_params", lambda self: broken)

    exc = assert_exception_function(
        subtests,
        add_params_to_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(signature=inspect.signature(_base), params_to_add=[_kw("y")]),
        error_name="SIGNATURE TYPE ERROR",
        label="parameters",
        value=broken,
        expected="valid inspect.Parameter objects",
    )

    assert isinstance(exc, TypeError)
