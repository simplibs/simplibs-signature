"""
Tests for replace_return_annotation_in_signature — updating return type hints in signatures.
"""
import pytest
import inspect
from typing import List, Any

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.modifiers.replace_return_annotation_in_signature import replace_return_annotation_in_signature
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def base_signature():
    """Provides a basic signature: (a: int) -> int"""
    p = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    return inspect.Signature(parameters=(p,), return_annotation=int)


# -----------------------------------------------------------------------------
# Successful Annotation Replacement
# -----------------------------------------------------------------------------

def test_replace_with_standard_type(base_signature):
    """Should replace the return annotation with a standard Python type."""
    new_sig = replace_return_annotation_in_signature(base_signature, str)

    assert new_sig.return_annotation is str
    # Parameters should remain unchanged
    assert new_sig.parameters["a"].annotation is int


def test_replace_with_complex_type(base_signature):
    """Should replace the return annotation with a complex/generic type."""
    new_annotation = List[str]
    new_sig = replace_return_annotation_in_signature(base_signature, new_annotation)

    assert new_sig.return_annotation == List[str]


def test_replace_with_string_forward_reference(base_signature):
    """Should replace the return annotation with a string forward reference."""
    new_sig = replace_return_annotation_in_signature(base_signature, "CustomClass")

    assert new_sig.return_annotation == "CustomClass"


def test_clear_annotation_using_empty(base_signature):
    """Should remove the return annotation by setting it to inspect.Signature.empty."""
    new_sig = replace_return_annotation_in_signature(
        base_signature,
        inspect.Signature.empty
    )

    assert new_sig.return_annotation is inspect.Signature.empty


# -----------------------------------------------------------------------------
# Immutability & Validation
# -----------------------------------------------------------------------------

def test_original_signature_is_not_modified(base_signature):
    """Verify that the source signature remains unchanged (immutability check)."""
    replace_return_annotation_in_signature(base_signature, float)
    assert base_signature.return_annotation is int


def test_invalid_signature_type_raises():
    """Should raise SignatureParameterError if the input is not a Signature object."""
    with pytest.raises(SignatureParameterError):
        replace_return_annotation_in_signature("not_a_signature", int)  # type: ignore


def test_skip_validation_bypass():
    """Should skip type checks when validate=False."""
    # Passing an invalid type for signature should not raise SignatureParameterError
    # but will likely fail inside inspect.Signature.replace() or similar
    try:
        replace_return_annotation_in_signature("invalid", int, validate=False)  # type: ignore
    except (AttributeError, TypeError):
        # We expect a standard Python error since our custom validator was bypassed
        pass