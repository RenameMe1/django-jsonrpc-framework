from typing import Generic, TypeVar, Any, ClassVar, Protocol

from jwt import algorithms
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
    def __call__(
        self, auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy
    ) -> Awaitable[bool]: ...


class PermissionCheckerType(Protocol):
    def __call__(
        self, auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy
    ) -> bool: ...


class TokenValidatorType(Protocol):
    def __call__(self, token: str) -> True: ...


class AsyncTokenValidatorType(Protocol):
    def __call__(self, token: TokenT) -> Awaitable[bool]: ...


class BearerAuthentication(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    is_valid_token: ClassVar[TokenValidatorType]
    name: ClassVar[str]

    algorithms: ClassVar[list[str]]
    key: ClassVar[str]

    def __init__(
        self,
        token_model: type[TokenT],
        algorithms: list[str],
        key: str,
        is_valid_token: TokenValidatorType,
    ) -> None:
        self.token_model = token_model
        self.algorithms = algorithms
        self.key = key
        self.is_valid_token = is_valid_token

    def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    def authenticate(self, request: HttpRequest) -> AuthResult | None:
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token is None:
            return INVALID_AUTH

        try:
            payload = jwt.decode(token, key=self.key, algorithms=self.algorithms)
        except jwt.InvalidTokenError:
            return INVALID_AUTH

        if payload is None:
            return INVALID_AUTH

        try:
            token_data = self.token_model.model_validate(payload)
        except ValidationError:
            return INVALID_AUTH

        if not self.is_valid_token(token_data):
            return INVALID_AUTH

        return AuthResult(
            auth_result=token_data,
            credentials_present=True,
            backend_used=self,
        )


class AsyncBearerAuthentication(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    is_valid_token: ClassVar[AsyncTokenValidatorType]
    name: ClassVar[str]

    algorithms: ClassVar[list[str]]
    key: ClassVar[str]

    def __init__(
        self,
        token_model: type[TokenT],
        algorithms: list[str],
        key: str,
        is_valid_token: AsyncTokenValidatorType,
    ) -> None:
        self.token_model = token_model
        self.algorithms = algorithms
        self.key = key
        self.is_valid_token = is_valid_token

    async def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        print("asdasdasdasdsadasds")
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token is None:
            return INVALID_AUTH

        try:
            payload = jwt.decode(token, key=self.key, algorithms=self.algorithms)
        except jwt.InvalidTokenError:
            return INVALID_AUTH

        if payload is None:
            return INVALID_AUTH

        try:
            token_data = self.token_model.model_validate(payload)
        except ValidationError:
            return INVALID_AUTH

        if not await self.is_valid_token(token_data):
            return INVALID_AUTH

        return AuthResult(
            auth_result=token_data,
            credentials_present=True,
            backend_used=self,
        )


class BearerPermission(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    permission_checker: ClassVar[PermissionCheckerType]
    name: ClassVar[str]

    def __init__(
        self, token_model: type[TokenT], permission_checker: PermissionCheckerType
    ) -> None:
        self.token_model = token_model
        self.permission_checker = permission_checker

    def has_permission(
        self, access_policy: AccessPolicy, request: HttpRequest, auth_result: AuthResult
    ) -> bool:
        return self.permission_checker(auth_result, request, access_policy)


class AsyncBearerPermission(Generic[TokenT]):
    token_model: ClassVar[type[TokenT]]
    permission_checker: ClassVar[AsyncPermissionCheckerType]
    name: ClassVar[str]

    def __init__(
        self, token_model: type[TokenT], permission_checker: AsyncPermissionCheckerType
    ) -> None:
        self.token_model = token_model
        self.permission_checker = permission_checker

    async def has_permission(
        self, access_policy: AccessPolicy, request: HttpRequest, auth_result: AuthResult
    ) -> bool:
        return await self.permission_checker(auth_result, request, access_policy)
