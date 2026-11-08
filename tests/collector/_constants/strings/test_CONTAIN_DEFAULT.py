from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT


def test_is_a_non_empty_string():
    assert isinstance(CONTAIN_DEFAULT, str) and CONTAIN_DEFAULT


def test_differs_from_the_other_tier():
    assert CONTAIN_DEFAULT != WITHOUT_DEFAULT
