import pytest
from typing import Any
import time
import secrets

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType, run_auth, ANONYMOUS_AUTH
from jsonrpc_framework.controller.auth.bearer import make_bearer_auth_backend, make_permission_backend

from django.http import HttpRequest
import jwt
from pydantic import BaseModel

pytestmark = pytest.mark.asyncio

test_secret = secrets.token_hex(32)

class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float

def jwt_decode(token: str) -> dict[str, Any]:
    return jwt.decode(token, key=test_secret, algorithms=["HS256"])

BearerAuth = make_bearer_auth_backend(
    token_model=BearerToken,
    token_decoder=jwt_decode,
)

AdminPermission = make_permission_backend(
    token_model=BearerToken,
    permission_checker=lambda token: token.admin is True,
)

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
        "secret",
        algorithm="HS256",
    )