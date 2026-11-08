import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs
from simplibs.sentinels import UNSET

from simplibs.signature.orchestrators._helpers import resolve_return_annotation


def _annotated(x) -> int:
    ...


def _plain(x):
    ...


def _looped():
    ...


_looped.__wrapped__ = _looped


def test_unset_means_no_annotation():
    assert resolve_return_annotation(UNSET) is inspect.Signature.empty


def test_none_is_an_annotation_not_a_missing_one():
    assert resolve_return_annotation(None) is None


@pytest.mark.parametrize("annotation", [int, str, list[int], dict[str, int], int | None, "later"])
def test_an_annotation_is_returned_as_it_is(annotation):
    assert resolve_return_annotation(annotation) == annotation


def test_a_class_is_an_annotation_not_a_function_to_copy_from():
    assert resolve_return_annotation(int) is int


def test_a_function_gives_its_return_annotation():
    assert resolve_return_annotation(_annotated) is int


def test_a_function_without_annotation_gives_none_at_all():
    assert resolve_return_annotation(_plain) is inspect.Signature.empty


def test_a_function_that_cannot_be_read_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        resolve_return_annotation,
        exception_type=ParamError,
        invalid_params=Kwargs(return_source=_looped),
        valid_params=Kwargs(return_source=_annotated),
        error_name="SIGNATURE INTROSPECTION ERROR",
    )

    assert isinstance(exc, ValueError)
