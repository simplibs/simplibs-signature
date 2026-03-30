"""
Tests for create_copy_signature — return type, normalisation, return annotation, validation, and edge cases.
"""
import inspect
import pytest
from simplibs.sentinels import UNSET
from simplibs.signature.utils.signatures.create_copy_signature import create_copy_signature
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Return type
# -----------------------------------------------------------------------------

def test_returns_inspect_signature():
    """Must return an inspect.Signature instance."""
    def my_func(x: int): ...
    assert isinstance(create_copy_signature(my_func), inspect.Signature)


# -----------------------------------------------------------------------------
# Normalisation — default (normalize=True)
# -----------------------------------------------------------------------------

def test_self_is_removed():
    """self must be removed from the copied signature."""
    class MyClass:
        def __init__(self, name: str, value: int = 0): ...
    sig = create_copy_signature(MyClass.__init__)
    assert "self" not in sig.parameters


def test_cls_is_removed():
    """cls must be removed from the copied signature."""
    class MyClass:
        @classmethod
        def create(cls, name: str): ...
    sig = create_copy_signature(MyClass.create)
    assert "cls" not in sig.parameters


def test_kwargs_is_appended():
    """**kwargs must be appended at the end of the normalised signature."""
    def my_func(x: int, y: str): ...
    sig = create_copy_signature(my_func)
    last_param = list(sig.parameters.values())[-1]
    assert last_param.kind == inspect.Parameter.VAR_KEYWORD


def test_original_parameters_are_preserved():
    """Original parameters must be preserved after normalisation."""
    def my_func(x: int, y: str): ...
    sig = create_copy_signature(my_func)
    assert "x" in sig.parameters
    assert "y" in sig.parameters


# -----------------------------------------------------------------------------
# Normalisation — disabled (normalize=False)
# -----------------------------------------------------------------------------

def test_normalize_false_preserves_self():
    """normalize=False must preserve self in the signature."""
    class MyClass:
        def __init__(self, name: str): ...
    sig = create_copy_signature(MyClass.__init__, normalize=False)
    assert "self" in sig.parameters


def test_normalize_false_does_not_append_kwargs():
    """normalize=False must not append **kwargs."""
    def my_func(x: int): ...
    sig = create_copy_signature(my_func, normalize=False)
    param_kinds = [p.kind for p in sig.parameters.values()]
    assert inspect.Parameter.VAR_KEYWORD not in param_kinds


# -----------------------------------------------------------------------------
# Return annotation
# -----------------------------------------------------------------------------

def test_return_type_unset_preserves_original():
    """return_type=UNSET must preserve the original return annotation."""
    def my_func(x: int) -> str: ...
    sig = create_copy_signature(my_func, return_type=UNSET)
    assert sig.return_annotation == str


def test_return_type_none_removes_annotation():
    """return_type=None must remove the return annotation."""
    def my_func(x: int) -> str: ...
    sig = create_copy_signature(my_func, return_type=None)
    assert sig.return_annotation == inspect.Parameter.empty


def test_return_type_overrides_annotation():
    """A provided return_type must override the original return annotation."""
    def my_func(x: int) -> str: ...
    sig = create_copy_signature(my_func, return_type=int)
    assert sig.return_annotation == int


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_non_callable_raises():
    """A non-callable base_func must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        create_copy_signature(42)


def test_invalid_return_type_raises():
    """A non-type return_type must raise SignatureParameterError."""
    def my_func(): ...
    with pytest.raises(SignatureParameterError):
        create_copy_signature(my_func, return_type="int")


def test_builtin_without_signature_raises():
    """A built-in without introspectable signature must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError):
        create_copy_signature(object.__subclasshook__)