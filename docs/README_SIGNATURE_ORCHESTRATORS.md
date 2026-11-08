# 🎼 `orchestrators` — Build a Whole Signature in One Call

The `orchestrators` package holds the two **high-level builders**. They combine the
[collector](README_SIGNATURE_PARAMETER_COLLECTOR.md) with the [tools](README_SIGNATURE_TOOLS.md) into one call:
load the parameters, settle the return annotation, compose and validate the result. Everything the
[decorators](README_SIGNATURE_DECORATORS.md) do is built on them, and they are useful on their own whenever
you want the signature as an **object** rather than attached to a function.

```python
from simplibs.signature import create_signature, copy_signature
```

| Function           | Starts from …                                         | Typical use                                           |
|--------------------|-------------------------------------------------------|-------------------------------------------------------|
| `create_signature` | **any number** of parameters and callables             | merge, assemble, build from scratch                    |
| `copy_signature`   | **one** callable, plus changes                         | "the same arguments, with a few more or fewer"         |

```python
import inspect
from simplibs.signature import create_signature, copy_signature

def f(a, *args, b=1): ...
def g(c, *rest): ...

create_signature(f, g)                                     # -> (a, c, *rest, b=1)
copy_signature(g, extra_params=[inspect.Parameter("z", inspect.Parameter.KEYWORD_ONLY)])    # -> (c, *rest, z)
```

Both return an `inspect.Signature`; neither touches the functions it reads from.

## A note on order and priority

Sources are loaded **in the order given**, and a parameter that meets one with the same name is a
collision. With the default `replace_double=True` the **later** parameter wins, so the order of your
arguments is the priority. In `copy_signature` the original parameters come first and `extra_params` second,
so with the defaults the extras win.

```python
create_signature(f, g)                          # -> (a, c, *rest, b=1)     g came later: its *rest replaced *args
create_signature(f, g, replace_double=False)    # -> (a, c, *args, b=1)     the earlier one stays
create_signature(f, g, accept_double=False)     # raises: DUPLICATE PARAMETER ERROR
```

## A note on the order of the result

You never place a parameter. Whatever order the sources come in, the result is in the order Python
requires: positional-only, ordinary, `*args`, keyword-only, `**kwargs` — and required before optional inside
a kind.

```python
create_signature(
    inspect.Parameter("k", inspect.Parameter.KEYWORD_ONLY),
    inspect.Parameter("kw", inspect.Parameter.VAR_KEYWORD),
    inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD),
)                                               # -> (a, *, k, **kw)
```

The one thing a collector cannot reorder is a **required positional parameter after an optional one**
(`def f(a=1, b)`): moving it would change the meaning of a call, so it is refused with an
`INVALID PARAMETER ORDER` card instead.

## A note on variadics

A signature holds one `*args` and one `**kwargs`. The collector treats a second one as a collision even
under a different name, and settles it by the same rules as any duplicate: the later one replaces the earlier
(default), the earlier one stays (`replace_double=False`) or it is an error (`accept_double=False`). Plain
`inspect` accepts `(*a, *b)` without a word, so this is checked here.

## A note on return annotations

`create_signature` takes a `return_source`, which is resolved like this:

| `return_source`                          | Return annotation of the result              |
|------------------------------------------|----------------------------------------------|
| not given (`UNSET`)                      | none                                         |
| `None`                                   | `None` — a real annotation (returns nothing) |
| a class, `list[int]`, `int \| None`, `"str"` | exactly that                             |
| a plain function                         | **that function's** return annotation        |

A class is callable too, and so are generics like `list[int]`, yet they are annotations — only a plain
function (callable, not a class, no `__origin__`) is taken as "a function to copy from".
`copy_signature` has no such rule: the function being copied is already the source, so `return_annotation`
is the annotation itself, and `UNSET` keeps the original one.

---

## 🧭 Table of Contents

* [`create_signature`](#create_signature)
* [`copy_signature`](#copy_signature)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-orchestrators--build-a-whole-signature-in-one-call)

---

### `create_signature`

Creates a signature from **any mix of parameters and callables**. The sources are merged in the order given
and the result is always in a valid order.

**Parameters:**

| Name               | Type                            | Default | Description                                                                 |
|--------------------|---------------------------------|---------|-----------------------------------------------------------------------------|
| `*param_sources`   | `inspect.Parameter \| Callable` |         | Parameters and callables, in the order they are loaded. A callable contributes all of its parameters. |
| `return_source`    | `Any`                           | `UNSET` | `UNSET` for no annotation, a plain function to copy it from, or the annotation itself. *(keyword-only)* |
| `excluded_names`   | `Iterable[str]`                 | `()`    | Names of parameters to leave out. Any iterable, also a generator. *(keyword-only)*                           |
| `accept_double`    | `bool`                          | `True`  | If `False`, a collision is an error. *(keyword-only)*                        |
| `replace_double`   | `bool`                          | `True`  | The later parameter wins a collision. *(keyword-only)*                       |
| `include_variadic` | `bool`                          | `True`  | If `False`, every `*args` and `**kwargs` is left out. *(keyword-only)*       |
| `include_binding`  | `bool`                          | `True`  | If `False`, `self` and `cls` are left out. *(keyword-only)*                  |
| `flat_to_kwargs`   | `bool`                          | `False` | Everything keyword-only. *(keyword-only)*                                     |
| `_validate_call`   | `bool`                          | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                         |

**Returns:** a new `inspect.Signature`.

**Raises:**
`ParamError` — `INVALID PARAMETER SOURCE` (a source is neither a parameter nor a callable),
`DUPLICATE PARAMETER ERROR`, `INVALID PARAMETER ORDER`, `SIGNATURE INTROSPECTION ERROR` (a callable's signature
cannot be read).
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import create_signature, create_keyword_parameter

def f(a, *args, b=1): ...
def g(c, *rest): ...
def typed() -> str: ...

create_signature()                                         # -> ()
create_signature(f)                                        # -> (a, *args, b=1)
create_signature(f, g)                                     # -> (a, c, *rest, b=1)
create_signature(f, g, include_variadic=False)             # -> (a, c, *, b=1)
create_signature(f, g, excluded_names=["a", "c"])          # -> (*rest, b=1)
create_signature(f, g, flat_to_kwargs=True)                # -> (*, a, b=1, c)
create_signature(f, return_source=typed)                   # -> (a, *args, b=1) -> str
create_signature(f, return_source=list[int])               # -> (a, *args, b=1) -> list[int]
create_signature(f, create_keyword_parameter("x"))         # -> (a, *args, x, b=1)      a required keyword-only goes before the optional ones

create_signature(f, g, accept_double=False)                # raises: DUPLICATE PARAMETER ERROR — 'rest' collides with the already defined variadic positional parameter 'args'
create_signature(
    inspect.Parameter("opt", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1),
    inspect.Parameter("req", inspect.Parameter.POSITIONAL_OR_KEYWORD),
)                                                          # raises: INVALID PARAMETER ORDER — 'req' (no default value) cannot follow parameters that already have default values
```

**Why one function for everything.** `copy_signature`, the decorators and the modifiers are all special cases
of "load some parameters, settle a few options, compose". Keeping that in one place means one set of rules
and one set of errors.

**Why it trusts its own calls.** The arguments are validated once, by this function's own `@validate_call`.
Every inner call passes `_validate_call=False`; validating the same values again at every level would only
repeat the work.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def create_signature(
    *param_sources: inspect.Parameter | Callable,
    return_source: Any = UNSET,
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Prepare the collector
    collector = ParameterCollector(
        excluded_names = excluded_names,
        accept_double = accept_double,
        replace_double = replace_double,
        include_variadic = include_variadic,
        include_binding = include_binding,
        flat_to_kwargs = flat_to_kwargs,
        _validate_call = False
    )

    # 2. Load parameters from all sources
    load_param_sources(
        collector=collector,
        param_sources=param_sources,
        _validate_call=False
    )

    # 3. Resolve the return annotation
    return_annotation = resolve_return_annotation(
        return_source=return_source,
        _validate_call=False
    )

    # 4. Compose the final signature
    return compose_signature(
        parameters = collector.get_ordered_params(),
        return_annotation = return_annotation,
        _validate_call = False
    )
```

The four steps are the four helpers. The two that belong to this package:

```python
@validate_call
def load_param_sources(
    collector: ParameterCollector,
    param_sources: tuple[inspect.Parameter | Callable, ...],
    *,
    _validate_call: bool = True
) -> None:
    for index, item in enumerate(param_sources):

        # 1. A Parameter goes straight into the collector
        if isinstance(item, inspect.Parameter):
            collector.add_param(
                param=item,
                _validate_call=False
            )

        # 2. A callable contributes all of its parameters
        elif callable(item):
            signature = get_signature(
                function=item,
                _validate_call=False
            )
            collector.add_params(
                params=signature.parameters.values(),
                _validate_call=False
            )

        # 3. Anything else is an invalid source
        else:
            raise_invalid_parameter_source_error(index, item)
```

A `Parameter` is checked first and a callable second — an `inspect.Parameter` is not callable, but the order
makes that independent of any future change. Anything else is an error naming the **position** of the
offender.

```python
@validate_call
def resolve_return_annotation(
    return_source: Any,
    *,
    _validate_call: bool = True
) -> Any:
    # 1. No source given
    if return_source is UNSET:
        return inspect.Signature.empty

    # 2. A plain callable (not a class, not a typing construct): take its return annotation
    if (
        callable(return_source)
        and not isclass(return_source)
        and not hasattr(return_source, "__origin__")
    ):
        return get_signature(
            function=return_source,
            _validate_call=False
        ).return_annotation

    # 3. A direct annotation (type, None, string, Union...)
    return return_source
```

`UNSET` and `None` are two different things: `None` is a valid annotation (a function that returns nothing),
so "not given" needs a marker of its own.

</details>

[▲ Back to top](#-table-of-contents)

---

### `copy_signature`

Creates a **changed copy** of one callable's signature: parameters can be removed, added or replaced, and the
return annotation changed, in one operation. The original is not touched.

**Parameters:**

| Name               | Type                          | Default | Description                                                                 |
|--------------------|-------------------------------|---------|-----------------------------------------------------------------------------|
| `function`         | `Callable`                    |         | The callable to copy the signature from.                                     |
| `return_annotation`| `Any`                         | `UNSET` | The new return annotation. `UNSET` keeps the original; `None` is a real annotation. *(keyword-only)* |
| `extra_params`     | `Iterable[inspect.Parameter]` | `()`    | Parameters to add after the copied ones. Any iterable, also a generator. *(keyword-only)*                    |
| `excluded_names`   | `Iterable[str]`               | `()`    | Names of parameters to leave out. Any iterable, also a generator. *(keyword-only)*                           |
| `accept_double`    | `bool`                        | `True`  | If `False`, a collision is an error. *(keyword-only)*                        |
| `replace_double`   | `bool`                        | `True`  | The later parameter — here an extra — wins a collision. *(keyword-only)*     |
| `include_variadic` | `bool`                        | `True`  | If `False`, every `*args` and `**kwargs` is left out. *(keyword-only)*       |
| `include_binding`  | `bool`                        | `True`  | If `False`, `self` and `cls` are left out. *(keyword-only)*                  |
| `flat_to_kwargs`   | `bool`                        | `False` | Everything keyword-only. *(keyword-only)*                                     |
| `_validate_call`   | `bool`                        | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                         |

**Returns:** a new `inspect.Signature`.

**Raises:**
`ParamError` — `SIGNATURE INTROSPECTION ERROR` (the signature of `function` cannot be read),
`DUPLICATE PARAMETER ERROR`, `INVALID PARAMETER ORDER`.
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import copy_signature, create_keyword_parameter, create_positional_parameter

def src(a, b=1, *args, k, **kwargs) -> str: ...

copy_signature(src)                                            # -> (a, b=1, *args, k, **kwargs) -> str
copy_signature(src, return_annotation=int)                     # -> (a, b=1, *args, k, **kwargs) -> int
copy_signature(src, return_annotation=None)                    # -> (a, b=1, *args, k, **kwargs) -> None
copy_signature(src, extra_params=[create_keyword_parameter("extra")], excluded_names=["a"])
                                                               # -> (b=1, *args, k, extra, **kwargs) -> str
copy_signature(src, extra_params=[create_positional_parameter("b", default=99)])
                                                               # -> (a, b=99, *args, k, **kwargs) -> str      the extra replaced b
copy_signature(src, extra_params=[create_positional_parameter("b", default=99)], replace_double=False)
                                                               # -> (a, b=1, *args, k, **kwargs) -> str       the original stays
```

**Why `return_annotation` is the annotation itself.** Unlike `create_signature(return_source=...)` it takes
no function to copy from: the source function is already the one being copied. `UNSET` keeps its own
annotation, so `None` can still be requested.

**Why the extras come second.** The original is the base, the extras are changes. With the defaults a change
overrides what it meets — the same "later wins" rule as everywhere else.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def copy_signature(
    function: Callable,
    *,
    return_annotation: Any = UNSET,
    extra_params: Iterable[inspect.Parameter] = (),
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    # 1. Get base signature from the function
    signature = get_signature(
        function=function,
        _validate_call=False
    )

    # 2. Initialize parameter collector with configuration
    param_collector = ParameterCollector(
        excluded_names=excluded_names,
        include_variadic=include_variadic,
        include_binding=include_binding,
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        _validate_call=False
    )

    # 3. Load original signature parameters into the collector
    param_collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 4. Add extra parameters to the collector
    param_collector.add_params(
        params=extra_params,
        _validate_call=False
    )

    # 5. Determine final return annotation
    final_return = (
        return_annotation
        if return_annotation is not UNSET
        else signature.return_annotation
    )

    # 6. Compose the final signature
    return compose_signature(
        parameters=param_collector.get_ordered_params(),
        return_annotation=final_return,
        _validate_call=False
    )
```

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

These functions raise `ParamError` cards of [`simplibs-exception`](https://pypi.org/project/simplibs-exception/)
(most of them from the collector and the tools they call); the package defines no exceptions of its own. The
card's `label` names the offending part and its `value` is what was given.

| Error name                      | Wraps                     | Raised by                              | Fix                                                                         |
|---------------------------------|---------------------------|----------------------------------------|-----------------------------------------------------------------------------|
| `INVALID PARAMETER SOURCE`      | `TypeError`               | `create_signature`                     | Pass `inspect.Parameter` objects or callables only; unpack a list with `*`   |
| `DUPLICATE PARAMETER ERROR`     | `ValueError`              | `create_signature`, `copy_signature`   | Make the names unique (also: one `*args` and one `**kwargs`), or use `accept_double=True` |
| `INVALID PARAMETER ORDER`       | `SyntaxError`             | `create_signature`, `copy_signature`   | Put required parameters before optional ones                                 |
| `SIGNATURE INTROSPECTION ERROR` | `ValueError`, `TypeError` | `create_signature`, `copy_signature`   | Use a Python function or a callable with a readable signature                |

An argument of the wrong type is a `ValidationError` from `@validate_call` and never reaches these.

[▲ Back to top](#-table-of-contents)
