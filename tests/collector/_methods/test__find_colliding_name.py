import inspect

from simplibs.signature.collector._constants.kinds import VAR_KEYWORD, VAR_POSITIONAL
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT
from simplibs.signature.collector._methods._find_colliding_name import _find_colliding_name

VAR_POS = inspect.Parameter.VAR_POSITIONAL
VAR_KW = inspect.Parameter.VAR_KEYWORD


def _store(storage, param):
    seen, params_map = storage
    tier = WITHOUT_DEFAULT if param.default is param.empty else CONTAIN_DEFAULT
    params_map[param.kind][tier].append(param)
    seen[param.name] = (param.kind, tier)


def test_nothing_stored_means_no_collision(storage, make_param):
    seen, params_map = storage

    assert _find_colliding_name(make_param("x"), seen, params_map) is None


def test_the_same_name_collides(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    assert _find_colliding_name(make_param("x"), seen, params_map) == "x"


def test_the_same_name_collides_across_kinds(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    assert _find_colliding_name(make_param("x", inspect.Parameter.KEYWORD_ONLY), seen, params_map) == "x"


def test_another_name_does_not_collide(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    assert _find_colliding_name(make_param("y"), seen, params_map) is None


def test_a_second_args_collides_under_another_name(storage, make_param):
    _store(storage, make_param("a", VAR_POS))
    seen, params_map = storage

    assert _find_colliding_name(make_param("b", VAR_POS), seen, params_map) == "a"


def test_a_second_kwargs_collides_under_another_name(storage, make_param):
    _store(storage, make_param("kw", VAR_KW))
    seen, params_map = storage

    assert _find_colliding_name(make_param("options", VAR_KW), seen, params_map) == "kw"


def test_args_and_kwargs_do_not_collide_with_each_other(storage, make_param):
    _store(storage, make_param("a", VAR_POS))
    seen, params_map = storage

    assert _find_colliding_name(make_param("kw", VAR_KW), seen, params_map) is None


def test_a_variadic_does_not_collide_with_ordinary_parameters(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    assert _find_colliding_name(make_param("a", VAR_POS), seen, params_map) is None


def test_the_same_name_wins_over_the_variadic_slot(storage, make_param):
    _store(storage, make_param("a", VAR_POS))
    seen, params_map = storage

    assert _find_colliding_name(make_param("a", VAR_POS), seen, params_map) == "a"
