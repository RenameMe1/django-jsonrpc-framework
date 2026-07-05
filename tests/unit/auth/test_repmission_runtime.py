from unittest.mock import MagicMock, patch

import pytest
from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.core.models import Request

from django.http import HttpRequest
from .conftest import BearerAuth, AdminPermission

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mocked_permission_backend(monkeypatch):
    with patch(
        "jsonrpc_framework.logic.dispatcher.run_permissions", autospec=True
    ) as mock_perm:
        mock_perm.return_value = True
        yield mock_perm


async def test_permission_runtime(
    admin_bearer_token: str,
    mocked_permission_backend: MagicMock,
) -> None:
    class TestController(BaseController):
        auth_backends = [BearerAuth]
        permission_backends = [AdminPermission]

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

    http_request = HttpRequest()
    http_request.path = "/jsonrpc"
    http_request.META.update(
        {"HTTP_AUTHORIZATION": f"Bearer {admin_bearer_token}"}
    )

    public_request = Request(id=1, method="public")
    optional_request = Request(id=1, method="optional")
    private_request = Request(id=1, method="private")

    await controller.dispatcher.dispatch(
        http_request=http_request,
        body=public_request,
        registry=controller.registry,
    )

    mocked_permission_backend.assert_not_called()
    mocked_permission_backend.reset_mock()

    await controller.dispatcher.dispatch(
        http_request=http_request,
        body=optional_request,
        registry=controller.registry,
    )

    mocked_permission_backend.assert_called_once()
    mocked_permission_backend.reset_mock()

    await controller.dispatcher.dispatch(
        http_request=http_request,
        body=private_request,
        registry=controller.registry,
    )

    mocked_permission_backend.assert_called_once()
