from simplibs.signature.collector._constants.kinds import KEYWORD_ONLY, POSITIONAL_OR_KEYWORD
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT
from simplibs.signature.collector._methods._remove_param import _remove_param


def _store(storage, param):
    seen, params_map = storage
    tier = WITHOUT_DEFAULT if param.default is param.empty else CONTAIN_DEFAULT
    params_map[param.kind][tier].append(param)
    seen[param.name] = (param.kind, tier)


def test_removes_the_parameter_and_forgets_the_name(storage, make_param):
    x, y = make_param("x"), make_param("y")
    _store(storage, x)
    _store(storage, y)
    seen, params_map = storage

    _remove_param("x", seen, params_map)

    assert params_map[POSITIONAL_OR_KEYWORD][WITHOUT_DEFAULT] == [y]
    assert "x" not in seen
    assert "y" in seen


def test_looks_into_the_tier_the_index_points_to(storage, make_param):
    required = make_param("a", KEYWORD_ONLY)
    optional = make_param("b", KEYWORD_ONLY, default=1)
    _store(storage, required)
    _store(storage, optional)
    seen, params_map = storage

    _remove_param("b", seen, params_map)

    assert params_map[KEYWORD_ONLY][WITHOUT_DEFAULT] == [required]
    assert params_map[KEYWORD_ONLY][CONTAIN_DEFAULT] == []


def test_unknown_name_changes_nothing(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    _remove_param("nope", seen, params_map)

    assert list(seen) == ["x"]
    assert len(params_map[POSITIONAL_OR_KEYWORD][WITHOUT_DEFAULT]) == 1


def test_a_removed_name_can_be_stored_again(storage, make_param):
    _store(storage, make_param("x"))
    seen, params_map = storage

    _remove_param("x", seen, params_map)
    _store(storage, make_param("x", default=5))

    assert seen["x"] == (POSITIONAL_OR_KEYWORD, CONTAIN_DEFAULT)
