"""
Tests for compose_signature — factory for creating inspect.Signature instances.
"""
import pytest
import inspect
from typing import Any

from src.simplibs.signature.core.utils.operations.compose_signature import compose_signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid Signature Composition
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("collection_type", [tuple, list])
def test_compose_signature_success(collection_type):
    """Should successfully create a signature from various valid iterable types."""
    p1 = inspect.Parameter("a", inspect.Parameter.POSITIONAL_ONLY)
    p2 = inspect.Parameter("b", inspect.Parameter.KEYWORD_ONLY)
    params = collection_type([p1, p2])

    sig = compose_signature(params, return_annotation=int)

    assert isinstance(sig, inspect.Signature)
    assert sig.parameters["a"] == p1
    assert sig.parameters["b"] == p2
    assert sig.return_annotation is int


def test_compose_signature_with_generator():
    """Should successfully create a signature even from a one-time generator."""
    p = inspect.Parameter("gen", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    def param_generator():
        yield p

    sig = compose_signature(param_generator())

    assert isinstance(sig, inspect.Signature)
    assert sig.parameters["gen"] == p


def test_compose_signature_empty():
    """Should create an empty signature when no parameters are provided."""
    # Testing with an empty list to verify iterable support
    sig = compose_signature([])
    assert len(sig.parameters) == 0


# -----------------------------------------------------------------------------
# Structural Error Handling (ValueError)
# -----------------------------------------------------------------------------

def test_compose_signature_duplicate_names_raises():
    """Should raise SignatureBuildError (ValueError) if parameter names are not unique."""
    p1 = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    p2 = inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY)

    with pytest.raises(SignatureBuildError) as exc_info:
        compose_signature([p1, p2])

    assert isinstance(exc_info.value.__cause__, ValueError)


# -----------------------------------------------------------------------------
# Type/Attribute Error Handling
# -----------------------------------------------------------------------------

def test_compose_signature_non_iterable_raises():
    """Should raise SignatureParameterError if parameters is not iterable (when validate=True)."""
    with pytest.raises(SignatureParameterError):
        compose_signature(123)  # type: ignore


def test_compose_signature_non_parameter_items_raises():
    """
    Should raise SignatureBuildError (wrapping AttributeError) if collection
    contains non-Parameter objects and validation is bypassed.
    """
    with pytest.raises(SignatureBuildError) as exc_info:
        # validate=False to let it reach inspect.Signature
        compose_signature(["not_a_parameter"], validate=False)  # type: ignore

    assert exc_info.value.error_name == "SIGNATURE COMPOSITION ERROR"
    assert isinstance(exc_info.value.__cause__, AttributeError)
    assert "duck typing failed" in exc_info.value.context


# -----------------------------------------------------------------------------
# Validation Bypass & Internal Flag
# -----------------------------------------------------------------------------

def test_compose_signature_skip_validation_flag():
    """
    Verify that when validate=False, we can pass parameters in 'wrong' order
    without any error being raised, thanks to __validate_parameters__=False.
    """
    p_kwo = inspect.Parameter("k", inspect.Parameter.KEYWORD_ONLY)
    p_pos = inspect.Parameter("p", inspect.Parameter.POSITIONAL_ONLY)

    # This should now PASS and return a signature, even though the order is wrong
    # We pass it as a list to ensure that even without validation, list is okay
    sig = compose_signature([p_kwo, p_pos], validate=False)

    assert isinstance(sig, inspect.Signature)
    # Verify the 'wrong' order is preserved
    assert list(sig.parameters.keys()) == ["k", "p"]