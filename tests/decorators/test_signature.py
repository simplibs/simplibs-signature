import asyncio
import inspect
from functools import partial

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.sentinels import UNSET

from simplibs.signature import KWARGS, signature

P = inspect.Parameter


def _kw(name, default=P.empty):
    return P(name, P.KEYWORD_ONLY, default=default)


def test_empty_decorator_reports_the_function_itself():
    def function(a, b=1, *args, **kwargs):
        ...

    decorated = signature()(function)

    assert inspect.signature(decorated) == inspect.signature(function)


def test_adds_parameters_in_their_place():
    @signature(_kw("extra"))
    def function(a, *args, **kwargs):
        ...

    assert str(inspect.signature(function)) == "(a, *args, extra, **kwargs)"


def test_use_func_false_ignores_the_function():
    @signature(_kw("only"), use_func=False)
    def function(a, b):
        ...

    assert str(inspect.signature(function)) == "(*, only)"


def test_parameters_win_a_collision_when_the_function_goes_first():
    @signature(P("a", P.POSITIONAL_OR_KEYWORD, default=2), func_first=True)
    def function(a=1):
        ...

    assert inspect.signature(function).parameters["a"].default == 2


def test_the_function_wins_a_collision_when_it_goes_last():
    @signature(P("a", P.POSITIONAL_OR_KEYWORD, default=2), func_first=False)
    def function(a=1):
        ...

    assert inspect.signature(function).parameters["a"].default == 1


def test_function_first_is_the_default():
    @signature(P("a", P.POSITIONAL_OR_KEYWORD, default=2))
    def function(a=1):
        ...

    assert inspect.signature(function).parameters["a"].default == 2


def test_a_callable_among_the_sources_contributes_its_parameters(names_of):
    def other(x, y):
        ...

    @signature(other)
    def function(a):
        ...

    assert names_of(inspect.signature(function)) == ["a", "x", "y"]


@pytest.mark.parametrize("returns, expected", [
    (int, int),
    (None, None),
    (UNSET, inspect.Signature.empty),
    (lambda: None, inspect.Signature.empty),
])
def test_returns(returns, expected):
    @signature(returns=returns)
    def function():
        ...

    assert inspect.signature(function).return_annotation == expected


def test_returns_a_callable_takes_its_annotation():
    def typed() -> str:
        ...

    @signature(returns=typed)
    def function():
        ...

    assert inspect.signature(function).return_annotation is str


def test_excepts(names_of):
    @signature(excepts=["b"])
    def function(a, b, c):
        ...

    assert names_of(inspect.signature(function)) == ["a", "c"]


def test_include_variadic_false(names_of):
    @signature(include_variadic=False)
    def function(a, *args, **kwargs):
        ...

    assert names_of(inspect.signature(function)) == ["a"]


def test_include_binding_false(names_of):
    @signature(include_binding=False)
    def method(self, x):
        ...

    assert names_of(inspect.signature(method)) == ["x"]


def test_flat_mode():
    @signature(flat_to_kwargs=True)
    def function(a, b=1, *args, **kw):
        ...

    assert str(inspect.signature(function)) == "(*, a, b=1, **kwargs)"


def test_a_second_args_replaces_the_function_s_own():
    @signature(P("rest", P.VAR_POSITIONAL))
    def function(a, *args):
        ...

    assert str(inspect.signature(function)) == "(a, *rest)"


def test_the_decorated_function_still_works():
    @signature(_kw("extra"))
    def function(a, b=2):
        return a + b

    assert function(1) == 3


def test_the_decorated_function_keeps_its_name():
    @signature()
    def function():
        ...

    assert function.__name__ == "function"


def test_a_coroutine_function_stays_awaitable():
    @signature(_kw("extra"))
    async def function(a):
        return a

    assert inspect.iscoroutinefunction(function)
    assert asyncio.run(function(7)) == 7


def test_an_invalid_source_is_refused_when_decorating(subtests):
    def function():
        ...

    exc = assert_exception_function(
        subtests,
        signature(5, _validate_call=False),
        exception_type=ParamError,
        invalid_params=(function,),
        error_name="INVALID PARAMETER SOURCE",
        label="param_sources[1]",
        value=5,
    )

    assert isinstance(exc, TypeError)


def test_a_collision_is_refused_when_decorating(subtests):
    def function(a):
        ...

    assert_exception_function(
        subtests,
        signature(P("a", P.KEYWORD_ONLY), accept_double=False),
        exception_type=ParamError,
        invalid_params=(function,),
        valid_params=(lambda z: None,),
        error_name="DUPLICATE PARAMETER ERROR",
        value="a",
    )


@pytest.mark.parametrize("excepts", [["b"], ("b",), {"b"}, (n for n in ["b"])])
def test_excepts_accepts_any_iterable(excepts, names_of):
    @signature(excepts=excepts)
    def function(a, b, c):
        ...

    assert names_of(inspect.signature(function)) == ["a", "c"]


def test_a_generator_of_excepts_serves_many_functions(names_of):
    decorator = signature(excepts=(name for name in ["b"]))

    @decorator
    def first(a, b):
        ...

    @decorator
    def second(b, c):
        ...

    assert names_of(inspect.signature(first)) == ["a"]
    assert names_of(inspect.signature(second)) == ["c"]