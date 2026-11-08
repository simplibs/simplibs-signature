from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.modifiers._validations import raise_signature_structure_value_error


def test_raises_the_error_with_its_fields(subtests):
    params = (1, 2)

    exc = assert_exception_function(
        subtests,
        raise_signature_structure_value_error,
        exception_type=ParamError,
        invalid_params=(params, ValueError("bad structure")),
        error_name="SIGNATURE STRUCTURE ERROR",
        label="params_to_add",
        value=params,
        expected="parameters that form a valid Python signature",
        problem="The resulting signature structure is invalid (e.g. invalid order or duplicate names).",
        how_to_fix=(
            "Check if the combination of existing and new parameters violates Python rules.",
            "Verify parameter order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
            "Verify that no parameter name occurs twice.",
        ),
        context="inspect.Signature.replace() — structural validation",
    )

    assert isinstance(exc, ValueError)
