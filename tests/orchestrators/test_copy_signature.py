import inspect

import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs
from simplibs.sentinels import UNSET

from simplibs.signature import copy_signature

P = inspect.Parameter


def _source(a: int, b=1, *args, k, **kwargs) -> str:
    ...


class _Thing:
    def method(self, x): ...


def _looped():
    ...


_looped.__wrapped__ = _looped


def test_copies_the_signature():
    assert copy_signature(_source) == inspect.signature(_source)


def test_the_original_return_annotation_is_kept_by_default():
    assert copy_signature(_source).return_annotation is str


def test_a_new_return_annotation_replaces_it():
    assert copy_signature(_source, return_annotation=int).return_annotation is int


def test_none_is_a_new_return_annotation():
    assert copy_signature(_source, return_annotation=None).return_annotation is None


def test_unset_keeps_the_original_annotation():
    assert copy_signature(_source, return_annotation=UNSET).return_annotation is str


def test_extra_parameters_come_after_the_copied_ones(names_of):
    result = copy_signature(_source, extra_params=[P("extra", P.KEYWORD_ONLY)])

    assert names_of(result) == ["a", "b", "args", "k", "extra", "kwargs"]


def test_an_extra_parameter_replaces_a_copied_one_by_default():
    result = copy_signature(_source, extra_params=[P("b", P.POSITIONAL_OR_KEYWORD, default=99)])

    assert result.parameters["b"].default == 99


def test_a_copied_parameter_stays_without_replace_double():
    result = copy_signature(
        _source, extra_params=[P("b", P.POSITIONAL_OR_KEYWORD, default=99)], replace_double=False,
    )

    assert result.parameters["b"].default == 1


def test_excluded_names_are_left_out(names_of):
    assert names_of(copy_signature(_source, excluded_names=["a", "k"])) == ["b", "args", "kwargs"]


def test_include_variadic_false_leaves_out_args_and_kwargs(names_of):
    assert names_of(copy_signature(_source, include_variadic=False)) == ["a", "b", "k"]


def test_include_binding_false_leaves_out_self(names_of):
    assert names_of(copy_signature(_Thing.method, include_binding=False)) == ["x"]


def test_binding_is_kept_by_default(names_of):
    assert names_of(copy_signature(_Thing.method)) == ["self", "x"]


def test_flat_mode(names_of):
    result = copy_signature(_source, flat_to_kwargs=True)

    assert str(result) == "(*, a: int, b=1, k, **kwargs) -> str"


def test_a_collision_is_refused_without_accept_double(subtests):
    exc = assert_exception_function(
        subtests,
        copy_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(function=_source, extra_params=[P("a", P.KEYWORD_ONLY)], accept_double=False),
        valid_params=Kwargs(function=_source, extra_params=[P("fresh", P.KEYWORD_ONLY)], accept_double=False),
        error_name="DUPLICATE PARAMETER ERROR",
        value="a",
    )

    assert isinstance(exc, ValueError)


def test_an_extra_args_replaces_the_copied_one(names_of):
    result = copy_signature(_source, extra_params=[P("rest", P.VAR_POSITIONAL)])

    assert names_of(result) == ["a", "b", "rest", "k", "kwargs"]


def test_a_signature_that_cannot_be_read_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        copy_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(function=_looped),
        error_name="SIGNATURE INTROSPECTION ERROR",
    )

    assert isinstance(exc, ValueError)


def test_the_original_function_is_not_touched():
    before = inspect.signature(_source)

    copy_signature(_source, excluded_names=["a"])

    assert inspect.signature(_source) == before


@pytest.mark.parametrize("names", [["a", "k"], ("a", "k"), {"a", "k"}, (n for n in ["a", "k"])])
def test_excluded_names_accept_any_iterable(names, names_of):
    assert names_of(copy_signature(_source, excluded_names=names)) == ["b", "args", "kwargs"]


@pytest.mark.parametrize("extras", [
    [P("extra", P.KEYWORD_ONLY)],
    (P("extra", P.KEYWORD_ONLY),),
    {P("extra", P.KEYWORD_ONLY)},
    (P("extra", P.KEYWORD_ONLY) for _ in range(1)),
])
def test_extra_params_accept_any_iterable(extras, names_of):
    result = copy_signature(_source, extra_params=extras)

    assert names_of(result) == ["a", "b", "args", "k", "extra", "kwargs"]


def test_the_items_of_a_generator_are_still_validated():
    with pytest.raises(ValidationError):
        copy_signature(_source, excluded_names=(n for n in [1]))