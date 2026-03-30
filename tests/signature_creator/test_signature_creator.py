"""
Tests for SignatureCreator — initialisation, validation, assembly, and return type priority.
"""
import inspect
import pytest
from simplibs.sentinels import UNSET
from simplibs.signature.signature_creator.SignatureCreator import SignatureCreator
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
# Valid construction
# -----------------------------------------------------------------------------

def test_sources_only_constructs():
    """SignatureCreator must construct successfully with only sources provided."""
    sc = SignatureCreator(make_param("x"))
    assert "x" in sc.signature.parameters


def test_base_func_only_constructs():
    """SignatureCreator must construct successfully with only base_func provided."""
    sc = SignatureCreator(base_func=func_a)
    assert "x" in sc.signature.parameters


def test_sources_and_base_func_constructs():
    """SignatureCreator must construct successfully with both sources and base_func."""
    sc = SignatureCreator(func_b, base_func=func_a)
    assert "x" in sc.signature.parameters
    assert "y" in sc.signature.parameters


# -----------------------------------------------------------------------------
# signature property
# -----------------------------------------------------------------------------

def test_signature_property_returns_inspect_signature():
    """The signature property must return an inspect.Signature instance."""
    sc = SignatureCreator(base_func=func_a)
    assert isinstance(sc.signature, inspect.Signature)


# -----------------------------------------------------------------------------
# Validation — missing parameter source
# -----------------------------------------------------------------------------

def test_no_sources_and_no_base_func_raises():
    """Providing neither sources nor base_func must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError) as exc_info:
        SignatureCreator()
    assert isinstance(exc_info.value, ValueError)


# -----------------------------------------------------------------------------
# Validation — invalid argument types
# -----------------------------------------------------------------------------

def test_invalid_base_func_raises():
    """A non-callable base_func must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        SignatureCreator(base_func=42)
    assert isinstance(exc_info.value, TypeError)


def test_invalid_base_func_first_raises():
    """A non-bool base_func_first must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        SignatureCreator(base_func=func_a, base_func_first=1)
    assert isinstance(exc_info.value, TypeError)


def test_invalid_return_type_raises():
    """A non-type, non-callable return_type must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        SignatureCreator(base_func=func_a, return_type=42)
    assert isinstance(exc_info.value, TypeError)


def test_invalid_excluded_names_raises():
    """A non-tuple excluded_names must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        SignatureCreator(base_func=func_a, excluded_names=["x"])


def test_invalid_accept_double_raises():
    """A non-bool accept_double must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        SignatureCreator(base_func=func_a, accept_double=1)


# -----------------------------------------------------------------------------
# Return type priority
# -----------------------------------------------------------------------------

def test_explicit_return_type_takes_priority_over_base_func():
    """An explicit return_type must take priority over base_func's annotation."""
    sc = SignatureCreator(base_func=func_a, return_type=int)
    assert sc.signature.return_annotation is int


def test_base_func_annotation_used_when_return_type_unset():
    """base_func's return annotation must be used when return_type is not provided."""
    sc = SignatureCreator(base_func=func_a)
    assert sc.signature.return_annotation is float


def test_empty_when_no_return_type_and_no_base_func_annotation():
    """inspect.Signature.empty must be used when neither return_type nor base_func annotation exists."""
    sc = SignatureCreator(base_func=func_no_annotation)
    assert sc.signature.return_annotation is inspect.Signature.empty


def test_none_return_type_sets_annotation_to_none():
    """return_type=None must set the return annotation to None (-> None)."""
    sc = SignatureCreator(base_func=func_a, return_type=None)
    assert sc.signature.return_annotation is None


# -----------------------------------------------------------------------------
# excluded_names forwarding
# -----------------------------------------------------------------------------

def test_excluded_names_are_forwarded_to_collector():
    """Parameters matching excluded_names must be excluded from the signature."""
    def func(x, my_param): ...
    sc = SignatureCreator(base_func=func, excluded_names=("my_param",))
    assert "my_param" not in sc.signature.parameters
    assert "x" in sc.signature.parameters


# -----------------------------------------------------------------------------
# accept_double forwarding
# -----------------------------------------------------------------------------

def test_accept_double_false_raises_on_duplicate():
    """accept_double=False must raise SignatureBuildError when duplicate parameters appear."""
    def func_x(x): ...
    with pytest.raises(SignatureBuildError):
        SignatureCreator(func_x, base_func=func_x, accept_double=False)