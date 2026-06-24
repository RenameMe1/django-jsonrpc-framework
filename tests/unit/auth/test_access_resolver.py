from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.auth import (
    AccessType,
    BaseAuthentication,
    BasePermission,
)
from jsonrpc_framework.controller.decor import jsonrpc_method


def test_resolve_default_access() -> None:

    class TestController(BaseController):
        default_access = AccessType.PRIVATE
        auth_backends = [BaseAuthentication]
        permission_backends = [BasePermission]

        def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]

    access_policy = controller._resolve_method_access(handler)

    assert access_policy.access == controller.default_access
    assert access_policy.auth == controller.auth_backends
    assert access_policy.permissions == controller.permission_backends


def test_explicit_access_type_and_auth_and_permissions() -> None:

    class TestController(BaseController):
        default_access = AccessType.PRIVATE
        auth_backends = []
        permission_backends = []

        @jsonrpc_method(
            "test",
            access=AccessType.OPTIONAL,
            auth=[BaseAuthentication],
            permissions=[BasePermission],
        )
        def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]
    access_policy = controller._resolve_method_access(handler)

    assert access_policy.access == AccessType.OPTIONAL
    assert access_policy.auth == [BaseAuthentication]
    assert access_policy.permissions == [BasePermission]


def test_default_auth_and_permissions() -> None:
    """Test default auth and permissions."""

    class TestController(BaseController):
        default_access = AccessType.PRIVATE
        auth_backends = [BaseAuthentication]
        permission_backends = [BasePermission]

        @jsonrpc_method(
            "test",
            access=AccessType.OPTIONAL,
        )
        def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]
    access_policy = controller._resolve_method_access(handler)

    assert access_policy.access == AccessType.OPTIONAL
    assert access_policy.auth == controller.auth_backends
    assert access_policy.permissions == controller.permission_backends
