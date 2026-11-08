import inspect

from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import ParameterCollector
from simplibs.signature.orchestrators._helpers import load_param_sources

P = inspect.Parameter


def _first(a, b=1):
    ...


def _second(c, *rest):
    ...


class _Thing:
    def __init__(self, x): ...


def _load(*sources, **options):
    collector = ParameterCollector(**options)
    load_param_sources(collector=collector, param_sources=sources)
    return collector.get_ordered_params()


def test_a_parameter_goes_straight_in(names_of):
    assert names_of(_load(P("x", P.KEYWORD_ONLY))) == ["x"]


def test_a_callable_contributes_all_its_parameters(names_of):
    assert names_of(_load(_second)) == ["c", "rest"]


def test_a_class_is_a_callable_source(names_of):
    assert names_of(_load(_Thing)) == ["x"]


def test_sources_load_in_the_order_given(names_of):
    assert names_of(_load(_second, _first)) == ["c", "a", "b", "rest"]
    assert names_of(_load(_first, P("k", P.KEYWORD_ONLY), P("z", P.KEYWORD_ONLY))) == ["a", "b", "k", "z"]


def test_a_later_source_wins_a_collision_by_default():
    [param] = _load(P("x", P.KEYWORD_ONLY, default=1), P("x", P.KEYWORD_ONLY, default=2))

    assert param.default == 2


def test_an_earlier_source_wins_without_replace_double():
    [param] = _load(P("x", P.KEYWORD_ONLY, default=1), P("x", P.KEYWORD_ONLY, default=2), replace_double=False)

    assert param.default == 1


def test_no_sources_load_nothing():
    assert _load() == ()


def test_something_that_is_neither_is_refused(subtests):
    collector = ParameterCollector()

    exc = assert_exception_function(
        subtests,
        load_param_sources,
        exception_type=ParamError,
        invalid_params=Kwargs(collector=collector, param_sources=(_first, 5), _validate_call=False),
        error_name="INVALID PARAMETER SOURCE",
        label="param_sources[1]",
        value=5,
    )

    assert isinstance(exc, TypeError)
