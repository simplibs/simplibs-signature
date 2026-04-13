"""
Tests for ProcessReturnSourceMixin — finalizes the return annotation for a signature.
"""
import pytest
import inspect
from typing import List, Union, Optional
from simplibs.sentinels import UNSET

# Imports based on the provided project structure
from src.simplibs.signature.core.signature_creator._mixins.ProcessReturnSource import ProcessReturnSourceMixin


# -----------------------------------------------------------------------------
# Mock Creator Class
# -----------------------------------------------------------------------------

class MockReturnCreator(ProcessReturnSourceMixin):
    """
    A minimal mock class to provide the environment required by the mixin.
    """

    def __init__(self):
        self._return_annotation = UNSET


# -----------------------------------------------------------------------------
# Test Functions
# -----------------------------------------------------------------------------

def test_process_unset_defaults_to_empty():
    """Should set _return_annotation to inspect.Signature.empty when source is UNSET."""
    creator = MockReturnCreator()

    creator._process_return_source(UNSET)

    assert creator._return_annotation is inspect.Signature.empty


def test_process_callable_extracts_annotation():
    """Should extract the return annotation from a provided callable."""
    creator = MockReturnCreator()

    def source_func() -> List[str]:
        pass

    creator._process_return_source(source_func)

    assert creator._return_annotation == List[str]


def test_process_callable_with_no_annotation():
    """Should result in inspect.Signature.empty if the callable has no return hint."""
    creator = MockReturnCreator()

    def no_hint_func(a, b):
        pass

    creator._process_return_source(no_hint_func)

    assert creator._return_annotation is inspect.Signature.empty


def test_process_direct_type_annotation():
    """Should accept a standard type (int, str, etc.) directly as an annotation."""
    creator = MockReturnCreator()

    creator._process_return_source(int)
    assert creator._return_annotation is int


def test_process_complex_typing_annotation():
    """Diagnostic test to see why Optional[int] fails."""
    from typing import Optional
    import inspect

    creator = MockReturnCreator()
    complex_hint = Optional[int]

    # --- Diagnostic prints ---
    print(f"\nValue: {complex_hint}")
    print(f"Is callable: {callable(complex_hint)}")
    print(f"Is class: {inspect.isclass(complex_hint)}")
    print(f"Is UNSET: {complex_hint is UNSET}")

    creator._process_return_source(complex_hint)

    print(f"Result in creator: {creator._return_annotation}")
    print(f"Type of result: {type(creator._return_annotation)}")
    # -------------------------

    assert creator._return_annotation == Optional[int]


def test_process_string_forward_reference():
    """Should accept a string as a forward reference annotation."""
    creator = MockReturnCreator()
    forward_ref = "MyFutureClass"

    creator._process_return_source(forward_ref)
    assert creator._return_annotation == "MyFutureClass"


def test_process_none_as_annotation():
    """Should accept None as a valid return annotation (common in Python)."""
    creator = MockReturnCreator()

    creator._process_return_source(None)
    assert creator._return_annotation is None


def test_process_arbitrary_object_as_annotation():
    """
    Verify that any arbitrary object is accepted (Python's permissive nature),
    ensuring no unexpected exceptions are raised.
    """
    creator = MockReturnCreator()
    custom_obj = object()

    creator._process_return_source(custom_obj)
    assert creator._return_annotation is custom_obj