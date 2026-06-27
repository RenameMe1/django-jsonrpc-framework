from collections.abc import Callable, Sequence
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
    access: AccessType = AccessType._NOT_SET,
    summary: str | None = None,
    tags: Sequence[str] | None = None,
    auth: Sequence[type[BaseAuthentication]] | None = None,
    permissions: Sequence[type[BasePermission]] | None = None,
) -> Callable[P, R]:

    if not isinstance(access, AccessType):
        raise ValueError(
            f"Invalid access type: {access}, "
            "expected AccessType.PUBLIC | AccessType.OPTIONAL | AccessType.PRIVATE"
        )

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


def parametrized_decorator[R, **P](
    func: Callable[P, R],
    *,
    name: str | None,
    summary: str | None,
    description: str | None,
    tags: Sequence[str] | None,
    access: AccessType,
    auth: Sequence[type[BaseAuthentication]] | None,
    permissions: Sequence[type[BasePermission]] | None,
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
    tags: Sequence[str] | None = None,
    access: AccessType = AccessType._NOT_SET,
    auth: Sequence[type[BaseAuthentication]] | None = None,
    permissions: Sequence[type[BasePermission]] | None = None,
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
        return parametrized_decorator(
            name_or_func,
            name=name_or_func.__name__,
            summary=summary,
            description=description
            if description is not None
            else name_or_func.__doc__,
            tags=tags,
            access=access,
            auth=auth,
            permissions=permissions,
        )

    return decorator
