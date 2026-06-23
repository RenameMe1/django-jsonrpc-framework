import pytest
from typing import Any
import time
import secrets
from typing import Generic, Callable, TypeVar, Awaitable
import asyncio

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType, run_auth, ANONYMOUS_AUTH, AuthResult, INVALID_AUTH
from jsonrpc_framework.controller.auth.bearer import make_bearer_auth_backend, make_permission_backend, make_async_bearer_auth_backend, make_async_permission_backend

from django.http import HttpRequest
import jwt
from pydantic import BaseModel, ValidationError

TokenT = TypeVar("TokenT", bound=BaseModel)
test_secret = secrets.token_hex(32)

class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float

def jwt_decode(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, key=test_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None

BearerAuth = make_bearer_auth_backend(
    token_model=BearerToken,
    token_decoder=jwt_decode,
)

def permission_checker(token: BearerToken) -> bool:
    return token.admin is True

AdminPermission = make_permission_backend(
    token_model=BearerToken,
    permission_checker=permission_checker,
)

@pytest.fixture
def invalid_bearer_token() -> str:
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"

@pytest.fixture
def admin_bearer_token() -> str:
    return jwt.encode(
        {
            "sub": "test",
            "admin": True,
            "exp": time.time() + 3600,
        },
        key=test_secret,
        algorithm="HS256",
    )

@pytest.fixture
def user_bearer_token() -> str:
    return jwt.encode(
        {
            "sub": "test",
            "admin": False,
            "exp": time.time() + 3600,
        },
        key=test_secret,
        algorithm="HS256",
    )

class AsyncBearerAuthentication(Generic[TokenT]):
    token_model: type[TokenT]
    decode_token: Callable[[str], dict[str, Any]]
    name: str

    async def has_credentials(self, request: HttpRequest) -> bool:
        return request.headers.get("Authorization", "").startswith("Bearer ")

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token is None:
            return INVALID_AUTH

        payload = await self.decode_token(token)

        if payload is None:
            return INVALID_AUTH

        try:
            token_data = self.token_model.model_validate(payload)
        except ValidationError as e:
            return INVALID_AUTH

        return AuthResult(
            auth_result=token_data,
            credentials_present=True,
            backend_used=self.name,
        )


class AsyncBearerPermission(Generic[TokenT]):
    token_model: type[TokenT]
    permission_checker: Callable[[TokenT, HttpRequest], bool]
    name: str

    async def has_permission(self, request: HttpRequest, auth_result: AuthResult, handler: Callable[..., Any]) -> bool:
        return await self.permission_checker(auth_result.auth_result, request)


async def async_jwt_decode(token: str) -> dict[str, Any]:
    return jwt.decode(token, key=test_secret, algorithms=["HS256"])

async def async_permission_checker(token: TokenT, request: HttpRequest) -> bool:
    return token.admin is True


AsyncBearerAuth = make_async_bearer_auth_backend(
    token_model=BearerToken,
    token_decoder=async_jwt_decode,
)

AsyncAdminPermission = make_async_permission_backend(
    token_model=BearerToken,
    permission_checker=async_permission_checker,
)
