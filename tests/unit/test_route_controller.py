import pytest

from jsonrpc_framework.controller import BaseController, RouteController



def test_route_controller() -> None:
    class TestController(BaseController):
        def method_other(self) -> str:
            return "other"

    class TestController2(BaseController):
        def method_another(self) -> str:
            return "another"

    route_controller = RouteController(
        path="jsonrpc",
        controllers=[TestController, TestController2],
    )

    assert route_controller.registry.keys() == {"other", "another"}
    assert route_controller.registry["other"]() == "other"
    assert route_controller.registry["another"]() == "another"


def test_route_controller_with_conflict() -> None:
    class TestController(BaseController):
        def method_other(self) -> str:
            return "other"

    class TestController2(BaseController):
        def method_other(self) -> str:
            return "other"

    with pytest.raises(ValueError):
        RouteController(
            path="jsonrpc",
            controllers=[TestController, TestController2],
        )


def test_route_controller_with_invalid_controller() -> None:
    class InvalidController:
        def method_other(self) -> str:
            return "other"

    class TestController(BaseController):
        def method_other(self) -> str:
            return "other"

    with pytest.raises(TypeError):
        RouteController(
            path="jsonrpc",
            controllers=[TestController, InvalidController],
        )
