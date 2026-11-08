from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.operations._validations import raise_signature_composition_attribute_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_signature_composition_attribute_error,
        exception_type=ParamError,
        invalid_params=(["x"], AttributeError("kind")),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=["x"],
        expected="a collection of inspect.Parameter instances",
        problem="One or more items in the parameters collection are not valid Parameter objects.",
        how_to_fix=(
            "Ensure all items are created via inspect.Parameter() or our factory functions.",
            "Verify that you are not accidentally passing strings or other objects.",
        ),
        context="inspect.Signature() — duck typing failed (missing .name)",
    )

    assert isinstance(exc, AttributeError)
