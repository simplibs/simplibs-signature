import inspect

from simplibs.signature import set_signature


def _target(a, b):
    return a + b


def _new_signature():
    return inspect.Signature([inspect.Parameter("only", inspect.Parameter.KEYWORD_ONLY)])


def test_changes_what_inspect_reports():
    function = _target
    signature = _new_signature()

    set_signature(function, signature)

    assert inspect.signature(function) == signature
    del function.__signature__


def test_returns_the_same_function():
    function = lambda a: a
    signature = _new_signature()

    assert set_signature(function, signature) is function


def test_does_not_change_how_the_function_runs():
    function = lambda a, b: a + b

    set_signature(function, _new_signature())

    assert function(1, 2) == 3


def test_validation_switch_is_accepted():
    function = lambda: None

    assert set_signature(function, _new_signature(), _validate_call=False) is function
