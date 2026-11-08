import inspect

from simplibs.signature.collector._constants.kinds import EMPTY


def test_is_the_inspect_marker():
    assert EMPTY is inspect.Parameter.empty


def test_marks_a_parameter_without_default():
    assert inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD).default is EMPTY
