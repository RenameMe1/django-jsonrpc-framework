from typing import Generic, TypeVar, Callable, Any, ClassVar, Self, Protocol

from pydantic import BaseModel, ValidationError

from jsonrpc_framework.controller.auth import AuthResult, INVALID_AUTH
from django.http import HttpRequest
from typing import Awaitable
from jsonrpc_framework.controller.auth import AccessPolicy

try:
    import jwt
except ImportError:
    raise ImportError(
        "PyJWT is not installed, please install it with `pip install django-jsonrpc-framework[jwt]`"
    ) from None


TokenT = TypeVar("TokenT", bound=BaseModel)

class AsyncPermissionCheckerType(Protocol):
    def __call__(self, auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy) -> Awaitable[bool]:
        ...

class PermissionCheckerType(Protocol):
    def __call__(self, auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy) -> bool:
        ...

class TokenDecoderType(Protocol):
    def __call__(self, token: str) -> dict[str, Any]: ...

class AsyncTokenDecoderType(Protocol):
    def __call__(self, token: str) -> Awaitable[dict[str, Any]]:
        ...

class BearerAuthentication(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    decode_token: ClassVar[TokenDecoderType]
    name: ClassVar[str]

    def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    def authenticate(self, request: HttpRequest) -> AuthResult | None:
        print("asdasdasdasdsadasds")
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token is None:
            return INVALID_AUTH

        payload = self.decode_token(token)

        if payload is None:
            return INVALID_AUTH

        try:
            token_data = self.token_model.model_validate(payload)
        except ValidationError:
            return INVALID_AUTH

        return AuthResult(
            auth_result=token_data,
            credentials_present=True,
            backend_used=self.__class__,
        )


class AsyncBearerAuthentication(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    decode_token: ClassVar[AsyncTokenDecoderType]
    name: ClassVar[str]

    async def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        print("asdasdasdasdsadasds")
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token is None:
            return INVALID_AUTH

        payload = await self.decode_token(token)

        if payload is None:
            return INVALID_AUTH

        try:
            token_data = self.token_model.model_validate(payload)
        except ValidationError:
            return INVALID_AUTH

        return AuthResult(
            auth_result=token_data,
            credentials_present=True,
            backend_used=self.__class__,
        )


class BearerPermission(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    permission_checker: ClassVar[PermissionCheckerType]
    name: ClassVar[str]

    def has_permission(
        self, access_policy: AccessPolicy, request: HttpRequest, auth_result: AuthResult
    ) -> bool:
        return self.permission_checker(auth_result, request, access_policy)


class AsyncBearerPermission(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    permission_checker: ClassVar[AsyncPermissionCheckerType]
    name: ClassVar[str]

    async def has_permission(
        self, access_policy: AccessPolicy, request: HttpRequest, auth_result: AuthResult
    ) -> bool:
        return await self.permission_checker(auth_result, request, access_policy)


def make_bearer_auth_backend(
    *,
    token_model: type[TokenT],
    token_decoder: TokenDecoderType,
) -> type[BearerAuthentication[TokenT]]:

    class _Backend(BearerAuthentication[TokenT]):
        token_model: ClassVar[type[TokenT]]
        decode_token: ClassVar[TokenDecoderType]
        name: ClassVar[str]

    _Backend.token_model = token_model
    _Backend.decode_token = staticmethod(token_decoder)
    _Backend.name = f"BearerAuth_{token_model.__name__}"

    return _Backend


def make_permission_backend(
    *,
    token_model: type[TokenT],
    permission_checker: PermissionCheckerType,
) -> type[BearerPermission[TokenT]]:

    class _Permission(BearerPermission[TokenT]):
        token_model: ClassVar[type[TokenT]]
        permission_checker: ClassVar[PermissionCheckerType]
        name: ClassVar[str]

    _Permission.token_model = token_model
    _Permission.permission_checker = staticmethod(permission_checker)
    _Permission.name = f"Permission_{token_model.__name__}"

    return _Permission


def make_async_bearer_auth_backend(
    *,
    token_model: type[TokenT],
    token_decoder: AsyncTokenDecoderType,
) -> type[AsyncBearerAuthentication[TokenT]]:
    class _Backend(AsyncBearerAuthentication[TokenT]):
        token_model: ClassVar[type[TokenT]]
        decode_token: ClassVar[AsyncTokenDecoderType]
        name: ClassVar[str]

    _Backend.token_model = token_model
    _Backend.decode_token = staticmethod(token_decoder)
    _Backend.name = f"BearerAuth_{token_model.__name__}"

    return _Backend


def make_async_permission_backend(
    *,
    token_model: type[TokenT],
    permission_checker: AsyncPermissionCheckerType,
) -> type[AsyncBearerPermission[TokenT]]:
    class _Permission(AsyncBearerPermission[TokenT]):
        token_model: ClassVar[type[TokenT]]
        permission_checker: ClassVar[AsyncPermissionCheckerType]
        name: ClassVar[str]

    _Permission.token_model = token_model
    _Permission.permission_checker = staticmethod(permission_checker)
    _Permission.name = f"Permission_{token_model.__name__}"

    return _Permission
