import inspect
from functools import partial

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import create_signature

P = inspect.Parameter


def _f(a, *args, b=1):
    ...


def _g(c, *rest):
    ...


def _h(x, *a, **kw) -> list:
    ...


def _typed() -> int:
    ...


def test_no_sources_make_an_empty_signature():
    assert str(create_signature()) == "()"


def test_a_single_function():
    assert create_signature(_f) == inspect.signature(_f)


def test_parameters_and_functions_mix(names_of):
    result = create_signature(P("first", P.POSITIONAL_ONLY), _g, P("last", P.KEYWORD_ONLY))

    assert names_of(result) == ["first", "c", "rest", "last"]


def test_the_result_is_always_in_a_valid_order(names_of):
    result = create_signature(P("k", P.KEYWORD_ONLY), P("kw", P.VAR_KEYWORD), P("a", P.POSITIONAL_OR_KEYWORD))

    assert names_of(result) == ["a", "k", "kw"]


def test_a_second_args_replaces_the_first_by_default():
    assert str(create_signature(_f, _g)) == "(a, c, *rest, b=1)"


def test_a_second_args_is_dropped_without_replace_double():
    assert str(create_signature(_f, _g, replace_double=False)) == "(a, c, *args, b=1)"


def test_a_second_args_is_refused_without_accept_double(subtests):
    assert_exception_function(
        subtests,
        partial(create_signature, accept_double=False),
        exception_type=ParamError,
        invalid_params=(_f, _g),
        valid_params=(_f, P("other", P.KEYWORD_ONLY)),
        error_name="DUPLICATE PARAMETER ERROR",
        problem="collides with the already defined variadic positional parameter 'args'",
    )


def test_a_name_collision_is_refused_without_accept_double(subtests):
    exc = assert_exception_function(
        subtests,
        partial(create_signature, accept_double=False),
        exception_type=ParamError,
        invalid_params=(P("x", P.KEYWORD_ONLY), P("x", P.KEYWORD_ONLY)),
        error_name="DUPLICATE PARAMETER ERROR",
        value="x",
    )

    assert isinstance(exc, ValueError)


def test_no_return_source_means_no_annotation():
    assert create_signature(_f).return_annotation is inspect.Signature.empty


@pytest.mark.parametrize("source, expected", [
    (int, int),
    (None, None),
    ("later", "later"),
    (list[int], list[int]),
    (_typed, int),
])
def test_return_source(source, expected):
    assert create_signature(_f, return_source=source).return_annotation == expected


def test_excluded_names(names_of):
    assert names_of(create_signature(_f, _g, excluded_names=["a", "c"])) == ["rest", "b"]


def test_include_variadic_false(names_of):
    assert names_of(create_signature(_h, include_variadic=False)) == ["x"]


def test_include_binding_false(names_of):
    class Thing:
        def method(self, x): ...

    assert names_of(create_signature(Thing.method, include_binding=False)) == ["x"]


def test_flat_mode():
    assert str(create_signature(_f, _h, flat_to_kwargs=True)) == "(*, a, b=1, x, **kwargs)"


def test_a_source_that_is_neither_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        partial(create_signature, _validate_call=False),
        exception_type=ParamError,
        invalid_params=(_f, 5),
        error_name="INVALID PARAMETER SOURCE",
        label="param_sources[1]",
        value=5,
    )

    assert isinstance(exc, TypeError)


def test_a_signature_that_cannot_be_read_is_refused(subtests):
    looped = lambda: None
    looped.__wrapped__ = looped

    exc = assert_exception_function(
        subtests,
        create_signature,
        exception_type=ParamError,
        invalid_params=(looped,),
        error_name="SIGNATURE INTROSPECTION ERROR",
    )

    assert isinstance(exc, ValueError)


@pytest.mark.parametrize("names", [["a", "c"], ("a", "c"), {"a", "c"}, (n for n in ["a", "c"])])
def test_excluded_names_accept_any_iterable(names, names_of):
    assert names_of(create_signature(_f, _g, excluded_names=names)) == ["rest", "b"]