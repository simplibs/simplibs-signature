import inspect
from types import SimpleNamespace

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import compose_signature

P = inspect.Parameter


def _p(name, kind=P.POSITIONAL_OR_KEYWORD, default=P.empty):
    return P(name, kind, default=default)


def test_composes_a_signature():
    signature = compose_signature([_p("a"), _p("b", default=1)], int)

    assert str(signature) == "(a, b=1) -> int"


def test_return_annotation_is_optional():
    assert compose_signature([_p("a")]).return_annotation is inspect.Signature.empty


def test_none_is_a_return_annotation():
    assert compose_signature([_p("a")], None).return_annotation is None


def test_empty_parameters_make_an_empty_signature():
    assert str(compose_signature([])) == "()"


def test_accepts_a_generator():
    assert str(compose_signature(_p(name) for name in "xy")) == "(x, y)"


@pytest.mark.parametrize("parameters", [
    pytest.param([_p("a", default=1), _p("b")], id="required-after-optional"),
    pytest.param([_p("a"), _p("a", P.KEYWORD_ONLY)], id="duplicate-name"),
    pytest.param([_p("k", P.KEYWORD_ONLY), _p("a")], id="wrong-kind-order"),
])
def test_a_structure_that_is_not_a_signature_is_refused(subtests, parameters):
    exc = assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=parameters),
        valid_params=Kwargs(parameters=[_p("ok")]),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=tuple(parameters),
        expected="a collection of valid, uniquely named inspect.Parameter instances",
    )

    assert isinstance(exc, ValueError)


def test_the_error_shows_the_parameters_even_when_they_came_from_a_generator(subtests):
    parameters = [_p("a"), _p("a")]

    assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=(p for p in parameters)),
        value=tuple(parameters),
    )


def test_the_structure_is_checked_even_when_validation_is_off(subtests):
    parameters = [_p("a"), _p("a", P.KEYWORD_ONLY)]

    assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=parameters, _validate_call=False),
        error_name="SIGNATURE COMPOSITION ERROR",
        value=tuple(parameters),
    )


def test_an_item_that_is_not_a_parameter_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=["x"], _validate_call=False),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=("x",),
        expected="a collection of inspect.Parameter instances",
    )

    assert isinstance(exc, AttributeError)


def test_something_that_is_not_iterable_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=5, _validate_call=False),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=5,
        expected="an iterable of inspect.Parameter instances",
    )

    assert isinstance(exc, TypeError)


def test_a_parameter_with_an_unusable_kind_is_refused(subtests):
    broken = SimpleNamespace(name="x", kind="not-a-kind", default=P.empty)

    exc = assert_exception_function(
        subtests,
        compose_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(parameters=[broken], _validate_call=False),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=(broken,),
        expected="an iterable of inspect.Parameter instances",
    )

    assert isinstance(exc, TypeError)
