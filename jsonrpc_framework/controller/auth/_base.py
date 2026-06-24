from __future__ import annotations

from enum import StrEnum
from collections.abc import Sequence, Callable
from typing import Protocol, Any, assert_never, Final
from dataclasses import dataclass
from inspect import iscoroutinefunction

from django.http import HttpRequest


__all__ = [
    "AccessType",
    "AuthResult",
    "AccessPolicy",
    "run_auth",
    "BaseAuthentication",
    "BasePermission",
    "AsyncBaseAuthentication",
    "AsyncBasePermission",
]


class AccessType(StrEnum):
    PUBLIC = "public"
    OPTIONAL = "optional"
    PRIVATE = "private"
    _NOT_SET = "not_set"


@dataclass
class AuthResult:
    auth_result: Any | None
    credentials_present: bool
    backend_used: type[BaseAuthentication | AsyncBaseAuthentication] | None


class BaseAuthentication(Protocol):
    def has_credentials(self, request: HttpRequest) -> bool:
        """
        Return True if user try to authenticate with this backend.
        Return False if user not try to authenticate with this backend.
        """
        ...

    def authenticate(self, request: HttpRequest) -> AuthResult | None:
        """
        If has_credentials returns True, this method must be called to authenticate the user.

        Return AuthResult if the user is authenticated, otherwise return None.
        """
        ...


class AsyncBaseAuthentication(Protocol):
    async def has_credentials(self, request: HttpRequest) -> bool:
        """
        Return True if user try to authenticate with this backend.
        Return False if user not try to authenticate with this backend.
        """
        ...

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        """
        If has_credentials returns True, this method must be called to authenticate the user.

        Return AuthResult if the user is authenticated, otherwise return None.
        """
        ...


class BasePermission(Protocol):
    def has_permission(
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...


class AsyncBasePermission(Protocol):
    async def has_permission(
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...


ANONYMOUS_AUTH: Final = AuthResult(
    auth_result=None, credentials_present=False, backend_used=None
)
INVALID_AUTH: Final = None


@dataclass
class AccessPolicy:
    access: AccessType
    auth: Sequence[type[BaseAuthentication | AsyncBaseAuthentication]]
    permissions: Sequence[type[BasePermission | AsyncBasePermission]]


async def run_auth(
    access_policy: AccessPolicy, request: HttpRequest
) -> AuthResult | None:

    if access_policy.access == AccessType.PUBLIC:
        return ANONYMOUS_AUTH
    elif access_policy.access == AccessType.OPTIONAL:
        print(access_policy.access)
        return await _handle_optional_access(request, access_policy.auth)
    elif access_policy.access == AccessType.PRIVATE:
        return await _handle_private_access(request, access_policy.auth)
    else:
        assert_never(AccessPolicy.access)


async def _handle_optional_access(
    request: HttpRequest,
    auth_backends: Sequence[type[BaseAuthentication]],
) -> AuthResult | None:

    print("start optional access \n")

    has_credentials = False
    requested_backends = []

    for backend in auth_backends:
        backend = backend()

        if await is_have_credentials(backend, request):
            has_credentials = True
            requested_backends.append(backend)
        else:
            continue

    print(f"has_credentials: {has_credentials}")

    if not has_credentials:
        return ANONYMOUS_AUTH

    for backend in requested_backends:
        auth_result = await is_authenticate(backend, request)

        if auth_result is not INVALID_AUTH:
            return auth_result

    return INVALID_AUTH


async def _handle_private_access(
    request: HttpRequest,
    auth_backends: Sequence[type[BaseAuthentication]],
) -> AuthResult | None:

    for backend in auth_backends:
        backend = backend()

        if await is_have_credentials(backend, request):
            auth_result = await is_authenticate(backend, request)

            if auth_result is not INVALID_AUTH:
                return auth_result

    return INVALID_AUTH


async def is_have_credentials(
    backend: type[BaseAuthentication | AsyncBaseAuthentication], request: HttpRequest
) -> bool:
    if iscoroutinefunction(backend.has_credentials):
        return await backend.has_credentials(request)
    else:
        return backend.has_credentials(request)


async def is_authenticate(
    backend: type[BaseAuthentication | AsyncBaseAuthentication], request: HttpRequest
) -> AuthResult | None:
    if iscoroutinefunction(backend.authenticate):
        return await backend.authenticate(request)
    else:
        return backend.authenticate(request)


async def run_permissions(
    access_policy: AccessPolicy,
    request: HttpRequest,
    auth_result: AuthResult,
    handler: Callable[..., Any],
) -> bool:

    if access_policy.access == AccessType.PUBLIC:
        return True
    elif (
        access_policy.access == AccessType.OPTIONAL
        and not auth_result.credentials_present
    ):
        return True

    for backend in access_policy.permissions:
        backend = backend()

        if iscoroutinefunction(backend.has_permission):
            has_permission = await backend.has_permission(request, auth_result, handler)
        else:
            has_permission = backend.has_permission(request, auth_result, handler)

        if not has_permission:
            return False

    return True
