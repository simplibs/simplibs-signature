# 🎀 `decorators` — Give a Wrapper Its Real Signature

The `decorators` package holds three decorators and the two builders they are made of. A decorator that
wraps a function usually looks like `(*args, **kwargs)` from the outside; these give the wrapper the
signature the **caller** really sees — so an editor completes the right arguments, `help()` shows the
right call, and documentation generators describe the right parameters.

```python
from simplibs.signature import signature, signature_copy, signature_set
from simplibs.signature import apply_signature_to_wraps, create_signature_decorator
```

The three decorators differ only in **where the signature comes from**:

| Decorator        | The signature comes from …                                           | Built …                          |
|------------------|----------------------------------------------------------------------|----------------------------------|
| `signature`      | the decorated function **and** any parameters or functions you list  | when the decorator is **applied** |
| `signature_copy` | another callable (`base_func`), with changes                         | when the decorator is **created** |
| `signature_set`  | a finished `inspect.Signature` you already have                      | before — you made it              |

```python
import inspect

def original(a: int, b: str = "x", *args, **kwargs) -> bool: ...

@signature_copy(original, excepts=["b"])
def wrapper(*args, **kwargs):
    return original(*args, **kwargs)

str(inspect.signature(wrapper))     # -> '(a: int, *args, **kwargs) -> bool'
wrapper(1, "y")                     # the call goes through unchanged
```

## A note on what the wrapper is

Every decorator returns a **new function** made by `apply_signature_to_wraps`; the function you decorate is
not modified.

* The wrapper has the metadata of the original (`__name__`, `__doc__`, `__wrapped__` — through
  `functools.wraps`) and passes every call through **unchanged**: the signature *describes* the call, it
  does not enforce it.
* A coroutine function gets an `async` wrapper, so `inspect.iscoroutinefunction(wrapper)` stays `True` and
  `await wrapper(...)` keeps working. A plain wrapper would silently return a coroutine object.
* `inspect.signature` normally follows `__wrapped__` back to the original. It stops at an object that has
  `__signature__`, so the assigned signature is the one reported.

## A note on when the signature is built

`signature` needs the decorated function (it is one of the sources), so it builds the signature when the
decorator is **applied**; an invalid source is reported there. `signature_copy` and `signature_set` already
know everything when the decorator is **created**, so the signature is built **once** and shared by every
function the decorator is applied to — and a mistake is reported at once, before any function is decorated.

```python
decorator = signature_copy(original)       # the signature is built here, once
first = decorator(lambda *a, **k: 1)       # ...and shared
second = decorator(lambda *a, **k: 2)
```

## A note on collisions in `signature`

With `use_func=True` (the default) the decorated function is one of the sources, and **position is
priority**: with the default `replace_double=True` the later source wins a collision.

| `func_first` | Order of the sources            | A collision is won by … |
|--------------|---------------------------------|-------------------------|
| `True` (default) | the function, then `*params` | `*params`               |
| `False`      | `*params`, then the function    | the function            |

```python
@signature(inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=2))
def f(a=1): ...
str(inspect.signature(f))      # -> '(a=2)'      the parameter listed in the decorator won
```

Write `@signature()` — with parentheses — to apply it with no extra sources; a bare `@signature` would hand
the decorated function to the factory as its first **source**.

---

## 🧭 Table of Contents

* [`signature`](#signature)
* [`signature_copy`](#signature_copy)
* [`signature_set`](#signature_set)
* [`create_signature_decorator`](#create_signature_decorator)
* [`apply_signature_to_wraps`](#apply_signature_to_wraps)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../__DOC__/README.md#-decorators--give-a-wrapper-its-real-signature)

---

### `signature`

Decorator factory that **assembles** the signature of a function from several sources — by default the
function itself plus the parameters and callables you list.

**Parameters:**

| Name               | Type                              | Default | Description                                                                 |
|--------------------|-----------------------------------|---------|-----------------------------------------------------------------------------|
| `*params`          | `inspect.Parameter \| Callable`   |         | Extra parameters, or callables whose parameters are all taken.               |
| `returns`          | `Any`                             | `UNSET` | The return annotation: `UNSET` for none, a plain callable to copy it from, or the annotation itself. *(keyword-only)* |
| `excepts`          | `Iterable[str]`                   | `()`    | Names of parameters to leave out. Any iterable, also a generator. *(keyword-only)*                            |
| `use_func`         | `bool`                            | `True`  | Whether the decorated function's own parameters are a source. *(keyword-only)* |
| `func_first`       | `bool`                            | `True`  | Put the function before `*params` (so `*params` win collisions). *(keyword-only)* |
| `accept_double`    | `bool`                            | `True`  | If `False`, a collision is an error. *(keyword-only)*                          |
| `replace_double`   | `bool`                            | `True`  | The later parameter wins a collision. *(keyword-only)*                         |
| `include_variadic` | `bool`                            | `True`  | If `False`, every `*args` and `**kwargs` is left out. *(keyword-only)*         |
| `include_binding`  | `bool`                            | `True`  | If `False`, `self` and `cls` are left out. *(keyword-only)*                    |
| `flat_to_kwargs`   | `bool`                            | `False` | Everything keyword-only. *(keyword-only)*                                       |
| `_validate_call`   | `bool`                            | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                           |

**Returns:** a decorator; applied to a function, it returns a wrapper that reports the assembled signature.

**Raises:**
`ParamError` — when the decorator is **applied**: `INVALID PARAMETER SOURCE`, `DUPLICATE PARAMETER ERROR`,
`INVALID PARAMETER ORDER`, `SIGNATURE INTROSPECTION ERROR`.
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import signature, create_keyword_parameter

@signature(inspect.Parameter("extra", inspect.Parameter.KEYWORD_ONLY))
def d1(a, *args, **kwargs): ...
str(inspect.signature(d1))              # -> '(a, *args, extra, **kwargs)'      added in its place, the order stays valid

@signature(create_keyword_parameter("only"), use_func=False)
def d2(a, b): ...
str(inspect.signature(d2))              # -> '(*, only)'                        the function itself is ignored

def typed() -> str: ...

@signature(returns=typed)
def d3(): ...
str(inspect.signature(d3))              # -> '() -> str'                        a callable gives its return annotation

@signature(excepts=["b"], include_variadic=False)
def d4(a, b, *args, **kw): ...
str(inspect.signature(d4))              # -> '(a)'

@signature(flat_to_kwargs=True)
def d5(a, b=1, *args, **kw): ...
str(inspect.signature(d5))              # -> '(*, a, b=1, **kwargs)'            *args dropped, **kw became **kwargs
```

**Why the sources are built inside the decorator.** The decorated function is one of the sources, and it is
only known when the decorator is applied — so `create_signature` runs there, not in the factory.

**Why `_validate_call=False` inside.** The factory's own arguments are validated once by `@validate_call`;
the inner calls trust them instead of validating the same values again at every level.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def signature(
    *params: inspect.Parameter | Callable,
    returns: Any = UNSET,
    excepts: Iterable[str] = (),
    use_func: bool = True,
    func_first: bool = True,
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> Callable:
    # 1. Define the decorator
    def decorator(function: Callable) -> Callable:

        # 2. The function is one of the sources: before `params` or behind them
        param_sources = params
        if use_func:
            param_sources = (
                (function,) + param_sources if func_first
                else param_sources + (function,)
            )

        # 3. Assemble the signature from all sources
        new_signature = create_signature(
            *param_sources,
            return_source = returns,
            excluded_names = tuple(excepts),
            accept_double = accept_double,
            replace_double = replace_double,
            include_variadic = include_variadic,
            include_binding = include_binding,
            flat_to_kwargs = flat_to_kwargs,
            _validate_call = False
        )

        # 4. Wrap the function and apply the assembled signature
        return apply_signature_to_wraps(
            function = function,
            signature = new_signature,
            _validate_call = False
        )

    # 5. Return the decorator
    return decorator
```

Step 2 is the whole "where does the function go" logic: in front of `params` with `func_first=True`, behind
them otherwise. Everything else is the shared machinery of [`create_signature`](README_SIGNATURE_ORCHESTRATORS.md#create_signature).

</details>

[▲ Back to top](#-table-of-contents)

---

### `signature_copy`

Decorator factory that gives a function a **changed copy of another callable's signature** — the decorator
form of [`copy_signature`](README_SIGNATURE_ORCHESTRATORS.md#copy_signature), with shorter names.

**Parameters:**

| Name               | Type                         | Default | Description                                                                |
|--------------------|------------------------------|---------|----------------------------------------------------------------------------|
| `base_func`        | `Callable`                   |         | The callable to copy the signature from.                                    |
| `returns`          | `Any`                        | `UNSET` | The new return annotation. `UNSET` keeps the original; `None` is a real annotation. *(keyword-only)* |
| `extras`           | `Iterable[inspect.Parameter]` | `()`   | Parameters to add after the copied ones. Any iterable, also a generator. *(keyword-only)*                    |
| `excepts`          | `Iterable[str]`              | `()`    | Names of parameters to leave out. Any iterable, also a generator. *(keyword-only)*                           |
| `accept_double`, `replace_double`, `include_variadic`, `include_binding`, `flat_to_kwargs`, `_validate_call` | | | As in [`signature`](#signature). *(keyword-only)* |

**Returns:** a decorator; applied to a function, it returns a wrapper that reports the copied signature.

**Raises:**
`ParamError` — when the decorator is **created**: `SIGNATURE INTROSPECTION ERROR`,
`DUPLICATE PARAMETER ERROR`, `INVALID PARAMETER ORDER`.
`ValidationError` — an argument has the wrong type.

**Example usage:**

```python
import inspect
from simplibs.signature import signature_copy, create_keyword_parameter

def base(a: int, b=1, *args, k, **kwargs) -> str: ...

@signature_copy(base, extras=[create_keyword_parameter("extra", default=3)], excepts=["a"], returns=None)
def wrapper(*args, **kwargs): ...
str(inspect.signature(wrapper))         # -> '(b=1, *args, k, extra=3, **kwargs) -> None'

class Thing:
    def method(self, x: int, y: int = 0) -> int: ...

@signature_copy(Thing.method, include_binding=False)
def call_method(*args, **kwargs): ...
str(inspect.signature(call_method))     # -> '(x: int, y: int = 0) -> int'      self is not part of the call
```

**Why `extras` and `excepts`.** They are the decorator spelling of `extra_params` and `excluded_names` —
short, because they stand in a line of their own above a function.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def signature_copy(
    base_func: Callable,
    *,
    returns: Any = UNSET,
    extras: Iterable[inspect.Parameter] = (),
    excepts: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> Callable:
    # 1. Create the transformed signature
    signature = copy_signature(
        function = base_func,
        return_annotation = returns,
        extra_params = tuple(extras),
        excluded_names = tuple(excepts),
        accept_double = accept_double,
        replace_double = replace_double,
        include_variadic = include_variadic,
        include_binding = include_binding,
        flat_to_kwargs = flat_to_kwargs,
        _validate_call = False
    )

    # 2. Create and return the decorator
    return create_signature_decorator(
        signature=signature,
        _validate_call=False
    )
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `signature_set`

Decorator factory that **attaches a finished signature** to a function — for when the signature is ready
(built by hand, by [`create_signature`](README_SIGNATURE_ORCHESTRATORS.md#create_signature), read from
another function) and nothing needs to be assembled.

**Parameters:**

| Name             | Type                | Default | Description                                                  |
|------------------|---------------------|---------|--------------------------------------------------------------|
| `signature`      | `inspect.Signature` |         | The signature to attach.                                      |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*         |

**Returns:** a decorator; applied to a function, it returns a wrapper that reports `signature`.

**Example usage:**

```python
import inspect, asyncio
from simplibs.signature import signature_set

@signature_set(inspect.Signature([inspect.Parameter("only", inspect.Parameter.KEYWORD_ONLY)], return_annotation=int))
async def job(*args, **kwargs):
    return 5

str(inspect.signature(job))              # -> '(*, only) -> int'
inspect.iscoroutinefunction(job)         # -> True
asyncio.run(job())                       # -> 5
```

**Why it wraps and does not modify.** Despite the likeness of the name to
[`set_signature`](README_SIGNATURE_TOOLS.md#set_signature), the decorated function itself is left alone: a
wrapper is returned. The same function can be decorated twice, or used undecorated elsewhere.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def signature_set(
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    # 1. Create and return the decorator
    return create_signature_decorator(
        signature=signature,
        _validate_call=False
    )
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `create_signature_decorator`

Turns a finished signature into a **reusable decorator** — the last step that
[`signature_copy`](#signature_copy) and [`signature_set`](#signature_set) share.

**Parameters:**

| Name             | Type                | Default | Description                                                                 |
|------------------|---------------------|---------|-----------------------------------------------------------------------------|
| `signature`      | `inspect.Signature` |         | The signature every decorated function will report.                          |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`; forwarded to `apply_signature_to_wraps`. *(keyword-only)* |

**Returns:** a decorator. Applied to a function, it returns the wrapper made by `apply_signature_to_wraps`.

**Example usage:**

```python
import inspect
from simplibs.signature import create_signature_decorator

decorator = create_signature_decorator(inspect.Signature([inspect.Parameter("z", inspect.Parameter.KEYWORD_ONLY)]))

str(inspect.signature(decorator(lambda: 1)))     # -> '(*, z)'
str(inspect.signature(decorator(lambda: 2)))     # -> '(*, z)'      one decorator, many functions
```

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def create_signature_decorator(
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    # 1. Define the decorator factory
    def decorator(function: Callable) -> Callable:
        return apply_signature_to_wraps(
            function = function,
            signature = signature,
            _validate_call = _validate_call,
        )

    # 2. Return the decorator
    return decorator
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `apply_signature_to_wraps`

Wraps **one function** in a transparent wrapper that reports a given signature — the piece every decorator
here ends in.

**Parameters:**

| Name             | Type                | Default | Description                                                  |
|------------------|---------------------|---------|--------------------------------------------------------------|
| `function`       | `Callable`          |         | The function to wrap.                                         |
| `signature`      | `inspect.Signature` |         | The signature the wrapper reports.                            |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*         |

**Returns:** a new function with the metadata of `function`, forwarding every call to it, and with
`signature` as its `__signature__`. It is `async` if `function` is a coroutine function.

**Example usage:**

```python
import inspect
from simplibs.signature import apply_signature_to_wraps

wrapper = apply_signature_to_wraps(lambda a, b: a + b, inspect.Signature([inspect.Parameter("q", inspect.Parameter.KEYWORD_ONLY)]))

str(inspect.signature(wrapper))      # -> '(*, q)'
wrapper(1, 2)                        # -> 3        the call is forwarded unchanged
```

**Why a wrapper at all, and not `__signature__` on the function.** Assigning `__signature__` to the function
itself (that is what [`set_signature`](README_SIGNATURE_TOOLS.md#set_signature) does) changes an object other
code may share. A decorator must not do that.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def apply_signature_to_wraps(
    function: Callable,
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    # 1. A coroutine function needs an async wrapper, so callers can still await it
    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            return await function(*args, **kwargs)
        wrapper = async_wrapper

    # 2. Anything else gets a plain wrapper
    else:
        @wraps(function)
        def sync_wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        wrapper = sync_wrapper

    # 3. Assign the custom signature
    wrapper.__signature__ = signature

    # 4. Return the transparent wrapper
    return wrapper
```

The two branches exist because a plain wrapper around a coroutine function would return a coroutine object
and lose the fact that the function can be awaited. `__signature__` is assigned to the wrapper, so the
function passed in is left alone.

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

The decorators raise no cards of their own. The `ParamError` cards of
[`simplibs-exception`](https://pypi.org/project/simplibs-exception/) below come from the collector, the
orchestrators and the tools underneath, and reach you unchanged. The card's `label` names the offending part
and its `value` is what was given.

| Error name                      | Wraps        | Raised by                           | Fix                                                                         |
|---------------------------------|--------------|-------------------------------------|-----------------------------------------------------------------------------|
| `INVALID PARAMETER SOURCE`      | `TypeError`  | `signature`                         | Pass `inspect.Parameter` objects or callables only; unpack a list with `*`   |
| `DUPLICATE PARAMETER ERROR`     | `ValueError` | `signature`, `signature_copy`       | Make the names unique, or use `accept_double=True`                           |
| `INVALID PARAMETER ORDER`       | `SyntaxError`| `signature`, `signature_copy`       | Put required parameters before optional ones                                 |
| `SIGNATURE INTROSPECTION ERROR` | `ValueError`, `TypeError` | `signature`, `signature_copy` | Use a Python function or a callable with a readable signature     |

An argument of the wrong type is a `ValidationError` from `@validate_call` and never reaches these.

[▲ Back to top](#-table-of-contents)
