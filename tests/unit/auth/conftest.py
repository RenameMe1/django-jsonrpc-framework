import pytest
from typing import Any
import time
import secrets
from typing import TypeVar

from jsonrpc_framework.controller.auth.bearer import (
    BearerAuthentication,
    BearerPermission,
    AsyncBearerAuthentication,
    AsyncBearerPermission,
)
from jsonrpc_framework.controller.auth import AccessPolicy, AuthResult
from django.http import HttpRequest
import jwt
from pydantic import BaseModel

TokenT = TypeVar("TokenT", bound=BaseModel)
test_secret = secrets.token_hex(32)


class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float


def jwt_validator(token: BearerToken) -> bool:
    if token.exp < time.time():
        return False
    return True


BearerAuth = BearerAuthentication(
    token_model=BearerToken,
    key=test_secret,
    algorithms=["HS256"],
    is_valid_token=jwt_validator,
)


def permission_checker(auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy) -> bool:
    return auth_result.auth_result.admin is True


AdminPermission = BearerPermission(
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


async def async_jwt_validator(token: BearerToken) -> bool:
    if token.exp < time.time():
        return False
    return True


AsyncBearerAuth = AsyncBearerAuthentication(
    token_model=BearerToken,
    is_valid_token=async_jwt_validator,
    algorithms=["HS256"],
    key=test_secret,
)

async def async_permission_checker(auth_result: AuthResult, request: HttpRequest, access_policy: AccessPolicy) -> bool:
    return auth_result.auth_result.admin is True

AsyncAdminPermission = AsyncBearerPermission(
    token_model=BearerToken,
    permission_checker=async_permission_checker,
)
