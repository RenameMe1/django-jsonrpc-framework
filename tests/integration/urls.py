from django.urls import path
from typing import Any

from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.core.error import ParseError, RpcError


class CutsomError(RpcError):
    code: int = -4000
    message: str = "Custom error"


class IntegrationController(BaseController):
    def method_test(self) -> str:
        return "test"

    def method_error(self, flag: bool = True) -> RpcError | str:
        if flag:
            return ParseError(data="Invalid request")
        return "test"

    def method_custom_error(self) -> CutsomError:
        return CutsomError(data="Custom error")

    def method_test_positional_params(self, *args: Any) -> str:
        return f"test_positional_params: {args}"

    def method_test_named_params(self, a: int, b: int, c: int) -> int:
        return a + b + c

    def method_sum(self, *args: int) -> int:
        if len(args) == 1:
            return args[0]

        return sum(args)


urlpatterns = [
    path("jsonrpc", IntegrationController.as_view()),
]
