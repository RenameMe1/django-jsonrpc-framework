import pytest

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.controller.auth import AccessType, BaseAuthentication, BasePermission

def test_method_metadata() -> None:
    """Test method metadata."""

    class TestController(BaseController):
        @jsonrpc_method(
            "test",
            access=AccessType.PRIVATE,
            auth=[BaseAuthentication],
            permissions=[BasePermission],
        )
        def test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]

    assert getattr(handler, "__rpc_method_access__", None) == AccessType.PRIVATE
    assert getattr(handler, "__rpc_method_auth__", None) == [BaseAuthentication]
    assert getattr(handler, "__rpc_method_permissions__", None) == [BasePermission]


def test_worng_access_type() -> None:
    """Test wrong access type."""

    with pytest.raises(ValueError):
        class TestController(BaseController):
            @jsonrpc_method(
                "test",
                access="wrong",
            )
            def test(self) -> str:
                return "test"

def test_not_set_access_type() -> None:
    """Test resolve default access."""

    class TestController(BaseController):
        def method_test(self) -> str:
            return "test"

    controller = TestController()
    handler = controller.registry["test"]

    assert getattr(handler, "__rpc_method_access__", None) == AccessType._NOT_SET