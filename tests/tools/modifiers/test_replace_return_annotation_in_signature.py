import inspect

import pytest

from simplibs.signature import replace_return_annotation_in_signature


def _base(a, b=1) -> str:
    ...


def test_changes_the_return_annotation():
    result = replace_return_annotation_in_signature(inspect.signature(_base), int)

    assert result.return_annotation is int


def test_keeps_the_parameters():
    original = inspect.signature(_base)

    result = replace_return_annotation_in_signature(original, int)

    assert result.parameters == original.parameters


def test_empty_removes_the_annotation():
    result = replace_return_annotation_in_signature(inspect.signature(_base), inspect.Signature.empty)

    assert result.return_annotation is inspect.Signature.empty


def test_none_is_a_real_annotation():
    result = replace_return_annotation_in_signature(inspect.signature(_base), None)

    assert result.return_annotation is None


@pytest.mark.parametrize("annotation", ["str", list[int], int | None])
def test_the_value_is_not_interpreted(annotation):
    result = replace_return_annotation_in_signature(inspect.signature(_base), annotation)

    assert result.return_annotation == annotation


def test_does_not_change_the_original():
    original = inspect.signature(_base)

    replace_return_annotation_in_signature(original, int)

    assert original.return_annotation is str
