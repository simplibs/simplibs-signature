import importlib

import pytest

import simplibs.signature as root

PUBLIC = {
    "create_signature", "copy_signature",
    "signature", "signature_copy", "signature_set",
    "ParameterCollector",
    "get_signature", "set_signature", "compose_signature",
    "add_params_to_signature", "delete_params_from_signature", "replace_return_annotation_in_signature",
    "create_positional_parameter", "create_keyword_parameter",
    "apply_signature_to_wraps", "create_signature_decorator",
    "ARGS", "KWARGS",
}

SUB_PACKAGES = [
    "collector",
    "collector._constants",
    "collector._constants.groups",
    "collector._constants.kinds",
    "collector._constants.strings",
    "collector._methods",
    "collector._methods.validations",
    "constants",
    "decorators",
    "decorators.builders",
    "orchestrators",
    "orchestrators._helpers",
    "orchestrators._helpers._validations",
    "tools",
    "tools.modifiers",
    "tools.modifiers._validations",
    "tools.operations",
    "tools.operations._validations",
    "tools.parameters",
    "tools.parameters._validations",
]


def test_public_api_is_exactly_this():
    assert set(root.__all__) == PUBLIC


def test_there_are_no_duplicates_in_all():
    assert len(root.__all__) == len(set(root.__all__))


@pytest.mark.parametrize("name", sorted(PUBLIC))
def test_every_public_name_exists(name):
    assert hasattr(root, name)


@pytest.mark.parametrize("name", SUB_PACKAGES)
def test_sub_packages_import_and_define_no_all(name):
    module = importlib.import_module(f"simplibs.signature.{name}")

    assert not hasattr(module, "__all__")


def test_every_design_notes_block_is_present():
    import pathlib

    package = pathlib.Path(root.__file__).parent
    missing = [
        str(path.relative_to(package))
        for path in package.rglob("*.py")
        if "_DESIGN_NOTES" not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
