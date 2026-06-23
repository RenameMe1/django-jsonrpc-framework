import pytest
from typing import Any

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType, AuthResult, run_auth, ANONYMOUS_AUTH, INVALID_AUTH
from jsonrpc_framework.controller.decor import jsonrpc_method

from django.http import HttpRequest, request
from .conftest import BearerAuth, BearerToken, AdminPermission, AsyncBearerAuth, AsyncAdminPermission

pytestmark = pytest.mark.asyncio


async def test_auth_runtime() -> None:

    class TestController(BaseController):
        default_access = AccessType.PUBLIC

        def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]
    access_policy = controller._resolve_method_access(handler)


    auth_result = await run_auth(access_policy, HttpRequest())

    assert auth_result is ANONYMOUS_AUTH


async def test_auth_without_credentials() -> None:

    class TestController(BaseController):

        auth_backends = [BearerAuth]

        @jsonrpc_method(access=AccessType.PUBLIC)
        def public(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    request = HttpRequest()

    public_access_policy = controller._resolve_method_access(controller.registry["public"])
    optional_access_policy = controller._resolve_method_access(controller.registry["optional"])
    private_access_policy = controller._resolve_method_access(controller.registry["private"])

    auth_result = await run_auth(public_access_policy, request)
    assert auth_result is ANONYMOUS_AUTH

    auth_result = await run_auth(optional_access_policy, request)
    assert auth_result is ANONYMOUS_AUTH

    auth_result = await run_auth(private_access_policy, request)
    assert auth_result is INVALID_AUTH


async def test_auth_with_correct_credentials(
    admin_bearer_token: str,
) -> None:

    class TestController(BaseController):

        auth_backends = [BearerAuth]

        @jsonrpc_method(access=AccessType.PUBLIC)
        def public(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    request = HttpRequest()
    request.META.update({"HTTP_AUTHORIZATION": f"Bearer {admin_bearer_token}"})

    public_access_policy = controller._resolve_method_access(controller.registry["public"])
    optional_access_policy = controller._resolve_method_access(controller.registry["optional"])
    private_access_policy = controller._resolve_method_access(controller.registry["private"])

    auth_result = await run_auth(public_access_policy, request)
    assert auth_result == ANONYMOUS_AUTH

    auth_result = await run_auth(optional_access_policy, request)
    assert auth_result == AuthResult(
        auth_result=BearerToken(sub="test", admin=True, exp=auth_result.auth_result.exp),
        credentials_present=True,
        backend_used="BearerAuth_BearerToken",
    )

    auth_result = await run_auth(private_access_policy, request)
    assert auth_result == AuthResult(
        auth_result=BearerToken(sub="test", admin=True, exp=auth_result.auth_result.exp),
        credentials_present=True,
        backend_used="BearerAuth_BearerToken",
    )



async def test_async_auth_runtime(
    admin_bearer_token: str,
) -> None:
    class TestController(BaseController):

        default_access = AccessType.PRIVATE
        auth_backends = [AsyncBearerAuth]

        async def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]
    access_policy = controller._resolve_method_access(handler)

    request = HttpRequest()
    request.META.update({"HTTP_AUTHORIZATION": f"Bearer {admin_bearer_token}"})

    auth_result = await run_auth(access_policy, request)

    assert auth_result == AuthResult(
        auth_result=BearerToken(sub="test", admin=True, exp=auth_result.auth_result.exp),
        credentials_present=True,
        backend_used="BearerAuth_BearerToken",
    )