"""
Tests for signature_copy — decorator factory for copying and normalising signatures.
"""
import inspect
import pytest
from simplibs.signature.signature_decorators.signature_copy import signature_copy
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

class MyClass:
    def __init__(self, x: int, y: str) -> None: ...

def standalone(a: float, b: bool) -> list: ...


# -----------------------------------------------------------------------------
# Return value
# -----------------------------------------------------------------------------

def test_returns_callable():
    """signature_copy must return a callable (the decorator)."""
    decorator = signature_copy(standalone)
    assert callable(decorator)


# -----------------------------------------------------------------------------
# Signature application
# -----------------------------------------------------------------------------

def test_signature_is_applied():
    """The decorated function must have the copied signature."""
    @signature_copy(standalone)
    def wrapper(*args, **kwargs): ...

    sig = inspect.signature(wrapper)
    assert "a" in sig.parameters
    assert "b" in sig.parameters


# -----------------------------------------------------------------------------
# Normalisation — self/cls removal
# -----------------------------------------------------------------------------

def test_self_is_removed():
    """self must be removed from the copied signature."""
    @signature_copy(MyClass.__init__)
    def wrapper(*args, **kwargs): ...

    assert "self" not in inspect.signature(wrapper).parameters


def test_cls_is_removed():
    """cls must be removed from the copied signature."""
    class Meta:
        def __init__(cls, x): ...

    @signature_copy(Meta.__init__)
    def wrapper(*args, **kwargs): ...

    assert "cls" not in inspect.signature(wrapper).parameters


# -----------------------------------------------------------------------------
# Normalisation — **kwargs appended
# -----------------------------------------------------------------------------

def test_kwargs_is_appended():
    """**kwargs must be appended to the copied signature."""
    @signature_copy(standalone)
    def wrapper(*args, **kwargs): ...

    sig = inspect.signature(wrapper)
    var_keyword_params = [
        p for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_KEYWORD
    ]
    assert len(var_keyword_params) == 1
    assert var_keyword_params[0].name == "kwargs"


# -----------------------------------------------------------------------------
# return_type handling
# -----------------------------------------------------------------------------

def test_return_type_unset_preserves_original():
    """return_type=UNSET must preserve the original return annotation."""
    @signature_copy(standalone)
    def wrapper(*args, **kwargs): ...

    assert inspect.signature(wrapper).return_annotation is list


def test_return_type_none_removes_annotation():
    """return_type=None must remove the return annotation."""
    @signature_copy(standalone, return_type=None)
    def wrapper(*args, **kwargs): ...

    assert inspect.signature(wrapper).return_annotation is inspect.Signature.empty


def test_return_type_replaces_annotation():
    """An explicit return_type must replace the original return annotation."""
    @signature_copy(MyClass.__init__, return_type=MyClass)
    def wrapper(*args, **kwargs): ...

    assert inspect.signature(wrapper).return_annotation is MyClass


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_invalid_base_func_raises():
    """A non-callable base_func must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        signature_copy(42)
    assert isinstance(exc_info.value, TypeError)