from .modifiers import (
    add_params_to_signature,
    delete_params_from_signature,
    replace_return_annotation_in_signature,
)
from .operations import (
    compose_signature,
    get_signature,
    set_signature,
)
from .parameters import (
    create_keyword_parameter,
    create_positional_parameter,
)


_DESIGN_NOTES = """
# Signature Tools Sub-Package

## Purpose
The small, independent building blocks: create a parameter, read / build /
attach a signature, change a signature. They do not depend on the orchestrators
or decorators above them. Plain imports, no `__all__`: the package root decides
what is public.

## Internal Components Registry

| Component    | Type        | Description                                                  |
| :----------- | :---------- | :----------------------------------------------------------- |
| `modifiers`  | Sub-package | Return a changed copy of a signature.                        |
| `operations` | Sub-package | Read, build and attach a signature.                          |
| `parameters` | Sub-package | Constructors of `inspect.Parameter`.                         |

## Where `load_param_sources` and `resolve_return_annotation` Went
They used to be exported from here. They serve only `create_signature`, so they
live next to it in `orchestrators/_helpers`.
"""
