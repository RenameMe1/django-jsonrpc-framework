import pytest

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType, BaseAuthentication, BasePermission
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.core.models import Request
from django.http import HttpRequest
from jsonrpc_framework.core.error import UnauthorizedError, ForbiddenError
from jsonrpc_framework.core.models import ErrorResponse, SuccessResponse

from .conftest import BearerAuth, AdminPermission

pytestmark = pytest.mark.asyncio


async def test_dispatcher_access_invalid_credentials(
    invalid_bearer_token: str,
) -> None:
    class TestController(BaseController):

        default_access = AccessType.PRIVATE
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    http_request = HttpRequest()
    http_request.path = "/jsonrpc"
    http_request.META.update({"HTTP_AUTHORIZATION": f"Bearer {invalid_bearer_token}"})

    optional_request = Request(id=1, method="optional")
    private_request = Request(id=1, method="private")

    optional_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=optional_request,
        registry=controller.registry,
    )

    assert optional_response.id == 1
    assert isinstance(optional_response, ErrorResponse)
    assert optional_response.error.code == UnauthorizedError().code
    assert optional_response.error.message == UnauthorizedError().message

    private_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=private_request,
        registry=controller.registry,
    )

    assert private_response.id == 1
    assert isinstance(private_response, ErrorResponse)
    assert private_response.error.code == UnauthorizedError().code
    assert private_response.error.message == UnauthorizedError().message



async def test_dispatcher_access_valid_credentials(
    admin_bearer_token: str,
) -> None:
    class TestController(BaseController):

        default_access = AccessType.PRIVATE
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    http_request = HttpRequest()
    http_request.path = "/jsonrpc"
    http_request.META.update({"HTTP_AUTHORIZATION": f"Bearer {admin_bearer_token}"})

    optional_request = Request(id=1, method="optional")
    private_request = Request(id=1, method="private")

    optional_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=optional_request,
        registry=controller.registry,
    )

    assert optional_response.id == 1
    assert isinstance(optional_response, SuccessResponse)
    assert optional_response.result == "test"

    private_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=private_request,
        registry=controller.registry,
    )

    assert private_response.id == 1
    assert isinstance(private_response, SuccessResponse)
    assert private_response.result == "test"


async def test_dispatcher_access_without_credentials() -> None:
    class TestController(BaseController):

        default_access = AccessType.PRIVATE
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    http_request = HttpRequest()
    http_request.path = "/jsonrpc"

    optional_request = Request(id=1, method="optional")
    private_request = Request(id=1, method="private")

    optional_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=optional_request,
        registry=controller.registry,
    )

    assert optional_response.id == 1
    assert isinstance(optional_response, SuccessResponse)
    assert optional_response.result == "test"

    private_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=private_request,
        registry=controller.registry,
    )

    assert private_response.id == 1
    assert isinstance(private_response, ErrorResponse)
    assert private_response.error.code == UnauthorizedError().code
    assert private_response.error.message == UnauthorizedError().message


async def test_dispatcher_access_with_permissions(
    user_bearer_token: str,
) -> None:
    class TestController(BaseController):

        default_access = AccessType.PRIVATE
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "test"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "test"

    controller = TestController()
    http_request = HttpRequest()
    http_request.path = "/jsonrpc"
    http_request.META.update({"HTTP_AUTHORIZATION": f"Bearer {user_bearer_token}"})

    private_request = Request(id=1, method="private")
    optional_request = Request(id=1, method="optional")

    optional_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=optional_request,
        registry=controller.registry,
    )

    assert optional_response.id == 1
    assert isinstance(optional_response, ErrorResponse)
    assert optional_response.error.code == ForbiddenError().code
    assert optional_response.error.message == ForbiddenError().message

    private_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=private_request,
        registry=controller.registry,
    )

    assert private_response.id == 1
    assert isinstance(private_response, ErrorResponse)
    assert private_response.error.code == ForbiddenError().code
    assert private_response.error.message == ForbiddenError().message