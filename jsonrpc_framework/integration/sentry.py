from __future__ import annotations

import logging
from typing import Any
import inspect

import sentry_sdk
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.utils import capture_internal_exceptions, ensure_integration_enabled

from jsonrpc_framework.logic.dispatcher import RpcDispatcher

logger = logging.getLogger("django.server")

class JsonRpcIntegration(Integration):
    identifier = "jsonrpc"
    origin = "auto.rpc.jsonrpc"

    def __init__(
        self,
        *,
        capture_internal_errors: bool = True,
        set_transaction_name: bool = True,
        mechanism_handled: bool = True,
    ) -> None:
        self.capture_internal_errors = capture_internal_errors
        self.set_transaction_name = set_transaction_name
        self.mechanism_handled = mechanism_handled

    @staticmethod
    def setup_once() -> None:
        _patch_dispatch_single(RpcDispatcher)
        _patch_call_handler(RpcDispatcher)


def _patch_dispatch_single(RpcDispatcher: type) -> None:
    old = RpcDispatcher._dispatch_single

    @ensure_integration_enabled(JsonRpcIntegration, old)
    async def patched(
        self: Any,
        request: Any,
        registry: Any,
        http_request: Any,
    ) -> Any:
        integration = sentry_sdk.get_client().get_integration(JsonRpcIntegration)
        method = request.method
        scope = sentry_sdk.get_current_scope()

        if integration and integration.set_transaction_name:
            scope.set_transaction_name(
                f"jsonrpc.{method}",
                source="custom",
            )

        scope.set_tag("jsonrpc.method", method)

        if request.id is not None:
            scope.set_tag("jsonrpc.id", str(request.id))

        with sentry_sdk.start_span(
            op="rpc.server",
            name=method,
            origin=JsonRpcIntegration.origin,
        ):
            return await old(self, request, registry, http_request)

    RpcDispatcher._dispatch_single = patched 


def _patch_call_handler(RpcDispatcher: type) -> None:
    old = RpcDispatcher._call_handler
    @ensure_integration_enabled(JsonRpcIntegration, old)
    async def patched(
        self: Any,
        handler: Any,
        bound: Any,
    ) -> Any:
        try:
            return await old(self, handler, bound)
        except Exception:
            raise

    @ensure_integration_enabled(JsonRpcIntegration, old)
    async def patched_call_handler(
        self: Any,
        handler: Any,
        bound: Any,
    ) -> Any:
        try:
            if bound is None:
                result = handler()
            else:
                result = handler(*bound.args, **bound.kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            integration = sentry_sdk.get_client().get_integration(JsonRpcIntegration)
            if integration and integration.capture_internal_errors:
                with capture_internal_exceptions():
                    sentry_sdk.capture_exception(
                        exc,
                        hint={
                            "mechanism": {
                                "type": "jsonrpc",
                                "handled": integration.mechanism_handled,
                            }
                        },
                    )
            logger.exception(exc)
            from jsonrpc_framework.core.error import InternalError
            return InternalError()

    RpcDispatcher._call_handler = patched_call_handler