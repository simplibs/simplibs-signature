# 🔧 `tools` — The Small Building Blocks

The `tools` package holds the **independent functions** everything else is made of: create a parameter, read,
build and attach a signature, change a signature. They know nothing about the
[orchestrators](README_SIGNATURE_ORCHESTRATORS.md) or the [decorators](README_SIGNATURE_DECORATORS.md) above
them — and each is useful on its own.

```python
from simplibs.signature import (
    create_positional_parameter, create_keyword_parameter, ARGS, KWARGS,                      # parameters
    get_signature, set_signature, compose_signature,                                          # operations
    add_params_to_signature, delete_params_from_signature, replace_return_annotation_in_signature,   # modifiers
)
```

| Group          | Functions                                                                                      | Changes the input? |
|----------------|------------------------------------------------------------------------------------------------|--------------------|
| **Parameters** | `create_positional_parameter`, `create_keyword_parameter`, `ARGS`, `KWARGS`                     | — (they create)    |
| **Operations** | `get_signature`, `compose_signature`, `set_signature`                                           | only `set_signature` — and it says so |
| **Modifiers**  | `add_params_to_signature`, `delete_params_from_signature`, `replace_return_annotation_in_signature` | **never** — each returns a new signature |

```python
import inspect
from simplibs.signature import add_params_to_signature, create_keyword_parameter

def original(a: int, b: str = "x", *args, **kwargs) -> bool: ...

sig = inspect.signature(original)
new = add_params_to_signature(sig, [create_keyword_parameter("dry_run", annotation=bool, default=False)])

str(new)     # -> "(a: int, b: str = 'x', *args, dry_run: bool = False, **kwargs) -> bool"
str(sig)     # -> "(a: int, b: str = 'x', *args, **kwargs) -> bool"       the original is as it was
```

## A note on `_validate_call`

Every public function here has a reserved keyword-only `_validate_call`, the switch of `@validate_call`:
`False` skips the validation of the **arguments** of that call. It exists for the library's own inner calls,
which trust values that were already checked. It never changes what a function does with valid input — the
structure of a composed signature, for example, is **always** checked.

---

## 🧭 Table of Contents

**🧱 Parameters**

* [`create_positional_parameter`](#create_positional_parameter)
* [`create_keyword_parameter`](#create_keyword_parameter)
* [`ARGS` and `KWARGS`](#args-and-kwargs)

**🔬 Operations**

* [`get_signature`](#get_signature)
* [`compose_signature`](#compose_signature)
* [`set_signature`](#set_signature)

**🩹 Modifiers**

* [`add_params_to_signature`](#add_params_to_signature)
* [`delete_params_from_signature`](#delete_params_from_signature)
* [`replace_return_annotation_in_signature`](#replace_return_annotation_in_signature)

[Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../__DOC__/README.md#-tools--the-small-building-blocks)

---

## 🧱 Parameters

Short, readable constructors of `inspect.Parameter`. `inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY,
default=1)` hides the interesting part — the name and the default — behind the kind; these say only what a
caller means. In both, `annotation` and `default` must be **named**, so a call never has to be decoded by position.

[▲ Back to top](#-table-of-contents)

---

### `create_positional_parameter`

Creates a **positional** parameter: ordinary (passed by position or by name) by default, positional-only on request.

**Parameters:**

| Name              | Type   | Default | Description                                                              |
|-------------------|--------|---------|--------------------------------------------------------------------------|
| `name`            | `str`  |         | The parameter name.                                                       |
| `annotation`      | `Any`  | *none*  | The annotation. *(keyword-only)*                                          |
| `default`         | `Any`  | *none*  | The default value; without it the parameter is required. *(keyword-only)* |
| `positional_only` | `bool` | `False` | If `True`, the parameter can only be passed by position. *(keyword-only)* |
| `_validate_call`  | `bool` | `True`  | Reserved switch of `@validate_call`; also gates the default check. *(keyword-only)* |

**Returns:** an `inspect.Parameter` of kind `POSITIONAL_OR_KEYWORD`, or `POSITIONAL_ONLY` with `positional_only=True`.

**Raises:**
`ParamError` — `INVALID DEFAULT VALUE`: `default` does not fit a plain-class `annotation`.
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import create_positional_parameter

create_positional_parameter("x", annotation=int, default=3)             # -> x: int = 3
create_positional_parameter("x", positional_only=True).kind             # -> <_ParameterKind.POSITIONAL_ONLY: 0>
create_positional_parameter("x", annotation=int, default="text")        # raises: INVALID DEFAULT VALUE — a default of type str for an annotation int
create_positional_parameter("x", annotation=int, default="text", _validate_call=False)   # -> x: int = 'text'      the check is skipped
```

**Why one function for both kinds.** The two positional kinds share everything but a flag, and
`positional_only=False` is the common case.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def create_positional_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    positional_only: bool = False,
    _validate_call: bool = True
) -> inspect.Parameter:
    # 1. A default that contradicts its annotation is refused (unless validation is off)
    if _validate_call:
        validate_default_matches_annotation(default, annotation)

    # 2. Resolve the parameter kind
    kind = (
        inspect.Parameter.POSITIONAL_ONLY
        if positional_only
        else inspect.Parameter.POSITIONAL_OR_KEYWORD
    )

    # 3. Build the parameter
    return inspect.Parameter(
        name = name,
        kind = kind,
        default = default,
        annotation = annotation,
    )
```

The default is checked by `validate_default_matches_annotation`, which is **deliberately light**: it judges only a
real default against a plain class annotation. `None`, `Any`, a missing annotation, unions, generics and strings are
not judged — judging `list[int]` or `int | None` means reimplementing a type checker, and a wrong "no" would block a
valid signature.

```python
def validate_default_matches_annotation(
    default_value: Any,
    annotation: Any,
) -> None:
    # 1. Skip validation if nothing to check or annotation not suitable
    if (
        default_value is inspect.Parameter.empty
        or default_value is None
        or annotation is inspect.Parameter.empty
        or annotation is Any
    ):
        return  # Nothing deterministic to validate

    if isinstance(annotation, type):
        if not isinstance(default_value, annotation):
            raise ParamError(
                error_name = "INVALID DEFAULT VALUE",
                label = "default for parameter",
                value = default_value,
                expected = f"value of type {annotation.__name__}",
                problem = f"The default value does not match its annotation {annotation.__name__!r}.",
                how_to_fix = (
                    f"Provide a default value of type {annotation.__name__}.",
                    "If unsure, remove the default or adjust the annotation.",
                ),
                exception = TypeError,
            )
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `create_keyword_parameter`

Creates a **keyword-only** parameter — one that can only be passed by name and stands after `*args` (or a bare
`*`) in a signature.

**Parameters:**

| Name             | Type   | Default | Description                                                              |
|------------------|--------|---------|--------------------------------------------------------------------------|
| `name`           | `str`  |         | The parameter name.                                                       |
| `annotation`     | `Any`  | *none*  | The annotation. *(keyword-only)*                                          |
| `default`        | `Any`  | *none*  | The default value; without it the parameter is required. *(keyword-only)* |
| `_validate_call` | `bool` | `True`  | Reserved switch of `@validate_call`; also gates the default check. *(keyword-only)* |

**Returns:** an `inspect.Parameter` of kind `KEYWORD_ONLY`.

**Raises:**
`ParamError` — `INVALID DEFAULT VALUE`: `default` does not fit a plain-class `annotation`.
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
from simplibs.signature import create_keyword_parameter

create_keyword_parameter("x")                                  # -> x
create_keyword_parameter("x", annotation=int, default=3)       # -> x: int = 3
create_keyword_parameter("x", annotation=int, default=None)    # -> x: int = None      None is always an acceptable default
create_keyword_parameter("x", annotation=int, default="text")  # raises: INVALID DEFAULT VALUE
```

**Why `_validate_call` is used twice.** It bypasses `@validate_call`'s own checks, and it also gates the
default/annotation check in the body, so one switch turns off every check of this function.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def create_keyword_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    _validate_call: bool = True
) -> inspect.Parameter:
    # 1. A default that contradicts its annotation is refused (unless validation is off)
    if _validate_call:
        validate_default_matches_annotation(default, annotation)

    # 2. Build the parameter
    return inspect.Parameter(
        name = name,
        kind = inspect.Parameter.KEYWORD_ONLY,
        default = default,
        annotation = annotation,
    )
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `ARGS` and `KWARGS`

Two **ready-made parameters**: a `*args` and a `**kwargs`. Building `inspect.Parameter(name="args",
kind=VAR_POSITIONAL, ...)` by hand takes four arguments for something that is always the same.

**Definition:**

| Constant | Is                                       |
|----------|------------------------------------------|
| `ARGS`   | `inspect.Parameter` named `args`, kind `VAR_POSITIONAL`   |
| `KWARGS` | `inspect.Parameter` named `kwargs`, kind `VAR_KEYWORD`    |

**Example usage:**

```python
import inspect
from simplibs.signature import ARGS, KWARGS, create_keyword_parameter, create_signature

str(ARGS)                                  # -> '*args'
str(KWARGS)                                # -> '**kwargs'
str(inspect.Signature([ARGS, KWARGS]))     # -> '(*args, **kwargs)'

create_signature(create_keyword_parameter("x"), KWARGS)       # -> (*, x, **kwargs)      an open-ended signature
```

**Why `KWARGS` matters more.** Flat mode merges every `**kwargs` it meets, under whatever name, into this one
parameter, so a flattened signature always ends in a plain `**kwargs`. The library itself never needs `ARGS` — flat
mode drops `*args` — it is exported as its counterpart, for callers who want an open-ended signature.

**Why sharing one instance is safe.** `inspect.Parameter` is immutable.

<details>
<summary>🔍 Under the hood</summary>

```python
ARGS: Final[inspect.Parameter] = inspect.Parameter(
    name="args",
    kind=inspect.Parameter.VAR_POSITIONAL,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty,
)

KWARGS: Final[inspect.Parameter] = inspect.Parameter(
    name="kwargs",
    kind=inspect.Parameter.VAR_KEYWORD,
    default=inspect.Parameter.empty,
    annotation=inspect.Parameter.empty,
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

## 🔬 Operations

The three basic operations on signatures: **read** one, **build** one, **attach** one.

[▲ Back to top](#-table-of-contents)

---

### `get_signature`

Reads the `inspect.Signature` of a callable — `inspect.signature` with a **readable failure**.

**Parameters:**

| Name             | Type       | Default | Description                                                     |
|------------------|------------|---------|-----------------------------------------------------------------|
| `function`       | `Callable` |         | A function, method, class or other callable.                     |
| `_validate_call` | `bool`     | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*            |

**Returns:** the signature of `function`.

**Raises:**
`ParamError` — `SIGNATURE INTROSPECTION ERROR`: the callable has no readable signature (also a `ValueError`), or
the object is not supported (also a `TypeError`).
`ValidationError` — `function` is not callable.

**Example usage:**

```python
from simplibs.signature import get_signature

def src(a, b=1, *args, k, **kwargs) -> str: ...

class Point:
    def __init__(self, x, y=0): ...

get_signature(src)                    # -> (a, b=1, *args, k, **kwargs) -> str
get_signature(Point)                  # -> (x, y=0)                        a class: the signature of its constructor
get_signature(Point(1).__init__)      # -> (x, y=0)                        a bound method: without self
```

**Why it exists.** `inspect.signature` raises a bare `ValueError` for built-ins such as `len` and a bare
`TypeError` for objects that are not callables. Neither says which argument was wrong. This wrapper turns them into
a card that names the object and suggests a way out; the original type stays in the card's MRO, so
`except ValueError` keeps working.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def get_signature(
    function: Callable,
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Introspect
    try:
        return inspect.signature(function)

    # 2. Handle callables lacking signature metadata
    except ValueError as e:
        raise_signature_introspection_value_error(function, e)

    # 3. Handle objects that cannot be introspected as callables
    except TypeError as e:
        raise_signature_introspection_type_error(function, e)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `compose_signature`

Builds an `inspect.Signature` from parameters and a return annotation — **the one place** where every
operation of the library ends in a signature.

**Parameters:**

| Name                | Type                          | Default       | Description                                                  |
|---------------------|-------------------------------|---------------|--------------------------------------------------------------|
| `parameters`        | `Iterable[inspect.Parameter]` |               | The parameters, in the order they are to appear. Any iterable, also a generator.              |
| `return_annotation` | `Any`                         | *none*        | The return annotation. `None` is a real annotation.           |
| `_validate_call`    | `bool`                        | `True`        | Reserved switch of `@validate_call`. *(keyword-only)*         |

**Returns:** the new `inspect.Signature`.

**Raises:**
`ParamError` — `SIGNATURE COMPOSITION ERROR`: the parameters do not form a valid signature (also a `ValueError`:
wrong order, duplicate name), an item is not a parameter (also an `AttributeError`), or the input is not an
iterable (also a `TypeError`).

**Example usage:**

```python
import inspect
from simplibs.signature import compose_signature

P = inspect.Parameter

compose_signature([P("a", P.POSITIONAL_OR_KEYWORD), P("b", P.POSITIONAL_OR_KEYWORD, default=1)], int)   # -> (a, b=1) -> int
compose_signature([])                                                                                    # -> ()
compose_signature(P(n, P.KEYWORD_ONLY) for n in "xy")                                                    # -> (*, x, y)      a generator is fine

compose_signature([P("a", P.POSITIONAL_OR_KEYWORD, default=1), P("b", P.POSITIONAL_OR_KEYWORD)])
                                                  # raises: SIGNATURE COMPOSITION ERROR — non-default argument follows default argument
```

**Why it is always validated.** Skipping the checks would need `inspect.Signature(...,
__validate_parameters__=False)`, an undocumented CPython argument. It would save a loop over a handful of
parameters and cost a lot: a duplicate name would be merged silently and the error branches would never run.
`_validate_call` therefore only controls `@validate_call`; the structure is checked every time.

**Why the parameters are read once.** `parameters` may be a generator. The first pass would empty it, and the
error would then show an empty collection instead of the parameters that failed. They are read into a tuple first
and that tuple serves both the signature and the message. `@validate_call(materialize_iterators=True)` already
turns a generator into a tuple before the function starts; the explicit `tuple(...)` keeps the function correct
with `_validate_call=False`, where nothing is converted.

**What it does not catch.** `(*a, *b)` — plain `inspect` accepts two variadics of one kind. The
[collector](README_SIGNATURE_PARAMETER_COLLECTOR.md#one-args-one-kwargs) prevents that before this function is
reached.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def compose_signature(
    parameters: Iterable[inspect.Parameter],
    return_annotation: Any = inspect.Signature.empty,
    *,
    _validate_call: bool = True,
) -> inspect.Signature:
    # 1. Read the parameters once: a generator would be empty for the error message
    try:
        params = tuple(parameters)
    except TypeError as e:
        raise_signature_composition_type_error(parameters, e)

    # 2. Signature composition (inspect validates the structure)
    try:
        return inspect.Signature(
            parameters=params,
            return_annotation=return_annotation,
        )

    # 3. Handle structural issues
    except ValueError as e:
        raise_signature_composition_value_error(params, e)

    # 4. Handle duck-typing failures
    except AttributeError as e:
        raise_signature_composition_attribute_error(params, e)

    # 5. Handle invalid types in the parameters or annotations
    except TypeError as e:
        raise_signature_composition_type_error(params, e)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `set_signature`

Attaches a signature to a function through `__signature__` — the only function here that **changes the object
it is given**.

**Parameters:**

| Name             | Type                | Default | Description                                                  |
|------------------|---------------------|---------|--------------------------------------------------------------|
| `function`       | `Callable`          |         | The function to change.                                       |
| `signature`      | `inspect.Signature` |         | The signature to attach.                                      |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*         |

**Returns:** the **same** `function`, now reporting `signature` to `inspect`.

**Example usage:**

```python
import inspect
from simplibs.signature import set_signature

function = lambda: None
set_signature(function, inspect.Signature([inspect.Parameter("only", inspect.Parameter.KEYWORD_ONLY)]))

str(inspect.signature(function))     # -> '(*, only)'
function()                           # still works — only what inspect reports has changed
```

**Why it exists beside the decorators.** `inspect.signature` looks at `__signature__` first, so assigning it changes
what tools, editors and documentation generators see while the code stays as it is. Where a *separate* callable is
wanted, use [`signature_set`](README_SIGNATURE_DECORATORS.md#signature_set), which wraps instead.

**Not checked further.** The signature is not compared with what the function really accepts. That is the caller's
responsibility; this function only attaches.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def set_signature(
    function: Callable,
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    # 1. Assign signature to function
    function.__signature__ = signature

    # 2. Return the modified function
    return function
```

</details>

[▲ Back to top](#-table-of-contents)

---

## 🩹 Modifiers

Take a signature, return a **changed copy**: add parameters, delete parameters, replace the return annotation.
The original is never touched.

[▲ Back to top](#-table-of-contents)

---

### `add_params_to_signature`

Creates a new signature by **adding parameters** to an existing one; the result is always in a valid order,
whatever the order of the input.

**Parameters:**

| Name             | Type                          | Default | Description                                                          |
|------------------|-------------------------------|---------|----------------------------------------------------------------------|
| `signature`      | `inspect.Signature`           |         | The signature to start from.                                          |
| `params_to_add`  | `Iterable[inspect.Parameter]` |         | The parameters to add. Any iterable, also a generator.                 |
| `accept_double`  | `bool`                        | `True`  | If `False`, a collision raises. *(keyword-only)*                       |
| `replace_double` | `bool`                        | `True`  | The later parameter — here a new one — wins a collision. *(keyword-only)* |
| `flat_to_kwargs` | `bool`                        | `False` | Flat mode: everything keyword-only. *(keyword-only)*                   |
| `_validate_call` | `bool`                        | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                  |

**Returns:** a new `inspect.Signature` with the merged parameters; the return annotation is kept.

**Raises:**
`ParamError` — `DUPLICATE PARAMETER ERROR` (a collision with `accept_double=False`), `INVALID PARAMETER ORDER`,
`SIGNATURE STRUCTURE ERROR` and `SIGNATURE TYPE ERROR` (safety nets: the collector normally prevents them).
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import add_params_to_signature, create_keyword_parameter, create_positional_parameter

def src(a, b=1, *args, k, **kwargs) -> str: ...
sig = inspect.signature(src)

add_params_to_signature(sig, [create_keyword_parameter("extra", default=2)])
                                                   # -> (a, b=1, *args, k, extra=2, **kwargs) -> str       added in its place
add_params_to_signature(sig, [create_positional_parameter("b", default=99)])
                                                   # -> (a, b=99, *args, k, **kwargs) -> str               the new b replaced the old
add_params_to_signature(sig, [create_positional_parameter("b", default=99)], replace_double=False)
                                                   # -> (a, b=1, *args, k, **kwargs) -> str                the old b stays
add_params_to_signature(sig, [create_keyword_parameter("extra")], flat_to_kwargs=True)
                                                   # -> (*, a, b=1, k, extra, **kwargs) -> str
```

**Why only three options.** `include_variadic` and `include_binding` are not offered: the signature is taken as
it is, and nothing is meant to disappear from it.

**Why the new parameters are read once.** `params_to_add` may be a generator. It is read into a tuple first, so the
collector and the error message see the same parameters. `@validate_call(materialize_iterators=True)` already
turns a generator into a tuple before the function starts; the explicit `tuple(...)` keeps the function correct
with `_validate_call=False`, where nothing is converted.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def add_params_to_signature(
    signature: inspect.Signature,
    params_to_add: Iterable[inspect.Parameter],
    *,
    accept_double: bool = True,
    replace_double: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Read the new parameters once: a generator would be empty for the error message
    params_to_add = tuple(params_to_add)

    # 2. Initialize collector with duplicate handling rules
    param_collector = ParameterCollector(
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        _validate_call=False,  # Parameters already validated or trusted
    )

    # 3. Load existing signature parameters into the collector
    param_collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 4. Add new parameters to the collector
    param_collector.add_params(
        params=params_to_add,
        _validate_call=False
    )

    # 5. Get ordered parameters
    ordered_params = param_collector.get_ordered_params()

    # 6. Construct the new signature from ordered parameters
    try:
        return signature.replace(
            parameters=ordered_params
        )

    # 7. Handle structural issues
    except ValueError as e:
        raise_signature_structure_value_error(params_to_add, e)

    # 8. Handle type mismatches during replacement
    except TypeError as e:
        raise_signature_type_error(ordered_params, e)
```

The existing parameters go into the collector first and the new ones second — which is why a new parameter wins a
collision by default. The two `except` branches stay for the cases nobody foresaw: the collector already refuses
duplicates and a wrong order, so `inspect` rarely has anything left to object to.

</details>

[▲ Back to top](#-table-of-contents)

---

### `delete_params_from_signature`

Creates a new signature **without the named parameters**.

**Parameters:**

| Name             | Type                | Default | Description                                                  |
|------------------|---------------------|---------|--------------------------------------------------------------|
| `signature`      | `inspect.Signature` |         | The signature to start from.                                  |
| `excluded_names` | `Iterable[str]`     |         | The names of the parameters to remove. Any iterable, also a generator. Names that are not in the signature are ignored. |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*         |

**Returns:** a new `inspect.Signature` without the excluded parameters; the return annotation is kept.

**Example usage:**

```python
import inspect
from simplibs.signature import delete_params_from_signature

sig = inspect.signature(src)       # (a, b=1, *args, k, **kwargs) -> str

delete_params_from_signature(sig, ["a", "kwargs", "missing"])     # -> (b=1, *args, k) -> str      "missing" is simply ignored
delete_params_from_signature(sig, ["args", "kwargs"])             # -> (a, b=1, *, k) -> str       variadics go by name here
delete_params_from_signature(sig, (n for n in ["a"]))             # -> (b=1, *args, k, **kwargs) -> str
```

**Why unknown names are fine.** Excluding a name that is not there does nothing: a delete that has nothing to
delete is already in the state the caller asked for.

**Why no order error is possible.** Removing a parameter can never break the order, so the result is valid
whatever is removed.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def delete_params_from_signature(
    signature: inspect.Signature,
    excluded_names: Iterable[str],
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Initialize collector with exclusion rules
    collector = ParameterCollector(
        excluded_names=excluded_names,
        _validate_call=False,
    )

    # 2. Load signature parameters into the collector
    collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 3. Retrieve the filtered and ordered parameters
    new_params = collector.get_ordered_params()

    # 4. Construct and return the new signature
    return signature.replace(
        parameters=new_params
    )
```

Deleting is "load the signature into a collector that already excludes these names".

</details>

[▲ Back to top](#-table-of-contents)

---

### `replace_return_annotation_in_signature`

Creates a new signature with **another return annotation** — the counterpart of the two functions above for the
one part of a signature that is not a parameter.

**Parameters:**

| Name                    | Type                | Default | Description                                                              |
|-------------------------|---------------------|---------|--------------------------------------------------------------------------|
| `signature`             | `inspect.Signature` |         | The signature to start from.                                              |
| `new_return_annotation` | `Any`               |         | The new annotation: a type, a string, `None`, or `inspect.Signature.empty` to remove it. |
| `_validate_call`        | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                     |

**Returns:** a new `inspect.Signature` with the same parameters.

**Example usage:**

```python
import inspect
from simplibs.signature import replace_return_annotation_in_signature

sig = inspect.signature(src)       # (a, b=1, *args, k, **kwargs) -> str

replace_return_annotation_in_signature(sig, int)                        # -> (a, b=1, *args, k, **kwargs) -> int
replace_return_annotation_in_signature(sig, None)                       # -> (a, b=1, *args, k, **kwargs) -> None      None is a real annotation
replace_return_annotation_in_signature(sig, inspect.Signature.empty)    # -> (a, b=1, *args, k, **kwargs)              removed
```

**Why it is not interpreted.** The value is used as it is. `None` means "returns nothing";
`inspect.Signature.empty` is the way to say "no annotation".

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def replace_return_annotation_in_signature(
    signature: inspect.Signature,
    new_return_annotation: Any,
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Same parameters, new return annotation
    return signature.replace(
        return_annotation=new_return_annotation
    )
```

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

These functions raise `ParamError` cards of [`simplibs-exception`](https://pypi.org/project/simplibs-exception/);
the package defines no exceptions of its own. The card's `label` names the offending part and its `value` is what
was given.

| Error name                      | Wraps                                       | Raised by                                           | Fix                                                                     |
|---------------------------------|---------------------------------------------|-----------------------------------------------------|-------------------------------------------------------------------------|
| `INVALID DEFAULT VALUE`         | `TypeError`                                 | `create_positional_parameter`, `create_keyword_parameter` | Give a default of the annotated type, or adjust the annotation     |
| `SIGNATURE INTROSPECTION ERROR` | `ValueError`, `TypeError`                   | `get_signature`                                     | Use a Python function or a callable with a readable signature            |
| `SIGNATURE COMPOSITION ERROR`   | `ValueError`, `AttributeError`, `TypeError` | `compose_signature`                                 | Pass unique `inspect.Parameter` objects in a valid order                  |
| `DUPLICATE PARAMETER ERROR`     | `ValueError`                                | `add_params_to_signature`                           | Make the names unique, or use `accept_double=True`                        |
| `INVALID PARAMETER ORDER`       | `SyntaxError`                               | `add_params_to_signature`                           | Add required parameters before optional ones                              |
| `SIGNATURE STRUCTURE ERROR`     | `ValueError`                                | `add_params_to_signature`                           | Check the combination of the existing and the new parameters              |
| `SIGNATURE TYPE ERROR`          | `TypeError`                                 | `add_params_to_signature`                           | Make sure every item is an `inspect.Parameter`                            |

An argument of the wrong type is a `ValidationError` from `@validate_call` and never reaches these.

[▲ Back to top](#-table-of-contents)
