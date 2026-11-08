from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.operations._validations import raise_signature_composition_type_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_signature_composition_type_error,
        exception_type=ParamError,
        invalid_params=(5, TypeError("not iterable")),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=5,
        expected="an iterable of inspect.Parameter instances",
        problem="The parameters collection or return_annotation is of an unsupported type.",
        how_to_fix=(
            "Ensure all items in the parameters collection are inspect.Parameter instances.",
            "Use create_keyword_parameter() and create_positional_parameter() to construct parameters.",
        ),
        context="inspect.Signature() — type mismatch during construction",
    )

    assert isinstance(exc, TypeError)
