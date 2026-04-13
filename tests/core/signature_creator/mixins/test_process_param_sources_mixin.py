"""
Tests for ProcessParamSourcesMixin — handles ingestion of parameters from various sources.
"""
import pytest
import inspect
from typing import Any, Callable

# Imports based on the provided project structure
from src.simplibs.signature.core.signature_creator._mixins.ProcessParamSources import ProcessParamSourcesMixin
from src.simplibs.signature.core.parameter_collector import ParameterCollector
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Mock Creator Class
# -----------------------------------------------------------------------------

class MockSignatureCreator(ProcessParamSourcesMixin):
    """
    A minimal mock class to provide the environment required by the mixin.
    """

    def __init__(self, **collector_kwargs):
        self._params_collector = ParameterCollector(**collector_kwargs)
        self._return_annotation = None


# -----------------------------------------------------------------------------
# Test Functions
# -----------------------------------------------------------------------------

def test_process_individual_parameters():
    """Should add individual inspect.Parameter objects directly to the collector."""
    creator = MockSignatureCreator()
    p1 = inspect.Parameter("a", inspect.Parameter.POSITIONAL_ONLY)
    p2 = inspect.Parameter("b", inspect.Parameter.KEYWORD_ONLY)

    # Process parameters
    creator._process_param_sources((p1, p2), return_source=None)

    ordered = creator._params_collector.get_ordered_params()
    assert len(ordered) == 2
    assert ordered[0].name == "a"
    assert ordered[1].name == "b"


def test_process_callable_source():
    """Should extract all parameters from a callable and add them to the collector."""
    creator = MockSignatureCreator()

    def source_func(x: int, y: str = "default"):
        pass

    creator._process_param_sources((source_func,), return_source=None)

    ordered = creator._params_collector.get_ordered_params()
    assert len(ordered) == 2
    assert ordered[0].name == "x"
    assert ordered[1].name == "y"
    assert ordered[1].default == "default"


def test_return_source_optimization():
    """
    Should capture the return annotation immediately if a callable 
    in param_sources is also the designated return_source.
    """
    creator = MockSignatureCreator()

    def source_func(a: int) -> str:
        pass

    # Mark source_func as both a parameter source AND the return source
    creator._process_param_sources((source_func,), return_source=source_func)

    # Verify optimization: return_annotation should be captured automatically
    assert creator._return_annotation is str


def test_mixed_sources_ordering():
    """Should handle mixed Parameters and Callables while maintaining Collector's order."""
    creator = MockSignatureCreator()

    def func_a(a: int): pass

    p_b = inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # Passing callable then individual parameter
    creator._process_param_sources((func_a, p_b), return_source=None)

    names = [p.name for p in creator._params_collector.get_ordered_params()]
    assert names == ["a", "b"]


def test_invalid_source_type_raises():
    """Should raise SignatureBuildError if a source is neither a Parameter nor a callable."""
    creator = MockSignatureCreator()

    invalid_item = "not_a_valid_source"

    with pytest.raises(SignatureBuildError) as exc_info:
        # Pass a string instead of a Parameter/Callable
        creator._process_param_sources((invalid_item,), return_source=None)  # type: ignore

    assert exc_info.value.error_name == "INVALID PARAMETER SOURCE"
    assert "param_sources[0]" in str(exc_info.value)
    assert "str" in str(exc_info.value)


def test_collector_rules_integration():
    """
    Verify that mixin respects Collector rules (e.g., deduplication) 
    when processing sources.
    """
    # Setup collector to NOT accept duplicates
    creator = MockSignatureCreator(accept_double=False)

    p1 = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    p2 = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError):
        # Adding same name twice should trigger Collector's error through the mixin
        creator._process_param_sources((p1, p2), return_source=None)