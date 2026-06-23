from collections.abc import Callable
from functools import wraps
from typing import Any


def _decorate[R, **P](
    func: Callable[P, R],
    rpc_name: str,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Callable[P, R]:
    # Keep an explicit RPC alias on the callable, because class attribute
    # names are used during registry collection and cannot be renamed here.
    func.__rpc_method_name__ = rpc_name
    func.__rpc_method_summary__ = summary
    func.__rpc_method_description__ = description
    func.__rpc_method_tags__ = tags

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    wrapper.__rpc_method_name__ = rpc_name
    wrapper.__rpc_method_summary__ = summary
    wrapper.__rpc_method_description__ = description
    wrapper.__rpc_method_tags__ = tags

    return wrapper


def simple_decorator[R, **P](
    func: Callable[P, R],
) -> Callable[P, R]:
    return _decorate(
        func,
        rpc_name=func.__name__,
        description=func.__doc__,
    )


def parametrized_decorator[R, **P](
    func: Callable[P, R],
    *,
    name: str | None = None,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Callable[P, R]:
    rpc_name = name if isinstance(name, str) else func.__name__
    return _decorate(
        func,
        rpc_name,
        summary,
        description,
        tags,
    )


def jsonrpc_method(
    name_or_func: str | Callable[..., Any] | None = None,
    *,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return parametrized_decorator(
            func,
            name=name_or_func if isinstance(name_or_func, str) else None,
            summary=summary,
            description=description,
            tags=tags,
        )

    if callable(name_or_func):
        return simple_decorator(
            name_or_func,
        )

    return decorator
