from typing import Any

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.parameters._validations import validate_default_matches_annotation

EMPTY = __import__("inspect").Parameter.empty


@pytest.mark.parametrize("default, annotation, expected_name", [
    ("text", int, "int"),
    (1, str, "str"),
    ([], dict, "dict"),
    (1.5, int, "int"),
])
def test_mismatch_is_refused(subtests, default, annotation, expected_name):
    exc = assert_exception_function(
        subtests,
        validate_default_matches_annotation,
        exception_type=ParamError,
        invalid_params=(default, annotation),
        valid_params=(None, annotation),
        error_name="INVALID DEFAULT VALUE",
        label="default for parameter",
        value=default,
        expected=f"value of type {expected_name}",
        problem=f"The default value does not match its annotation '{expected_name}'.",
        how_to_fix=(
            f"Provide a default value of type {expected_name}.",
            "If unsure, remove the default or adjust the annotation.",
        ),
        exception=TypeError,
    )

    assert isinstance(exc, TypeError)


@pytest.mark.parametrize("default, annotation", [
    (5, int),
    (True, int),
    ("x", str),
    ([], list),
    (5, float | None),
    (5, "int"),
    (5, list[str]),
    (5, Any),
    (5, EMPTY),
    (EMPTY, int),
    (None, int),
    (None, EMPTY),
])
def test_clear_matches_and_undecidable_cases_pass(default, annotation):
    assert validate_default_matches_annotation(default, annotation) is None
