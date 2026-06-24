from typing import Generic, TypeVar, Callable, Any

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


type AsyncPermissionChecker = Callable[[TokenT, HttpRequest], Awaitable[bool]]

class BearerAuthentication(Generic[TokenT]):
    token_model: type[TokenT]
    decode_token: Callable[[str], dict[str, Any]]
    name: str

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
            backend_used=self.name,
        )


class AsyncBearerAuthentication(Generic[TokenT]):
    token_model: type[TokenT]
    decode_token: Awaitable[Callable[[str], dict[str, Any]]]
    name: str

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
            backend_used=self.name,
        )


class BearerAuthentication(Generic[TokenT]):
    token_model: type[TokenT]
    decode_token: Callable[[str], dict[str, Any]]
    name: str

    async def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
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
            backend_used=self.name,
        )


class BearerPermission(Generic[TokenT]):
    token_model: type[TokenT]
    permission_checker: Callable[[TokenT, HttpRequest], bool]
    name: str

    def has_permission(
        self, access_policy: AccessPolicy, request: HttpRequest, auth_result: AuthResult
    ) -> bool:
        return self.permission_checker(auth_result.auth_result)


class AsyncBearerPermission(Generic[TokenT]):
    token_model: type[TokenT]
    permission_checker: AsyncPermissionChecker
    name: str

    async def has_permission(
        self, request: HttpRequest, auth_result: AuthResult, handler: Callable[..., Any]
    ) -> bool:
        return await self.permission_checker(auth_result.auth_result)


def make_bearer_auth_backend(
    *,
    token_model: type[TokenT],
    token_decoder: Callable[[str], dict[str, Any]],
) -> type[BearerAuthentication[TokenT]]:

    class _Backend(BearerAuthentication[TokenT]):
        pass

    _Backend.token_model = token_model
    _Backend.decode_token = staticmethod(token_decoder)
    _Backend.name = f"BearerAuth_{token_model.__name__}"

    return _Backend


def make_permission_backend(
    *,
    token_model: type[TokenT],
    permission_checker: Callable[[TokenT, HttpRequest], bool],
) -> type[BearerPermission[TokenT]]:

    class _Permission(BearerPermission[TokenT]):
        pass

    _Permission.token_model = token_model
    _Permission.permission_checker = staticmethod(permission_checker)
    _Permission.name = f"Permission_{token_model.__name__}"

    return _Permission


def make_async_bearer_auth_backend(
    *,
    token_model: type[TokenT],
    token_decoder: Awaitable[Callable[[str], dict[str, Any]]],
) -> type[AsyncBearerAuthentication[TokenT]]:
    class _Backend(AsyncBearerAuthentication[TokenT]):
        pass

    _Backend.token_model = token_model
    _Backend.decode_token = staticmethod(token_decoder)
    _Backend.name = f"BearerAuth_{token_model.__name__}"

    return _Backend


def make_async_permission_backend(
    *,
    token_model: type[TokenT],
    permission_checker: AsyncPermissionChecker,
) -> type[AsyncBearerPermission[TokenT]]:
    class _Permission(AsyncBearerPermission[TokenT]):
        pass

    _Permission.token_model = token_model
    _Permission.permission_checker = staticmethod(permission_checker)
    _Permission.name = f"Permission_{token_model.__name__}"

    return _Permission
