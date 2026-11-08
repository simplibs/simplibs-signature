# 🧺 `collector` — One Valid, Ordered Set of Parameters

The `collector` package holds `ParameterCollector`: the class that takes parameters from any number of places
and ends with **one set that is a valid signature body**. Every builder of the library —
[`create_signature`](README_SIGNATURE_ORCHESTRATORS.md#create_signature),
[`copy_signature`](README_SIGNATURE_ORCHESTRATORS.md#copy_signature), the
[modifiers](README_SIGNATURE_TOOLS.md#-modifiers) and, through them, the
[decorators](README_SIGNATURE_DECORATORS.md) — does the same chore: take parameters from several sources, drop
some, settle name collisions and end with an order Python accepts. The collector is that chore, in one place,
and it is public, so you can use it directly when the builders are not enough.

```python
import inspect
from simplibs.signature import ParameterCollector

P = inspect.Parameter

collector = ParameterCollector()
for param in (P("kw", P.VAR_KEYWORD), P("k", P.KEYWORD_ONLY), P("req", P.POSITIONAL_OR_KEYWORD),
              P("a", P.VAR_POSITIONAL), P("p", P.POSITIONAL_ONLY), P("opt", P.POSITIONAL_OR_KEYWORD, default=1)):
    collector.add_param(param)

[p.name for p in collector.get_ordered_params()]     # -> ['p', 'req', 'opt', 'a', 'k', 'kw']
```

You added them in a scrambled order; you got them back in the order Python requires. That is the whole idea.

## The four jobs

| Job                  | What the collector does                                                                           |
|----------------------|---------------------------------------------------------------------------------------------------|
| **Exclude**          | Leaves out the names you list, `self` / `cls` on request, and every `*args` / `**kwargs` on request. |
| **Settle collisions**| A name that is already there — or a second `*args` / `**kwargs` — is refused, replaced or ignored, as you chose. |
| **Keep the order**   | Stores each parameter by kind and by "has a default"; reads them back in the order Python requires. |
| **Flatten**          | In flat mode, turns everything into one keyword-only API.                                          |

## A note on the order

Inside the collector every kind has **two lists**: parameters **without** a default and parameters **with** one.
`get_ordered_params` reads the kinds in the order Python requires, and inside each kind the required list first:

| # | Kind                    | Written as      |
|---|-------------------------|-----------------|
| 1 | `POSITIONAL_ONLY`       | before the `/`  |
| 2 | `POSITIONAL_OR_KEYWORD` | an ordinary `x` |
| 3 | `VAR_POSITIONAL`        | `*args`         |
| 4 | `KEYWORD_ONLY`          | after the `*`   |
| 5 | `VAR_KEYWORD`           | `**kwargs`      |

Because the order comes from the storage and not from the order of insertion, sources can be loaded in any
order — with **one exception**. A *required* positional parameter that arrives after an *optional* one
(`def f(a=1, b)`) cannot be put anywhere valid: moving it would change the meaning of a call. The collector
refuses it with an `INVALID PARAMETER ORDER` card. Keyword-only parameters have no such rule.

```python
collector = ParameterCollector()
collector.add_param(P("kw", P.KEYWORD_ONLY, default=1))
collector.add_param(P("req", P.KEYWORD_ONLY))
[p.name for p in collector.get_ordered_params()]     # -> ['req', 'kw']        the required one went first

collector = ParameterCollector()
collector.add_param(P("a", P.POSITIONAL_OR_KEYWORD, default=1))
collector.add_param(P("b", P.POSITIONAL_OR_KEYWORD))    # raises: INVALID PARAMETER ORDER — 'b' cannot follow parameters with defaults
```

## A note on collisions

A **collision** is a parameter that meets one with the same name — or a second `*args`, or a second
`**kwargs`, whatever it is called. What happens is decided by two options:

| `accept_double` | `replace_double` | The result                                                           |
|-----------------|------------------|----------------------------------------------------------------------|
| `False`         | *(ignored)*      | a `DUPLICATE PARAMETER ERROR` card                                    |
| `True` (default)| `True` (default) | the **later** parameter replaces the stored one                       |
| `True`          | `False`          | the **earlier** parameter stays; the new one is dropped               |

```python
collector = ParameterCollector()
collector.add_params([P("x", P.POSITIONAL_OR_KEYWORD, default=1), P("x", P.POSITIONAL_OR_KEYWORD, default=2)])
[(p.name, p.default) for p in collector.get_ordered_params()]     # -> [('x', 2)]

collector = ParameterCollector(replace_double=False)
collector.add_params([P("x", P.POSITIONAL_OR_KEYWORD, default=1), P("x", P.POSITIONAL_OR_KEYWORD, default=2)])
[(p.name, p.default) for p in collector.get_ordered_params()]     # -> [('x', 1)]
```

A replacement may change the kind and the default status: the stored parameter is removed from wherever it
was and the new one is stored where *it* belongs.

### One `*args`, one `**kwargs`

`inspect.Signature` accepts `(*a, *b)` and `(**x, **y)` without complaint, so nothing downstream would catch
them. The collector treats the variadic of each kind as **one slot**, and the table above applies to it as
well:

```python
collector = ParameterCollector()
collector.add_params([P("a", P.VAR_POSITIONAL), P("b", P.VAR_POSITIONAL)])
[p.name for p in collector.get_ordered_params()]     # -> ['b']                  the later *b replaced *a

collector = ParameterCollector(accept_double=False)
collector.add_param(P("a", P.VAR_POSITIONAL))
collector.add_param(P("b", P.VAR_POSITIONAL))        # raises: DUPLICATE PARAMETER ERROR — 'b' collides with the already defined variadic positional parameter 'a'
```

`*args` and `**kwargs` never collide with each other: they are different kinds.

## A note on exclusion

Two options leave things out, and they work in **different** ways on purpose.

| Option                  | Leaves out …                                  | Recognised by          |
|-------------------------|-----------------------------------------------|------------------------|
| `excluded_names`        | the names you list                            | **name**               |
| `include_binding=False` | `self` and `cls`                              | **name** (a convention) |
| `include_variadic=False`| every `*args` and `**kwargs`                  | **kind**               |

`self` and `cls` are ordinary parameters — nothing but the convention marks them — so they can only be found
by name. Variadics have a kind of their own, so they are found by it: `*a` and `**options` go as well as
`*args` and `**kwargs`, and a regular parameter that merely *happens* to be called `args` stays.

```python
collector = ParameterCollector(include_variadic=False)
collector.add_params([P("x", P.POSITIONAL_OR_KEYWORD), P("a", P.VAR_POSITIONAL), P("options", P.VAR_KEYWORD)])
[p.name for p in collector.get_ordered_params()]     # -> ['x']
```

An excluded parameter leaves **no trace**: it takes part in no collision, no order check and, in flat mode,
no renaming.

## A note on flat mode

`flat_to_kwargs=True` is for merging unrelated signatures. Clashes of kinds and defaults disappear because
every regular parameter becomes **keyword-only**: those may follow each other in any order, with or without
defaults.

| Kind              | Result in flat mode                                    |
|-------------------|--------------------------------------------------------|
| `VAR_POSITIONAL`  | **dropped** — a keyword-only API has no place for it   |
| `VAR_KEYWORD`     | all merge into one `**kwargs` (the `KWARGS` constant)  |
| everything else   | stored as `KEYWORD_ONLY`, in the order they arrived    |

```python
collector = ParameterCollector(flat_to_kwargs=True)
collector.add_params([P("p", P.POSITIONAL_ONLY), P("x", P.POSITIONAL_OR_KEYWORD, default=1),
                      P("a", P.VAR_POSITIONAL), P("options", P.VAR_KEYWORD)])
str(inspect.Signature(collector.get_ordered_params()))     # -> '(*, p, x=1, **kwargs)'
```

**Smart renaming.** Flat mode exists to merge *without losing anything*, so with `replace_double=False`
the collision rule is different from the normal mode: **both** parameters are kept and the later one is
renamed to `name_1`, `name_2`, … until the name is free.

```python
collector = ParameterCollector(flat_to_kwargs=True, replace_double=False)
collector.add_params([P("x", P.POSITIONAL_OR_KEYWORD), P("x", P.POSITIONAL_OR_KEYWORD), P("x", P.POSITIONAL_OR_KEYWORD)])
[p.name for p in collector.get_ordered_params()]     # -> ['x', 'x_1', 'x_2']
```

`**kwargs` ignores `accept_double` in flat mode: two of them are not a clash worth an error — they are folded
into one.

---

## 🧭 Table of Contents

* [`ParameterCollector`](#parametercollector)
* [`add_param`](#add_param)
* [`add_params`](#add_params)
* [`get_ordered_params`](#get_ordered_params)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-collector--one-valid-ordered-set-of-parameters)

---

### `ParameterCollector`

Creates a collector with its **exclusion, collision and mode rules**. The rules are fixed for the life of the
collector; parameters are added afterwards.

**Parameters:**

| Name               | Type            | Default | Description                                                                 |
|--------------------|-----------------|---------|-----------------------------------------------------------------------------|
| `excluded_names`   | `Iterable[str]` | `()`    | Names to leave out. Any iterable: list, set, tuple, generator. *(keyword-only)* |
| `accept_double`    | `bool`          | `True`  | If `False`, a collision raises. If `True`, `replace_double` decides. *(keyword-only)* |
| `replace_double`   | `bool`          | `True`  | `True`: the later parameter replaces the earlier one. `False`: the earlier one stays (flat mode: both are kept, the later one renamed). *(keyword-only)* |
| `include_variadic` | `bool`          | `True`  | If `False`, every `*args` and `**kwargs` is left out, by kind. *(keyword-only)* |
| `include_binding`  | `bool`          | `True`  | If `False`, parameters named `self` and `cls` are left out. *(keyword-only)*  |
| `flat_to_kwargs`   | `bool`          | `False` | Flat mode: everything keyword-only. *(keyword-only)*                           |
| `_validate_call`   | `bool`          | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*                          |

**Returns:** the collector, empty.

**Raises:** `ValidationError` — an argument has the wrong type.

**Example usage:**

```python
from simplibs.signature import ParameterCollector

ParameterCollector()                                              # keep everything, the later parameter wins
ParameterCollector(excluded_names=["secret"], include_binding=False)
ParameterCollector(accept_double=False)                           # strict: a collision is an error
ParameterCollector(flat_to_kwargs=True, include_variadic=False)   # merge into plain keyword-only parameters

collector = ParameterCollector(excluded_names=["secret"], include_binding=False)
collector.add_params([P("self", P.POSITIONAL_OR_KEYWORD), P("x", P.POSITIONAL_OR_KEYWORD), P("secret", P.KEYWORD_ONLY)])
[p.name for p in collector.get_ordered_params()]                  # -> ['x']
```

**Why two lists per kind.** The storage is `kind → (without default | with default) → list`. A parameter is
filed once, when it arrives, and the order falls out of reading the storage back — nothing is sorted, and a
parameter is found again by name in constant time through an index (`name → (kind, tier)`).

**Why the behaviour is not in the class.** The rules live in plain functions (`add_param` and its parts, in the
`_methods` sub-package); the class only holds the state and hands it over. That keeps every rule testable
without building a collector.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def __init__(
    self,
    *,
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
):
    # 1. Build excluded names set (variadics are excluded by kind, not by name)
    self._excluded_names = set(excluded_names)
    if not include_binding:
        self._excluded_names.update(BINDING_NAMES)

    # 2. Store configuration
    self._include_variadic = include_variadic
    self._accept_double = accept_double
    self._replace_double = replace_double
    self._flat_to_kwargs = flat_to_kwargs

    # 3. Initialize name tracking (maps name to its location for O(1) replacement)
    self._seen_names = {}

    # 4. Initialize tiered storage map using constants
    self._params_map = {
        kind: {WITHOUT_DEFAULT: [], CONTAIN_DEFAULT: []}
        for kind in (
            POSITIONAL_ONLY,
            POSITIONAL_OR_KEYWORD,
            VAR_POSITIONAL,
            KEYWORD_ONLY,
            VAR_KEYWORD
        )
    }
```

`excluded_names` is read into a `set` once. `include_variadic` is **not** folded into it — variadics are not
excluded by name — it is stored and checked by kind for every parameter.

</details>

[▲ Back to top](#-table-of-contents)

---

### `add_param`

Adds **one parameter**, subject to the exclusion, collision and order rules.

**Parameters:**

| Name             | Type                | Default | Description                                            |
|------------------|---------------------|---------|--------------------------------------------------------|
| `param`          | `inspect.Parameter` |         | The parameter to add.                                   |
| `_validate_call` | `bool`              | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*   |

**Returns:** `None`.

**Raises:**
`ParamError` — `DUPLICATE PARAMETER ERROR` (a collision with `accept_double=False`), `INVALID PARAMETER ORDER`
(a required positional parameter after an optional one), `INVALID PARAMETER KIND ERROR` (a kind the storage has
no slot for).
`ValidationError` — `param` is not an `inspect.Parameter`.

**Example usage:**

```python
collector = ParameterCollector(accept_double=False)
collector.add_param(P("x", P.POSITIONAL_OR_KEYWORD))             # stored
collector.add_param(P("x", P.KEYWORD_ONLY))                      # raises: DUPLICATE PARAMETER ERROR — 'x' is already defined in this signature
collector.add_param("x")                                         # raises ValidationError — not a Parameter
```

**The order of the decisions.** For every parameter, in this order:

1. A name you excluded, and `self` / `cls` if asked, is dropped.
2. A variadic is dropped if `include_variadic=False`.
3. In flat mode, the flat rules take over.
4. A collision (same name, or a second variadic of a kind) is refused, or settled for the old or the new one.
5. A required positional parameter after an optional one is refused.
6. The parameter is filed under its kind and tier, and its name is indexed.

Exclusion comes first so that an excluded parameter leaves no trace — no collision, no order check.

<details>
<summary>🔍 Under the hood</summary>

```python
def add_param(
    param: inspect.Parameter,
    excluded_names: set[str],
    include_variadic: bool,
    flat_to_kwargs: bool,
    accept_double: bool,
    replace_double: bool,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    # 1. Exclusion by name (the caller's names, `self` and `cls`)
    if param.name in excluded_names:
        return

    # 2. Exclusion by kind: a variadic is recognised by what it is, not by its name
    if not include_variadic and param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
        return

    # 3. Flat mode has its own storage rules
    if flat_to_kwargs:
        _flat_params_to_kwargs(
            param=param,
            params_map=params_map,
            seen_names=seen_names,
            accept_double=accept_double,
            replace_double=replace_double
        )
        return

    # 4. Collision: the same name, or a second variadic of a kind already stored
    colliding_name = _find_colliding_name(param, seen_names, params_map)
    if colliding_name is not None:

        # 4.1 Strict: a collision is an error
        if not accept_double:
            raise_duplicate_parameter_error(param, colliding_name)

        # 4.2 The original stays, the new parameter is dropped
        if not replace_double:
            return

        # 4.3 The new parameter replaces the stored one
        _remove_param(colliding_name, seen_names, params_map)

    # 5. A required positional parameter may not follow an optional one
    _positional_empty_order_check(param, params_map)

    # 6. Pick the tier: with or without a default
    inner_key = WITHOUT_DEFAULT if param.default is EMPTY else CONTAIN_DEFAULT

    # 7. Store it
    try:
        params_map[param.kind][inner_key].append(param)

    # 8. A kind the storage map does not know
    except KeyError as e:
        raise_invalid_parameter_kind_error(param, e)

    # 9. Index the name
    seen_names[param.name] = (param.kind, inner_key)
```

The steps of the code are the six decisions above. The four rules that need a function of their own:

```python
def _find_colliding_name(
    param: inspect.Parameter,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> str | None:
    # 1. The same name is always a collision
    if param.name in seen_names:
        return param.name

    # 2. A signature holds one variadic of each kind, whatever it is called
    if param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
        stored = params_map[param.kind][WITHOUT_DEFAULT]
        if stored:
            return stored[0].name

    # 3. Nothing in the way
    return None
```

It returns the **stored** name, not the name of the new parameter, because for a second `*b` the stored one is `a`
and that is what has to be removed.

```python
def _remove_param(
    name: str,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    # 1. Unknown name, nothing to remove
    if name not in seen_names:
        return

    # 2. Forget the name, and take the parameter out of its tier
    kind_key, default_key = seen_names.pop(name)
    params_map[kind_key][default_key] = [
        p for p in params_map[kind_key][default_key]
        if p.name != name
    ]
```

`_remove_param` also forgets the name, so a real parameter `a` can follow a replaced `*a` without being taken for a
duplicate.

```python
def _positional_empty_order_check(
    param: inspect.Parameter,
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    # 1. Skip check if the parameter has a default value
    if param.default is not EMPTY:
        return

    # 2. Validation Logic
    # 2.1 Check for POSITIONAL_ONLY violations
    if (
        param.kind is POSITIONAL_ONLY
        and params_map[POSITIONAL_ONLY][CONTAIN_DEFAULT]

        # 2.2 Check for POSITIONAL_OR_KEYWORD violations
    ) or (
        param.kind is POSITIONAL_OR_KEYWORD
        and (
            params_map[POSITIONAL_ONLY][CONTAIN_DEFAULT]
            or params_map[POSITIONAL_OR_KEYWORD][CONTAIN_DEFAULT]
        )
    ):
        # 2.3 Raise exception if a violation is detected
        raise_invalid_parameter_order_error(param)
```

```python
def _flat_params_to_kwargs(
    param: inspect.Parameter,
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]],
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    accept_double: bool,
    replace_double: bool,
) -> None:
    # 1. Variadic positional (*args) is dropped as it has no place in a flat signature.
    if param.kind is VAR_POSITIONAL:
        return

    # 2. Variadic keyword (**kwargs) is unified into a single clean placeholder.
    if param.kind is VAR_KEYWORD:
        if not params_map[VAR_KEYWORD][WITHOUT_DEFAULT]:
            params_map[VAR_KEYWORD][WITHOUT_DEFAULT].append(KWARGS)
            seen_names[KWARGS.name] = (VAR_KEYWORD, WITHOUT_DEFAULT)
        return

    # 3. Transform regular parameters to KEYWORD_ONLY
    param = param.replace(kind=KEYWORD_ONLY)

    # 4. Handle Name Collisions and Replacement Strategy
    if param.name in seen_names:

        # 4.1 Strict Duplicate Check
        if not accept_double:
            raise_duplicate_parameter_error(param)

        # 4.2 Replacement Strategy: Overwrite existing
        if replace_double:
            _remove_param(param.name, seen_names, params_map)

        # 4.3 Replacement Strategy: Keep & Rename (Smart Renaming)
        else:
            original_name = param.name
            counter = 1
            while param.name in seen_names:
                param = param.replace(name=f"{original_name}_{counter}")
                counter += 1

    # 5. Routing to Internal Storage
    params_map[KEYWORD_ONLY][CONTAIN_DEFAULT].append(param)

    # 6. Index Mapping Update
    seen_names[param.name] = (KEYWORD_ONLY, CONTAIN_DEFAULT)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `add_params`

Adds **several parameters**, one after another, in the order given. Each is treated exactly as `add_param`
would treat it.

**Parameters:**

| Name             | Type                          | Default | Description                                                    |
|------------------|-------------------------------|---------|----------------------------------------------------------------|
| `params`         | `Iterable[inspect.Parameter]` |         | The parameters to add. Any iterable, also a generator.           |
| `_validate_call` | `bool`                        | `True`  | Reserved switch of `@validate_call`. *(keyword-only)*            |

**Returns:** `None`.

**Raises:** as [`add_param`](#add_param).

**Example usage:**

```python
collector = ParameterCollector()
collector.add_params(inspect.signature(original).parameters.values())     # all parameters of a function
collector.add_params(P(name, P.KEYWORD_ONLY) for name in ("x", "y"))      # a generator is fine
```

**Why the order still matters a little.** The result is always in the valid order, but *who wins a collision*
depends on which parameter arrives later — so the order you give is the priority.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call(materialize_iterators=True)
def add_params(
    self,
    params: Iterable[inspect.Parameter],
    *,
    _validate_call: bool = True
) -> None:
    for param in params:
        self.add_param(param, _validate_call=False)
```

Each parameter goes through `add_param` with `_validate_call=False`: the iterable was already checked once.
`materialize_iterators=True` turns a generator into a tuple before the method starts, so it is read exactly once.

</details>

[▲ Back to top](#-table-of-contents)

---

### `get_ordered_params`

Returns the stored parameters **in the order Python requires**.

**Parameters:** none.

**Returns:** a `tuple[inspect.Parameter, ...]`, ordered by kind and, inside each kind, required before
optional. A new tuple on every call; the collector is not changed, so you can keep adding and read again.

**Example usage:**

```python
collector = ParameterCollector()
collector.add_params([P("req", P.POSITIONAL_OR_KEYWORD), P("a", P.VAR_POSITIONAL), P("k", P.KEYWORD_ONLY)])

collector.get_ordered_params()                         # -> (<Parameter "req">, <Parameter "*a">, <Parameter "k">)
inspect.Signature(collector.get_ordered_params())      # always valid — or this raises
```

**Why a tuple.** An immutable result that nobody can change under the collector's feet — and exactly what
[`compose_signature`](README_SIGNATURE_TOOLS.md#compose_signature) and `inspect.Signature` accept.

<details>
<summary>🔍 Under the hood</summary>

```python
def get_ordered_params(
    self
) -> tuple[inspect.Parameter, ...]:
    return tuple(
        param
        for category_map in self._params_map.values()
        for param_list in category_map.values()
        for param in param_list
    )
```

The storage is created in the order of the kinds, so reading it back in insertion order of the map **is** the
valid order; nothing is sorted at the end.

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

The collector raises `ParamError` cards of [`simplibs-exception`](https://pypi.org/project/simplibs-exception/);
the package defines no exceptions of its own. The card's `label` names the offending part and its `value` is
what was given.

| Error name                     | Wraps         | Raised by                   | Fix                                                                         |
|--------------------------------|---------------|-----------------------------|-----------------------------------------------------------------------------|
| `DUPLICATE PARAMETER ERROR`    | `ValueError`  | `add_param`, `add_params`   | Make the names unique (also: one `*args` and one `**kwargs`), or use `accept_double=True` |
| `INVALID PARAMETER ORDER`      | `SyntaxError` | `add_param`, `add_params`   | Add required parameters before optional ones, or use `flat_to_kwargs=True`    |
| `INVALID PARAMETER KIND ERROR` | `KeyError`    | `add_param`, `add_params`   | Use the standard `inspect.Parameter` kinds                                    |

An argument of the wrong type is a `ValidationError` from `@validate_call` and never reaches these.

[▲ Back to top](#-table-of-contents)
