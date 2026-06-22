from collections.abc import Callable
from functools import wraps
from typing import Any

from jsonrpc_framework.controller.auth import (
    AccessType,
    BaseAuthentication,
    BasePermission,
)


def _add_metadata(*funcs: Callable[..., Any], **kwargs: Any) -> None:
    for key, value in kwargs.items():
        for func in funcs:
            setattr(func, f"__rpc_method_{key}__", value)


def _decorate[R, **P](
    func: Callable[P, R],
    *,
    rpc_name: str,
    description: str | None,
    access: AccessType | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    auth: list[type[BaseAuthentication]] | None = None,
    permissions: list[type[BasePermission]] | None = None,
) -> Callable[P, R]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    _add_metadata(
        func,
        wrapper,
        name=rpc_name,
        summary=summary,
        description=description,
        tags=tags,
        access=access,
        auth=auth,
        permissions=permissions,
    )

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
    name: str | None,
    summary: str | None,
    description: str | None,
    tags: list[str] | None,
    access: AccessType | None,
    auth: list[type[BaseAuthentication]] | None,
    permissions: list[type[BasePermission]] | None,
) -> Callable[P, R]:
    rpc_name = name if isinstance(name, str) else func.__name__
    return _decorate(
        func,
        rpc_name=rpc_name,
        summary=summary,
        description=description,
        tags=tags,
        access=access,
        auth=auth,
        permissions=permissions,
    )


def jsonrpc_method(
    name_or_func: str | Callable[..., Any] | None = None,
    *,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    access: AccessType | None = None,
    auth: list[type[BaseAuthentication]] | None = None,
    permissions: list[type[BasePermission]] | None = None,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return parametrized_decorator(
            func,
            name=name_or_func if isinstance(name_or_func, str) else None,
            summary=summary,
            description=description,
            tags=tags,
            access=access,
            auth=auth,
            permissions=permissions,
        )

    if callable(name_or_func):
        return simple_decorator(
            name_or_func,
        )

    return decorator
