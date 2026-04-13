"""
Tests for validate_is_inspect_signature — valid signatures, invalid types, and error fields.
"""
import pytest
import inspect
from simplibs.signature.core.validators._inspects.validate_is_inspect_signature import validate_is_inspect_signature
from simplibs.signature.core.validators.exceptions import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("source", [
    lambda x: x,            # Lambda
    len,                    # Built-in function (has signature)
    complex,                # Built-in type that has a signature in 3.11+
])
def test_valid_signatures_pass(source):
    """Signatures obtained via inspect.signature must pass."""
    sig = inspect.signature(source)
    validate_is_inspect_signature(sig)


def test_custom_class_signature_passes():
    """Signature of a custom class must pass."""
    class MyClass:
        def __init__(self, a, b=1): ...

    sig = inspect.signature(MyClass)
    validate_is_inspect_signature(sig)


def test_manually_constructed_signatures_pass():
    """Manually built or empty inspect.Signature objects must pass."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    validate_is_inspect_signature(inspect.Signature([param]))
    validate_is_inspect_signature(inspect.Signature([]))


# -----------------------------------------------------------------------------
# Invalid types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    42,                     # int
    "signature",            # str
    None,                   # None
    [],                     # list
    lambda x: x,            # function itself (not signature)
    inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY), # Parameter object
])
def test_non_signature_type_raises(value):
    """Any non-inspect.Signature value must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_is_inspect_signature(value, "my_param")


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields and useful message."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_inspect_signature("not_a_signature", "target_sig")

    e = exc_info.value
    assert e.value == "not_a_signature"
    assert e.value_label == "target_sig"
    assert e.error_name == "INVALID ARGUMENT ERROR"
    assert isinstance(e, TypeError)


# -----------------------------------------------------------------------------
# Default parameter value
# -----------------------------------------------------------------------------

def test_default_value_name_is_signature():
    """When value_name is not provided, it should default to 'signature'."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_is_inspect_signature(None)

    assert exc_info.value.value_label == "signature"