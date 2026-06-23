from __future__ import annotations

from enum import StrEnum
from collections.abc import Sequence
from typing import Protocol, Any, assert_never, Final
from dataclasses import dataclass

from django.http import HttpRequest

__all__ = [
    "AccessType",
    "AuthResult",
    "AccessPolicy",
    "run_auth",
    "BaseAuthentication",
    "BasePermission",
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
    backend_used: type[BaseAuthentication] | None


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


class BasePermission: ...


ANONYMOUS_AUTH: Final = AuthResult(auth_result=None, credentials_present=False, backend_used=None)

@dataclass
class AccessPolicy:
    access: AccessType
    auth: Sequence[type[BaseAuthentication]]
    permissions: Sequence[type[BasePermission]]


def run_auth(access_policy: AccessPolicy, request: HttpRequest) -> AuthResult | None:

    if access_policy.access == AccessType.PUBLIC:
        return ANONYMOUS_AUTH
    elif access_policy.access == AccessType.OPTIONAL:
        return handle_optional_access(request, access_policy.auth)
    elif access_policy.access == AccessType.PRIVATE:
        return handle_private_access()
    else:
        assert_never(AccessPolicy.access)

def handle_optional_access(
    request: HttpRequest,
    auth_backends: Sequence[type[BaseAuthentication]],
    ) -> AuthResult | None:

    has_credentials = False
    requested_backends = []

    for backend in auth_backends:
        backend = backend()

        if backend.has_credentials(request):
            has_credentials = True
            requested_backends.append(backend)

    if not has_credentials:
        return ANONYMOUS_AUTH

    for backend in requested_backends:
        auth_result = backend.authenticate(request)

        if auth_result is not None:
            return auth_result

    return None


def handle_private_access(
    request: HttpRequest,
    auth_backends: Sequence[type[BaseAuthentication]],
    ) -> AuthResult | None:

    for backend in auth_backends:
        backend = backend()

        if backend.has_credentials(request):
            return backend.authenticate(request)

    return None
