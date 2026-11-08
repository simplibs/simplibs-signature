import asyncio
import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs
from simplibs.sentinels import UNSET

from simplibs.signature import signature_copy

P = inspect.Parameter


def _base(a: int, b=1, *args, k, **kwargs) -> str:
    ...


def test_gives_the_wrapper_the_signature_of_the_base():
    @signature_copy(_base)
    def wrapper(*args, **kwargs):
        ...

    assert inspect.signature(wrapper) == inspect.signature(_base)


def test_returns():
    @signature_copy(_base, returns=int)
    def wrapper(*args, **kwargs):
        ...

    assert inspect.signature(wrapper).return_annotation is int


def test_unset_returns_keeps_the_original_annotation():
    @signature_copy(_base, returns=UNSET)
    def wrapper(*args, **kwargs):
        ...

    assert inspect.signature(wrapper).return_annotation is str


def test_extras_and_excepts(names_of):
    @signature_copy(_base, extras=[P("extra", P.KEYWORD_ONLY)], excepts=["a"])
    def wrapper(*args, **kwargs):
        ...

    assert names_of(inspect.signature(wrapper)) == ["b", "args", "k", "extra", "kwargs"]


def test_extras_accept_a_generator(names_of):
    @signature_copy(_base, extras=(P(n, P.KEYWORD_ONLY) for n in ("x", "y")))
    def wrapper(*args, **kwargs):
        ...

    assert names_of(inspect.signature(wrapper))[-3:] == ["x", "y", "kwargs"]


def test_include_variadic_false(names_of):
    @signature_copy(_base, include_variadic=False)
    def wrapper(*args, **kwargs):
        ...

    assert names_of(inspect.signature(wrapper)) == ["a", "b", "k"]


def test_include_binding_false(names_of):
    class Thing:
        def method(self, x): ...

    @signature_copy(Thing.method, include_binding=False)
    def wrapper(*args, **kwargs):
        ...

    assert names_of(inspect.signature(wrapper)) == ["x"]


def test_flat_mode():
    @signature_copy(_base, flat_to_kwargs=True)
    def wrapper(*args, **kwargs):
        ...

    assert str(inspect.signature(wrapper)) == "(*, a: int, b=1, k, **kwargs) -> str"


def test_one_decorator_serves_many_functions():
    decorator = signature_copy(_base)

    first = decorator(lambda *a, **k: 1)
    second = decorator(lambda *a, **k: 2)

    assert inspect.signature(first) == inspect.signature(second)
    assert (first(), second()) == (1, 2)


def test_the_wrapper_still_works():
    @signature_copy(_base)
    def wrapper(*args, **kwargs):
        return (args, kwargs)

    assert wrapper(1, k=2) == ((1,), {"k": 2})


def test_a_coroutine_function_stays_awaitable():
    @signature_copy(_base)
    async def wrapper(*args, **kwargs):
        return "done"

    assert inspect.iscoroutinefunction(wrapper)
    assert asyncio.run(wrapper(1, k=2)) == "done"


def test_a_collision_is_refused_when_the_decorator_is_made(subtests):
    exc = assert_exception_function(
        subtests,
        signature_copy,
        exception_type=ParamError,
        invalid_params=Kwargs(base_func=_base, extras=[P("a", P.KEYWORD_ONLY)], accept_double=False),
        valid_params=Kwargs(base_func=_base, extras=[P("fresh", P.KEYWORD_ONLY)], accept_double=False),
        error_name="DUPLICATE PARAMETER ERROR",
        value="a",
    )

    assert isinstance(exc, ValueError)


def test_a_signature_that_cannot_be_read_is_refused(subtests):
    looped = lambda: None
    looped.__wrapped__ = looped

    assert_exception_function(
        subtests,
        signature_copy,
        exception_type=ParamError,
        invalid_params=(looped,),
        error_name="SIGNATURE INTROSPECTION ERROR",
    )
