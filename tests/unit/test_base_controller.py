import pytest

from jsonrpc_framework.controller._base import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.controller.auth import AccessType


def test_collect_declared_methods() -> None:
    """Test default method names collection."""

    class TestController(BaseController):
        def method_other(self) -> str:
            return "other"

        def method_another(self) -> str:
            return "another"

    controller = TestController()

    assert controller.registry == {
        "other": controller.method_other,
        "another": controller.method_another,
    }


def test_decorator_method() -> None:
    """Test method names collection with decorator."""

    class TestController(BaseController):
        @jsonrpc_method
        def method_other(self) -> str:
            return "other"

        @jsonrpc_method
        def my_another(self) -> str:
            return "another"

    controller = TestController()

    assert controller.registry == {
        "method_other": controller.method_other,
        "my_another": controller.my_another,
    }


def test_change_alias_method() -> None:
    """Test changing method alias."""

    class TestController(BaseController):
        @jsonrpc_method("first")
        def method_other(self) -> str:
            return "first"

        @jsonrpc_method("second")
        def another(self) -> str:
            return "second"

    controller = TestController()
    assert controller.registry == {
        "first": controller.method_other,
        "second": controller.another,
    }


def test_name_conflict() -> None:
    """Test raising error on name conflict."""

    class TestController(BaseController):
        def method_other(self) -> str:
            return "other1"

        @jsonrpc_method("other")
        def another_other(self) -> str:
            return "other2"

    with pytest.raises(ValueError):
        TestController()


def test_decorator_openrpc_metadata() -> None:
    """Test summary/description metadata with decorator alias."""

    class TestController(BaseController):
        @jsonrpc_method(
            "sum",
            summary="Sum two numbers",
            description="Calculates the sum for provided arguments.",
        )
        def method_sum(self, a: int, b: int) -> int:
            return a + b

    controller = TestController()
    handler = controller.registry["sum"]

    assert getattr(handler, "__rpc_method_name__", None) == "sum"
    assert getattr(handler, "__rpc_method_summary__", None) == "Sum two numbers"
    assert getattr(handler, "__rpc_method_description__", None) == (
        "Calculates the sum for provided arguments."
    )
    assert getattr(handler, "__rpc_method_access__", None) == AccessType._NOT_SET
    assert getattr(handler, "__rpc_method_tags__", None) is None
    assert getattr(handler, "__rpc_method_auth__", None) is None
    assert getattr(handler, "__rpc_method_permissions__", None) is None


def test_decorator_openrpc_metadata_without_alias() -> None:
    """Test summary/description metadata without explicit alias."""

    class TestController(BaseController):
        @jsonrpc_method(
            summary="Echo value",
            description="Returns provided value without modifications.",
        )
        def echo(self, value: str) -> str:
            return value

    controller = TestController()
    handler = controller.registry["echo"]

    assert getattr(handler, "__rpc_method_name__", None) == "echo"
    assert getattr(handler, "__rpc_method_summary__", None) == "Echo value"
    assert getattr(handler, "__rpc_method_description__", None) == (
        "Returns provided value without modifications."
    )
    assert getattr(handler, "__rpc_method_access__", None) == AccessType._NOT_SET
    assert getattr(handler, "__rpc_method_tags__", None) is None
    assert getattr(handler, "__rpc_method_auth__", None) is None
    assert getattr(handler, "__rpc_method_permissions__", None) is None


def test_unexpected_access_type() -> None:
    """Test raising error on unexpected access type."""

    with pytest.raises(ValueError):

        class TestController(BaseController):
            @jsonrpc_method(access="public")
            def method_other(self) -> str:
                return "other"
