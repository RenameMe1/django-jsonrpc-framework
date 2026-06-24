from collections.abc import Callable
from inspect import BoundArguments
import inspect
from typing import Any
import logging

from django.http import HttpRequest

from jsonrpc_framework.core.models import MethodType, ParamType
from jsonrpc_framework.logic.validator import RequestType, BatchType
from jsonrpc_framework.core.error import (
    RpcError,
    InternalError,
    MethodNotFoundError,
    InvalidParamsError,
    UnauthorizedError,
    ForbiddenError,
)
from jsonrpc_framework.core.models import SuccessResponse, ErrorResponse
from jsonrpc_framework.core.models import Request, Notification
from jsonrpc_framework.controller.auth import (
    AccessPolicy,
    run_auth,
    run_permissions,
    ANONYMOUS_AUTH,
)


type ResponseType = SuccessResponse | ErrorResponse | None
type BatchResponseType = list[SuccessResponse | ErrorResponse]
type HandlerType = Callable[..., Any]

logger = logging.getLogger("django.server")


class RpcDispatcher:
    resolve_method_access: Callable[[Callable[..., Any]], AccessPolicy]

    def __init__(
        self, resolve_method_access: Callable[[Callable[..., Any]], AccessPolicy]
    ):
        self.resolve_method_access = resolve_method_access

    async def dispatch(
        self,
        body: RequestType | BatchType | RpcError,
        registry: dict[MethodType, HandlerType],
        http_request: HttpRequest,
    ) -> ResponseType | BatchResponseType:
        """Public method to dispatch a request.

        Args:
            body: A request item.
            registry: A collector of methods.
        """
        if isinstance(body, Request | Notification):
            return await self._dispatch_single(body, registry, http_request)
        elif isinstance(body, list):
            return await self._dispatch_batch(body, registry, http_request)
        elif isinstance(body, RpcError):
            return ErrorResponse(id=None, error=body)

    async def _dispatch_single(
        self,
        request: RequestType,
        registry: dict[MethodType, HandlerType],
        http_request: HttpRequest,
    ) -> ResponseType:
        """Dispatch a single request."""

        params = request.params
        method = request.method
        result = None

        handler, bound = self._get_handler(method, params, registry)

        if isinstance(handler, RpcError):
            if isinstance(request, Request):
                return ErrorResponse(id=request.id, error=handler)
            else:
                return None

        access_policy = self.resolve_method_access(handler)
        auth_result = await run_auth(access_policy, http_request)

        if auth_result is None:
            result = UnauthorizedError(
                    data=f"Method {request.method} is private and credentials are incorrect or not present"
                )

        if auth_result != ANONYMOUS_AUTH and auth_result is not None:
            if not await run_permissions(
                access_policy, http_request, auth_result,
            ):
                result = ForbiddenError(
                    data=f"Forbidden access to method {request.method}"
                )

        if result is None:
            result = await self._call_handler(handler, bound)

        if isinstance(request, Request):
            if isinstance(result, RpcError):
                id = None if isinstance(request, Notification) else request.id
                return ErrorResponse(id=id, error=result)
            return SuccessResponse(id=request.id, result=result)
        else:
            return None

    def _get_handler(
        self,
        method: MethodType,
        params: ParamType,
        registry: dict[MethodType, HandlerType],
    ) -> tuple[HandlerType | RpcError, BoundArguments | None]:
        """Get a handler from registry and bind params."""

        bound = None

        try:
            handler = registry[method]
        except KeyError:
            return MethodNotFoundError(data=f"Method {method} not found"), bound

        sig = inspect.signature(handler)

        try:
            if params is None:
                bound = sig.bind()
            elif isinstance(params, list):
                bound = sig.bind(*params)
            elif isinstance(params, dict):
                bound = sig.bind(**params)
        except TypeError as e:
            return InvalidParamsError(data=str(e)), bound

        bound.apply_defaults()

        return handler, bound

    async def _call_handler(
        self,
        handler: HandlerType,
        bound: BoundArguments | None,
    ) -> Any | RpcError:
        try:
            if bound is None:
                result = handler()
            else:
                result = handler(*bound.args, **bound.kwargs)

            if inspect.isawaitable(result):
                result = await result

        except Exception as e:
            logger.exception(e)
            result = InternalError()

        return result

    async def _dispatch_batch(
        self,
        requests: BatchType,
        registry: dict[MethodType, HandlerType],
        http_request: HttpRequest,
    ) -> BatchResponseType:
        batch_response: BatchResponseType = []

        for request in requests:
            if isinstance(request, RpcError):
                batch_response.append(ErrorResponse(id=None, error=request))
                continue
            else:
                result = await self._dispatch_single(request, registry, http_request)

                if result is not None:
                    batch_response.append(result)

        return batch_response
