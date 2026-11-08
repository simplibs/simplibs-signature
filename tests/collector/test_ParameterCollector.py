import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature import ARGS, KWARGS, ParameterCollector

P = inspect.Parameter
POS_ONLY, POK, VAR_POS, KW_ONLY, VAR_KW = (
    P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD, P.VAR_POSITIONAL, P.KEYWORD_ONLY, P.VAR_KEYWORD,
)


def test_starts_empty():
    assert ParameterCollector().get_ordered_params() == ()


def test_returns_a_tuple(make_param):
    collector = ParameterCollector()
    collector.add_param(make_param("x"))

    assert isinstance(collector.get_ordered_params(), tuple)


def test_orders_by_kind_whatever_the_insertion_order(make_param, names_of):
    collector = ParameterCollector()
    for param in (
        make_param("kw", VAR_KW),
        make_param("k", KW_ONLY),
        make_param("req", POK),
        make_param("a", VAR_POS),
        make_param("p", POS_ONLY),
        make_param("opt", POK, default=1),
    ):
        collector.add_param(param)

    ordered = collector.get_ordered_params()

    assert names_of(ordered) == ["p", "req", "opt", "a", "k", "kw"]
    inspect.Signature(ordered)  # a valid signature, or this raises


def test_required_keyword_only_goes_before_optional_ones(make_param, names_of):
    collector = ParameterCollector()
    collector.add_param(make_param("opt", KW_ONLY, default=1))
    collector.add_param(make_param("req", KW_ONLY))

    assert names_of(collector.get_ordered_params()) == ["req", "opt"]


def test_add_params_adds_in_the_order_given(make_param, names_of):
    collector = ParameterCollector()
    collector.add_params([make_param("a"), make_param("b"), make_param("c")])

    assert names_of(collector.get_ordered_params()) == ["a", "b", "c"]


def test_add_params_accepts_a_generator(make_param, names_of):
    collector = ParameterCollector()
    collector.add_params(make_param(name) for name in "xy")

    assert names_of(collector.get_ordered_params()) == ["x", "y"]


def test_validate_call_switch_is_accepted(make_param):
    collector = ParameterCollector(_validate_call=False)
    collector.add_param(make_param("x"), _validate_call=False)
    collector.add_params([make_param("y")], _validate_call=False)

    assert len(collector.get_ordered_params()) == 2


# --- exclusion -----------------------------------------------------------------

@pytest.mark.parametrize("excluded", [["x"], ("x",), {"x"}, (name for name in ["x"])])
def test_excluded_names_from_any_iterable(make_param, names_of, excluded):
    collector = ParameterCollector(excluded_names=excluded, _validate_call=False)
    collector.add_params([make_param("x"), make_param("y")], _validate_call=False)

    assert names_of(collector.get_ordered_params()) == ["y"]


def test_binding_names_are_kept_by_default(make_param, names_of):
    collector = ParameterCollector()
    collector.add_params([make_param("self"), make_param("cls"), make_param("x")])

    assert names_of(collector.get_ordered_params()) == ["self", "cls", "x"]


def test_include_binding_false_drops_self_and_cls(make_param, names_of):
    collector = ParameterCollector(include_binding=False)
    collector.add_params([make_param("self"), make_param("cls"), make_param("x")])

    assert names_of(collector.get_ordered_params()) == ["x"]


def test_variadics_are_kept_by_default(names_of):
    collector = ParameterCollector()
    collector.add_params([ARGS, KWARGS])

    assert names_of(collector.get_ordered_params()) == ["args", "kwargs"]


def test_include_variadic_false_drops_them_by_kind(make_param, names_of):
    collector = ParameterCollector(include_variadic=False)
    collector.add_params([
        make_param("x"),
        make_param("a", VAR_POS),
        make_param("options", VAR_KW),
        ARGS,
        KWARGS,
    ])

    assert names_of(collector.get_ordered_params()) == ["x"]


def test_include_variadic_false_keeps_self(make_param, names_of):
    collector = ParameterCollector(include_variadic=False)
    collector.add_param(make_param("self"))

    assert names_of(collector.get_ordered_params()) == ["self"]


# --- collisions ----------------------------------------------------------------

def test_collision_is_refused_without_accept_double(subtests, make_param):
    collector = ParameterCollector(accept_double=False)
    collector.add_param(make_param("x"))

    exc = assert_exception_function(
        subtests,
        collector.add_param,
        exception_type=ParamError,
        invalid_params=(make_param("x"),),
        error_name="DUPLICATE PARAMETER ERROR",
        value="x",
    )

    assert isinstance(exc, ValueError)


def test_the_later_parameter_wins_by_default(make_param):
    collector = ParameterCollector()
    collector.add_params([make_param("x", default=1), make_param("x", default=2)])

    [stored] = collector.get_ordered_params()
    assert stored.default == 2


def test_the_earlier_parameter_wins_without_replace_double(make_param):
    collector = ParameterCollector(replace_double=False)
    collector.add_params([make_param("x", default=1), make_param("x", default=2)])

    [stored] = collector.get_ordered_params()
    assert stored.default == 1


def test_a_second_args_replaces_the_first(make_param, names_of):
    collector = ParameterCollector()
    collector.add_params([make_param("a", VAR_POS), make_param("b", VAR_POS)])

    assert names_of(collector.get_ordered_params()) == ["b"]


def test_a_second_args_is_dropped_without_replace_double(make_param, names_of):
    collector = ParameterCollector(replace_double=False)
    collector.add_params([make_param("a", VAR_POS), make_param("b", VAR_POS)])

    assert names_of(collector.get_ordered_params()) == ["a"]


def test_a_second_kwargs_is_refused_without_accept_double(subtests, make_param):
    collector = ParameterCollector(accept_double=False)
    collector.add_param(make_param("kw", VAR_KW))

    assert_exception_function(
        subtests,
        collector.add_param,
        exception_type=ParamError,
        invalid_params=(make_param("options", VAR_KW),),
        problem="collides with the already defined variadic keyword parameter 'kw'",
    )


def test_a_collector_never_yields_two_variadics_of_one_kind(make_param):
    collector = ParameterCollector()
    collector.add_params([make_param("a", VAR_POS), make_param("b", VAR_POS), make_param("kw", VAR_KW), make_param("o", VAR_KW)])

    kinds = [p.kind for p in collector.get_ordered_params()]
    assert kinds.count(VAR_POS) == 1 and kinds.count(VAR_KW) == 1


# --- order ---------------------------------------------------------------------

def test_required_positional_after_optional_is_refused(subtests, make_param):
    collector = ParameterCollector()
    collector.add_param(make_param("a", default=1))

    exc = assert_exception_function(
        subtests,
        collector.add_param,
        exception_type=ParamError,
        invalid_params=(make_param("b"),),
        error_name="INVALID PARAMETER ORDER",
        value="b",
    )

    assert isinstance(exc, SyntaxError)


# --- flat mode -----------------------------------------------------------------

def test_flat_mode_makes_everything_keyword_only(make_param, names_of):
    collector = ParameterCollector(flat_to_kwargs=True)
    collector.add_params([
        make_param("p", POS_ONLY),
        make_param("x", default=1),
        make_param("a", VAR_POS),
        make_param("options", VAR_KW),
    ])

    ordered = collector.get_ordered_params()

    assert names_of(ordered) == ["p", "x", "kwargs"]
    assert [p.kind for p in ordered] == [KW_ONLY, KW_ONLY, VAR_KW]


def test_flat_mode_allows_what_the_normal_order_refuses(make_param, names_of):
    collector = ParameterCollector(flat_to_kwargs=True)
    collector.add_params([make_param("a", default=1), make_param("b")])

    assert names_of(collector.get_ordered_params()) == ["a", "b"]


def test_flat_mode_with_include_variadic_false_has_no_kwargs(make_param, names_of):
    collector = ParameterCollector(flat_to_kwargs=True, include_variadic=False)
    collector.add_params([make_param("x"), make_param("kw", VAR_KW)])

    assert names_of(collector.get_ordered_params()) == ["x"]


def test_flat_mode_renames_a_kept_duplicate(make_param, names_of):
    collector = ParameterCollector(flat_to_kwargs=True, replace_double=False)
    collector.add_params([make_param("x"), make_param("x")])

    assert names_of(collector.get_ordered_params()) == ["x", "x_1"]


# --- runtime validation --------------------------------------------------------

def test_rejects_something_that_is_not_a_parameter():
    with pytest.raises(Exception):
        ParameterCollector().add_param("x")
