import inspect

import pytest

from simplibs.signature import delete_params_from_signature


def _base(a, b=1, *args, k, **kwargs) -> str:
    ...


def test_removes_the_named_parameters():
    result = delete_params_from_signature(inspect.signature(_base), ["b", "k"])

    assert str(result) == "(a, *args, **kwargs) -> str"


def test_unknown_names_are_ignored():
    original = inspect.signature(_base)

    assert delete_params_from_signature(original, ["nope"]) == original


def test_removes_variadics_by_name():
    result = delete_params_from_signature(inspect.signature(_base), ["args", "kwargs"])

    assert str(result) == "(a, b=1, *, k) -> str"


def test_can_remove_everything(names_of):
    result = delete_params_from_signature(inspect.signature(_base), ["a", "b", "args", "k", "kwargs"])

    assert names_of(result) == []


def test_keeps_the_return_annotation():
    assert delete_params_from_signature(inspect.signature(_base), ["a"]).return_annotation is str


def test_does_not_change_the_original():
    original = inspect.signature(_base)

    delete_params_from_signature(original, ["a"])

    assert "a" in original.parameters


@pytest.mark.parametrize("names", [["a"], ("a",), {"a"}, (n for n in ["a"])])
def test_accepts_any_iterable_of_names(names, names_of):
    result = delete_params_from_signature(inspect.signature(_base), names)

    assert "a" not in names_of(result)


def test_the_result_is_always_a_valid_order(names_of):
    result = delete_params_from_signature(inspect.signature(_base), ["a", "args"])

    assert names_of(result) == ["b", "k", "kwargs"]
