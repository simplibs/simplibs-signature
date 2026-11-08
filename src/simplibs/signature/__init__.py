from .collector import ParameterCollector
from .constants import (
    ARGS,
    KWARGS,
)
from .decorators import (
    apply_signature_to_wraps,
    create_signature_decorator,
    signature,
    signature_copy,
    signature_set,
)
from .orchestrators import (
    copy_signature,
    create_signature,
)
from .tools import (
    add_params_to_signature,
    compose_signature,
    create_keyword_parameter,
    create_positional_parameter,
    delete_params_from_signature,
    get_signature,
    replace_return_annotation_in_signature,
    set_signature,
)


__all__ = [
    # Builders
    "create_signature",
    "copy_signature",
    # Decorators
    "signature",
    "signature_copy",
    "signature_set",
    # Parameter collector
    "ParameterCollector",
    # Signature operations
    "get_signature",
    "set_signature",
    "compose_signature",
    # Signature modifiers
    "add_params_to_signature",
    "delete_params_from_signature",
    "replace_return_annotation_in_signature",
    # Parameter creators
    "create_positional_parameter",
    "create_keyword_parameter",
    # Decorator builders
    "apply_signature_to_wraps",
    "create_signature_decorator",
    # Constants
    "ARGS",
    "KWARGS",
]


_DESIGN_NOTES = """
# simplibs.signature — Build, Copy and Attach Function Signatures

## Purpose
A wrapper that takes `(*args, **kwargs)` hides what it really accepts from IDEs,
documentation tools and `inspect`. This package builds the signature the wrapper
should report: from parameters, from other functions or from both, merged in a
valid order, and attaches it.

## Public API
This file is the only place where the public API is decided (`__all__`); every
sub-package uses plain imports.

| Name                                     | Type      | Description                                            |
| :--------------------------------------- | :-------- | :----------------------------------------------------- |
| `create_signature`                       | Function  | A signature from any mix of parameters and callables.  |
| `copy_signature`                         | Function  | A changed copy of one callable's signature.            |
| `signature`                              | Decorator | Assembles a signature from several sources.            |
| `signature_copy`                         | Decorator | Copies another callable's signature, with changes.     |
| `signature_set`                          | Decorator | Attaches a finished signature.                         |
| `ParameterCollector`                     | Class     | Collects parameters into one valid, ordered set.       |
| `get_signature`                          | Function  | Reads a signature with a readable failure.             |
| `set_signature`                          | Function  | Attaches a signature through `__signature__`.          |
| `compose_signature`                      | Function  | Builds an `inspect.Signature`, always validated.       |
| `add_params_to_signature`                | Function  | A copy of a signature with parameters added.           |
| `delete_params_from_signature`           | Function  | A copy of a signature without the named parameters.    |
| `replace_return_annotation_in_signature` | Function  | A copy of a signature with another return annotation.  |
| `create_positional_parameter`            | Function  | A positional-only or ordinary parameter.               |
| `create_keyword_parameter`               | Function  | A keyword-only parameter.                              |
| `apply_signature_to_wraps`               | Function  | A transparent wrapper reporting a given signature.     |
| `create_signature_decorator`             | Function  | A decorator that applies a fixed signature.            |
| `ARGS`, `KWARGS`                         | Constants | Ready-made `*args` and `**kwargs` parameters.          |

## Internal Components Registry

| Component       | Type        | Description                                                  |
| :-------------- | :---------- | :----------------------------------------------------------- |
| `collector`     | Sub-package | `ParameterCollector`: exclusion, collisions and order.       |
| `constants`     | Sub-package | `ARGS` and `KWARGS`.                                         |
| `decorators`    | Sub-package | The three decorators and the builders they are made of.      |
| `orchestrators` | Sub-package | `create_signature` and `copy_signature`.                     |
| `tools`         | Sub-package | Parameter creators, signature operations and modifiers.      |

## How the Layers Fit
`decorators` use `orchestrators`; `orchestrators` use the `collector` and
`tools.operations`; `tools.modifiers` use the `collector`. Nothing points back
up, so every layer can be used and tested without the ones above it.

## Rules Shared by Every Builder
The same options mean the same thing in `create_signature`, `copy_signature`, the
decorators and (where offered) the modifiers.

| Option             | Meaning                                                                  |
| :----------------- | :----------------------------------------------------------------------- |
| `accept_double`    | If False, a name collision raises `ParamError`.                          |
| `replace_double`   | Who wins a collision: the later parameter (True) or the earlier one.     |
| `include_variadic` | If False, every `*args` and `**kwargs` is left out, whatever its name.   |
| `include_binding`  | If False, parameters named `self` and `cls` are left out.                |
| `flat_to_kwargs`   | Everything keyword-only; `*args` dropped, all `**kwargs` merged into one.|

A signature holds one `*args` and one `**kwargs`. A second one counts as a
collision even under another name. With `replace_double=False` flat mode keeps
both colliding parameters and renames the later one to `name_1`, `name_2`, ...

## `_validate_call`
Every public function is decorated with `@validate_call` and has the reserved
keyword `_validate_call`. False skips the validation of that call's arguments.
Internal calls pass False, because the outermost call has already validated them.
It never changes what a function does with valid input. `compose_signature` is
the example: the structure of the result is always checked.

## Where an Error Points
Every error is a `ParamError` from `simplibs-exception`. It leaves all simplibs
frames out of the reported location, so the message points at the code that
called the library; only if no other frame is left does it fall back to the
last one. That is why no file here sets `skip_locations`. Where an error wraps
a standard one (`ValueError`, `TypeError`, `SyntaxError`, ...), the standard type
is in its MRO and existing `except` clauses keep working.
"""
