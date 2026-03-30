"""
Tests for create_signature — functional wrapper over SignatureCreator.
"""
import inspect
import pytest
from simplibs.signature.signature_creator.create_signature import create_signature
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


def func_a(x: int) -> float: ...
def func_b(y: str) -> list: ...
def func_no_annotation(z): ...


# -----------------------------------------------------------------------------
# Return type
# -----------------------------------------------------------------------------

def test_returns_inspect_signature():
    """create_signature must return an inspect.Signature instance."""
    sig = create_signature(base_func=func_a)
    assert isinstance(sig, inspect.Signature)


# -----------------------------------------------------------------------------
# Delegation — parameters
# -----------------------------------------------------------------------------

def test_sources_parameters_are_present():
    """Parameters from sources must appear in the returned signature."""
    sig = create_signature(make_param("x"), make_param("y"))
    assert "x" in sig.parameters
    assert "y" in sig.parameters


def test_base_func_parameters_are_present():
    """Parameters from base_func must appear in the returned signature."""
    sig = create_signature(base_func=func_a)
    assert "x" in sig.parameters


def test_return_type_is_forwarded():
    """An explicit return_type must appear as the return annotation."""
    sig = create_signature(base_func=func_a, return_type=int)
    assert sig.return_annotation is int


def test_base_func_return_annotation_inherited():
    """base_func return annotation must be inherited when return_type is omitted."""
    sig = create_signature(base_func=func_a)
    assert sig.return_annotation is float


def test_base_func_first_true_ordering():
    """With base_func_first=True, base_func parameters must precede sources parameters."""
    sig = create_signature(func_b, base_func=func_a, base_func_first=True)
    names = list(sig.parameters.keys())
    assert names.index("x") < names.index("y")


def test_base_func_first_false_ordering():
    """With base_func_first=False, sources parameters must precede base_func parameters."""
    sig = create_signature(func_b, base_func=func_a, base_func_first=False)
    names = list(sig.parameters.keys())
    assert names.index("y") < names.index("x")


def test_excluded_names_are_applied():
    """Parameters matching excluded_names must be absent from the returned signature."""
    def func(x, skip_me): ...
    sig = create_signature(base_func=func, excluded_names=("skip_me",))
    assert "skip_me" not in sig.parameters
    assert "x" in sig.parameters


def test_accept_double_false_raises_on_duplicate():
    """accept_double=False must raise SignatureBuildError on duplicate parameters."""
    def func_x(x): ...
    with pytest.raises(SignatureBuildError):
        create_signature(func_x, base_func=func_x, accept_double=False)


# -----------------------------------------------------------------------------
# Error propagation
# -----------------------------------------------------------------------------

def test_no_source_raises():
    """Calling with neither sources nor base_func must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError) as exc_info:
        create_signature()
    assert isinstance(exc_info.value, ValueError)


def test_invalid_base_func_raises():
    """A non-callable base_func must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_signature(base_func=42)
    assert isinstance(exc_info.value, TypeError)


def test_invalid_return_type_raises():
    """A non-type, non-callable return_type must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_signature(base_func=func_a, return_type=42)
    assert isinstance(exc_info.value, TypeError)