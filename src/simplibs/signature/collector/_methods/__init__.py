from .add_param import add_param


_DESIGN_NOTES = """
# Collector Methods Sub-Package

## Purpose
The logic of `ParameterCollector` as plain functions: state goes in as
arguments, so each function can be tested without building a collector. Plain
imports, no `__all__`: the package root decides what is public.

## Internal Components Registry

| Component                       | Type        | Description                                            |
| :------------------------------ | :---------- | :----------------------------------------------------- |
| `add_param`                     | Function    | The single entry door: exclude, collide, order, store. |
| `_find_colliding_name`          | Function    | Which stored parameter a new one collides with.        |
| `_flat_params_to_kwargs`        | Function    | Flat mode: everything keyword-only.                    |
| `_positional_empty_order_check` | Function    | Required positional after optional is refused.         |
| `_remove_param`                 | Function    | Removes a stored parameter and forgets its name.       |
| `validations`                   | Sub-package | The errors of the collector.                           |

Only `add_param` is exported; the underscored functions are its private parts.
"""
