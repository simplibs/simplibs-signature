"""
Tests for ParameterCollector — integration of storage, validation, and tiered ordering.
"""
import pytest
import inspect
from simplibs.signature.core.parameter_collector import ParameterCollector
from simplibs.signature.core.validators.exceptions import SignatureParameterError, SignatureBuildError


# -----------------------------------------------------------------------------
# Initialization & Internal Structure
# -----------------------------------------------------------------------------

def test_collector_initialization_tiered_structure():
    """Collector must initialize the nested _params_map correctly."""
    collector = ParameterCollector()

    # Check tiered storage structure: 5 kinds, each with 2 categories
    assert len(collector._params_map) == 5
    for kind, categories in collector._params_map.items():
        assert collector._WITHOUT_DEFAULT in categories
        assert collector._CONTAIN_DEFAULT in categories
        assert isinstance(categories[collector._WITHOUT_DEFAULT], list)
        assert isinstance(categories[collector._CONTAIN_DEFAULT], list)


@pytest.mark.parametrize("param_name, invalid_value", [
    ("accept_double", 1),
    ("replace_double", "True"),
    ("include_variadic", None),
    ("include_binding", []),
    ("flat_to_kwargs", 10),
])
def test_collector_invalid_boolean_args_raise(param_name, invalid_value):
    """Non-bool arguments must raise SignatureParameterError during validation."""
    kwargs = {param_name: invalid_value}
    with pytest.raises(SignatureParameterError) as exc_info:
        ParameterCollector(**kwargs)

    assert isinstance(exc_info.value, TypeError)
    assert param_name in str(exc_info.value.value_label)


# -----------------------------------------------------------------------------
# Automated Exclusions (Variadic & Binding)
# -----------------------------------------------------------------------------

def test_combined_exclusions_logic():
    """Automated and custom exclusions must be merged into the set."""
    collector = ParameterCollector(
        excluded_names=["custom_val"],
        include_binding=False,
        include_variadic=False
    )

    # self, cls (binding) + args, kwargs (variadic) + custom
    assert "self" in collector._excluded_names
    assert "args" in collector._excluded_names
    assert "custom_val" in collector._excluded_names
    assert len(collector._excluded_names) >= 5


# -----------------------------------------------------------------------------
# Full Integration Flow (The "Real World" Test)
# -----------------------------------------------------------------------------

def test_collector_full_integration_order_and_tiers():
    """
    Test a complex scenario ensuring structural integrity:
    1. Mixing POSITIONAL_ONLY and POSITIONAL_OR_KEYWORD parameters.
    2. Adding them in a safe order (mandatory before optional).
    3. Verifying they are retrieved in strict Python-legal kind-order.
    """
    collector = ParameterCollector()

    # --- 1. Define Parameters ---
    p_pos_opt = inspect.Parameter("pos_opt", inspect.Parameter.POSITIONAL_ONLY, default=1)
    p_pos_mand = inspect.Parameter("pos_mand", inspect.Parameter.POSITIONAL_ONLY)
    p_pk_opt = inspect.Parameter("pk_opt", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="x")
    p_pk_mand = inspect.Parameter("pk_mand", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # --- 2. Add in Syntactically Legal Order ---
    # To satisfy the PositionalEmptyOrderCheckMixin, we must add all mandatory
    # positional-capable parameters before any positional-capable defaults.

    collector.add_param(p_pos_mand)  # Mandatory Positional-Only
    collector.add_param(p_pk_mand)  # Mandatory Positional-or-Keyword

    # Now we can safely add optional parameters
    collector.add_param(p_pos_opt)  # Optional Positional-Only
    collector.add_param(p_pk_opt)  # Optional Positional-or-Keyword

    # --- 3. Verify Internal Mapping (O(1) lookup index) ---
    assert collector._seen_names["pos_mand"] == (inspect.Parameter.POSITIONAL_ONLY, "no_default")
    assert collector._seen_names["pos_opt"] == (inspect.Parameter.POSITIONAL_ONLY, "default")
    assert collector._seen_names["pk_mand"] == (inspect.Parameter.POSITIONAL_OR_KEYWORD, "no_default")
    assert collector._seen_names["pk_opt"] == (inspect.Parameter.POSITIONAL_OR_KEYWORD, "default")

    # --- 4. Get Final Result ---
    result = collector.get_ordered_params()

    # --- 5. Final Order Verification ---
    # GetOrderedParamsMixin flattens tiers by:
    #   A) Kind Order (POS_ONLY -> POS_OR_KW -> ...)
    #   B) Category Order (no_default -> default)
    #
    # Result should be:
    # (pos_mand, pos_opt) then (pk_mand, pk_opt)
    expected = (p_pos_mand, p_pos_opt, p_pk_mand, p_pk_opt)

    assert result == expected
    assert len(result) == 4


def test_collector_order_violation_integration():
    """Collector must trigger SyntaxError (via mixin) if order is violated."""
    collector = ParameterCollector()

    # Add an optional parameter first
    collector.add_param(inspect.Parameter("a", inspect.Parameter.POSITIONAL_ONLY, default=5))

    # Adding a mandatory one now must fail
    with pytest.raises(SignatureBuildError) as exc_info:
        collector.add_param(inspect.Parameter("b", inspect.Parameter.POSITIONAL_ONLY))

    assert exc_info.value.exception is SyntaxError
    assert "INVALID PARAMETER ORDER" in exc_info.value.error_name


# -----------------------------------------------------------------------------
# Flat Mode Integration
# -----------------------------------------------------------------------------

def test_collector_flat_mode_integration():
    """When flat_to_kwargs is True, all additions must go through flattening logic."""
    collector = ParameterCollector(flat_to_kwargs=True)

    # Add a positional-only mandatory parameter
    p = inspect.Parameter("x", inspect.Parameter.POSITIONAL_ONLY)
    collector.add_param(p)

    result = collector.get_ordered_params()

    # Should be transformed to KEYWORD_ONLY and stored in 'default' category (as per flat logic)
    assert len(result) == 1
    assert result[0].name == "x"
    assert result[0].kind == inspect.Parameter.KEYWORD_ONLY
    assert collector._seen_names["x"] == (inspect.Parameter.KEYWORD_ONLY, "default")


def test_collector_duplicate_replacement_integration():
    """Verify O(1) replacement across tiered lists works in the main collector."""
    collector = ParameterCollector(replace_double=True)

    p_old = inspect.Parameter("name", inspect.Parameter.POSITIONAL_ONLY, default=10)
    p_new = inspect.Parameter("name", inspect.Parameter.KEYWORD_ONLY)

    collector.add_param(p_old)
    collector.add_param(p_new) # Should remove p_old from POS_ONLY/default and add p_new to KW_ONLY/no_default

    result = collector.get_ordered_params()
    assert len(result) == 1
    assert result[0].kind == inspect.Parameter.KEYWORD_ONLY
    assert collector._seen_names["name"] == (inspect.Parameter.KEYWORD_ONLY, "no_default")