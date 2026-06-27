import pytest
from typing import Any
import time
import secrets
from typing import TypeVar

from jsonrpc_framework.controller.auth.bearer import (
    make_bearer_auth_backend,
    make_permission_backend,
    make_async_bearer_auth_backend,
    make_async_permission_backend,
)

from django.http import HttpRequest
import jwt
from pydantic import BaseModel

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


def permission_checker(token: BearerToken, request: HttpRequest) -> bool:
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
