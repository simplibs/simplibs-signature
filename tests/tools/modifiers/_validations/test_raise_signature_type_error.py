from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.modifiers._validations import raise_signature_type_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_signature_type_error,
        exception_type=ParamError,
        invalid_params=(("x",), TypeError("bad type")),
        error_name="SIGNATURE TYPE ERROR",
        label="parameters",
        value=("x",),
        expected="valid inspect.Parameter objects",
        problem="An unexpected type error occurred during signature reconstruction.",
        how_to_fix=("Verify that all objects in params_to_add are proper inspect.Parameter instances.",),
        context="inspect.Signature.replace() — type validation",
    )

    assert isinstance(exc, TypeError)
