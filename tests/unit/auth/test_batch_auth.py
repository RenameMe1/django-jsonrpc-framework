import pytest

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.core.models import Request
from django.http import HttpRequest
from jsonrpc_framework.controller.decor import jsonrpc_method
from .conftest import BearerAuth, AdminPermission
from jsonrpc_framework.core.models import ErrorResponse, SuccessResponse
from jsonrpc_framework.core.error import ForbiddenError

pytestmark = pytest.mark.asyncio


async def test_batch_auth(
    user_bearer_token: str,
) -> None:
    class TestController(BaseController):
        default_access = AccessType.PRIVATE
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

        @jsonrpc_method(access=AccessType.PUBLIC)
        def public(self) -> str:
            return "public"

        @jsonrpc_method(access=AccessType.OPTIONAL)
        def optional(self) -> str:
            return "optional"

        @jsonrpc_method(access=AccessType.PRIVATE)
        def private(self) -> str:
            return "private"

    controller = TestController()
    http_request = HttpRequest()
    http_request.path = "/jsonrpc"
    http_request.META.update({"HTTP_AUTHORIZATION": f"Bearer {user_bearer_token}"})

    public_request = Request(id=1, method="public")
    optional_request = Request(id=1, method="optional")
    private_request = Request(id=1, method="private")

    batch_response = await controller.dispatcher.dispatch(
        http_request=http_request,
        body=[public_request, optional_request, private_request],
        registry=controller.registry,
    )

    assert batch_response[0].id == 1
    assert isinstance(batch_response[0], SuccessResponse)
    assert batch_response[0].result == "public"

    assert batch_response[1].id == 1
    assert isinstance(batch_response[1], ErrorResponse)
    assert batch_response[1].error.code == ForbiddenError().code
    assert batch_response[1].error.message == ForbiddenError().message

    assert batch_response[2].id == 1
    assert isinstance(batch_response[2], ErrorResponse)
    assert batch_response[2].error.code == ForbiddenError().code
    assert batch_response[2].error.message == ForbiddenError().message
