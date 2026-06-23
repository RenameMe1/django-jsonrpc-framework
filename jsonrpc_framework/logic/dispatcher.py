import inspect
import logging
from collections.abc import Callable
from inspect import BoundArguments
from typing import Any

from jsonrpc_framework.core.error import (
    InternalError,
    InvalidParamsError,
    MethodNotFoundError,
    RpcError,
)
from jsonrpc_framework.core.models import (
    ErrorResponse,
    MethodType,
    Notification,
    ParamType,
    Request,
    SuccessResponse,
)
from jsonrpc_framework.logic.validator import BatchType, RequestType

type ResponseType = SuccessResponse | ErrorResponse | None
type BatchResponseType = list[SuccessResponse | ErrorResponse]
type HandlerType = Callable[..., Any]

logger = logging.getLogger("django.server")


class RpcDispatcher:
    async def dispatch(
        self,
        body: RequestType | BatchType | RpcError,
        registry: dict[MethodType, HandlerType],
    ) -> ResponseType | BatchResponseType:
        """Public method to dispatch a request.

        Args:
            body: A request item.
            registry: A collector of methods.
        """
        if isinstance(body, Request | Notification):
            return await self._dispatch_single(body, registry)
        elif isinstance(body, list):
            return await self._dispatch_batch(body, registry)
        elif isinstance(body, RpcError):
            return ErrorResponse(id=None, error=body)

    async def _dispatch_single(
        self,
        request: RequestType,
        registry: dict[MethodType, HandlerType],
    ) -> ResponseType:
        """Dispatch a single request."""

        params = request.params
        method = request.method

        handler, bound = self._get_handler(method, params, registry)

        if isinstance(handler, RpcError):
            if isinstance(request, Notification):
                return ErrorResponse(id=None, error=handler)
            else:
                return ErrorResponse(id=request.id, error=handler)

        result = await self._call_handler(handler, bound)

        if isinstance(result, RpcError):
            id = None if isinstance(request, Notification) else request.id
            return ErrorResponse(id=id, error=result)

        if isinstance(request, Request):
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
    ) -> BatchResponseType:
        batch_response: BatchResponseType = []

        for request in requests:
            if isinstance(request, RpcError):
                batch_response.append(ErrorResponse(id=None, error=request))
                continue
            else:
                result = await self._dispatch_single(request, registry)

                if result is not None:
                    batch_response.append(result)

        return batch_response
