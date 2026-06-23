import logging
from typing import Any
from collections.abc import Callable, Sequence

from django.views import View
from django.http import HttpRequest, HttpResponse

from jsonrpc_framework.logic.dispatcher import RpcDispatcher
from jsonrpc_framework.logic.validator import RequestValidator, RequestType, BatchType
from jsonrpc_framework.logic.responser import ResponseBuilder

from jsonrpc_framework.core.error import RpcError
from jsonrpc_framework.core.models import MethodType
from jsonrpc_framework.controller.auth import AccessType, BasePermission, BaseAuthentication, AccessPolicy


logger = logging.getLogger("django.server")


class BaseController(View):
    http_method_names = ["post"]
    path: str = "jsonrpc"

    # Access block
    default_access: AccessType = AccessType.PUBLIC
    permission_backends: Sequence[type[BasePermission]] | None = None
    auth_backends: Sequence[type[BaseAuthentication]] | None = None

    registry: dict[MethodType, Callable[..., Any]]

    dispatcher: RpcDispatcher
    validator: RequestValidator
    response_builder: ResponseBuilder

    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)

        if self.permission_backends is None:
            self.permission_backends = []
        if self.auth_backends is None:
            self.auth_backends = []

        self.registry = self._collect_declared_methods()

        self.dispatcher = RpcDispatcher(resolve_method_access=self._resolve_method_access)
        self.validator = RequestValidator()
        self.response_builder = ResponseBuilder()

    def _collect_declared_methods(self) -> dict[MethodType, Callable[..., Any]]:
        registry: dict[MethodType, Callable[..., Any]] = {}

        for func_name, value in vars(self.__class__).items():
            if not callable(value):
                continue

            rpc_name = getattr(value, "__rpc_method_name__", None)

            if rpc_name is not None:
                method_name = rpc_name
            elif func_name.startswith("method_"):
                method_name = func_name.replace("method_", "")
            else:
                continue

            if method_name in registry:
                raise ValueError(
                    f"Method {method_name} already registered in {self.__class__.__name__}"
                )

            registry[method_name] = getattr(self, func_name)

        return registry


    def _resolve_method_access(self, func: Callable[..., Any]) -> AccessPolicy:
        
        access = getattr(func, "__rpc_method_access__", None)
        auth = getattr(func, "__rpc_method_auth__", None)
        permissions = getattr(func, "__rpc_method_permissions__", None)

        if access is AccessType._NOT_SET:
            access = self.default_access

        if access is None:
            access = AccessType.PUBLIC
        if auth is None:
            auth = self.auth_backends
        if permissions is None:
            permissions = self.permission_backends

        return AccessPolicy(access=access, auth=auth, permissions=permissions)


    async def post(
        self,
        request: HttpRequest,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        body = self.validator.validate_body(request.body)

        result = await self.dispatcher.dispatch(body, registry=self.registry, http_request=request)
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
