import logging
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views import View

from jsonrpc_framework.core.error import RpcError
from jsonrpc_framework.core.models import MethodType
from jsonrpc_framework.logic.dispatcher import RpcDispatcher
from jsonrpc_framework.logic.responser import ResponseBuilder
from jsonrpc_framework.logic.validator import (
    BatchType,
    RequestType,
    RequestValidator,
)

logger = logging.getLogger("django.server")


class BaseController(View):
    http_method_names = ["post"]
    path: str = "jsonrpc"

    registry: dict[MethodType, Callable[..., Any]]

    dispatcher: RpcDispatcher
    validator: RequestValidator
    response_builder: ResponseBuilder

    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)

        self.registry = self._collect_declared_methods()

        self.dispatcher = RpcDispatcher()
        self.validator = RequestValidator()
        self.response_builder = ResponseBuilder()

    def _collect_declared_methods(self) -> dict[MethodType, Callable[..., Any]]:
        registry: dict[MethodType, Callable[..., Any]] = {}

        for name, value in vars(self.__class__).items():
            if not callable(value):
                continue

            rpc_name = getattr(value, "__rpc_method_name__", None)

            if rpc_name is not None:
                method_name = rpc_name
            elif name.startswith("method_"):
                method_name = name.replace("method_", "")
            else:
                continue

            if method_name in registry:
                raise ValueError(
                    f"Method {method_name} already registered in {self.__class__.__name__}"
                )

            registry[method_name] = getattr(self, name)

        return registry

    async def post(
        self,
        request: HttpRequest,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        body = self.validator.validate_body(request.body)

        result = await self.dispatcher.dispatch(body, registry=self.registry)
        self._log_jsonrpc_methods(request, body)

        return self.response_builder.build_response(result)

    def _log_jsonrpc_methods(
        self,
        request: HttpRequest,
        body: RequestType | BatchType | RpcError,
    ) -> None:
        methods = self._extract_method_names(body)

        if methods:
            logger.info(f"JSONRPC {request.path} {methods}")

    def _extract_method_names(
        self,
        body: RequestType | BatchType | RpcError,
    ) -> list[str] | str:
        if isinstance(body, RpcError):
            return []

        if isinstance(body, list):
            methods: list[str] = []

            for item in body:
                if isinstance(item, RpcError):
                    continue
                methods.append(item.method)
            return methods

        return body.method
