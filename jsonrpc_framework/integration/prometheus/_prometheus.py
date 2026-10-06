from __future__ import annotations

from typing import TYPE_CHECKING, Any
import time

from jsonrpc_framework.logic.dispatcher import RpcDispatcher
from jsonrpc_framework.core.error import RpcError
from jsonrpc_framework.core.models import ErrorResponse
from django.views import View
from django.http import HttpResponse

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        REGISTRY,
        CollectorRegistry,
        Counter,
        Histogram,
        generate_latest,
    )
except ImportError:
    raise ImportError(
        "prometheus-client is not installed, please install it with "
        "`pip install django-jsonrpc-framework[prometheus]`"
    ) from None


if TYPE_CHECKING:
    from django.http import HttpRequest

    from jsonrpc_framework.logic.validator import BatchType, RequestType
    from jsonrpc_framework.core.models import MethodType
    from jsonrpc_framework.logic.dispatcher import (
        BatchResponseType,
        HandlerType,
        ResponseType,
    )

__all__ = ["enable_prometheus", "reset_prometheus", "MetricsView"]


_enabled: bool = False
_registry: CollectorRegistry | None = None
_original_dispatch_single = None
_original_dispatch = None


def enable_prometheus(*, registry: CollectorRegistry | None = None) -> None:
    global _enabled, _registry, _original_dispatch_single, _original_dispatch

    if _enabled:
        return

    if registry is None:
        registry = REGISTRY

    _registry = registry

    requests_total = Counter(
        "jsonrpc_requests_total",
        "Total JSON-RPC requests",
        labelnames=("method", "result"),
        registry=_registry,
    )
    request_duration = Histogram(
        "jsonrpc_request_duration_seconds",
        "JSON-RPC request duration in seconds",
        labelnames=("method",),
        registry=_registry,
    )
    errors_total = Counter(
        "jsonrpc_errors_total",
        "Total JSON-RPC errors",
        labelnames=("method", "code"),
        registry=_registry,
    )

    _original_dispatch_single = RpcDispatcher._dispatch_single
    _original_dispatch = RpcDispatcher.dispatch

    _patch_dispatch_single(
        RpcDispatcher,
        requests_total=requests_total,
        request_duration=request_duration,
        errors_total=errors_total,
    )
    _patch_dispatch(
        RpcDispatcher,
        requests_total=requests_total,
        request_duration=request_duration,
        errors_total=errors_total,
    )
    _enabled = True


def reset_prometheus() -> None:
    global _enabled, _registry
    global _original_dispatch_single, _original_dispatch

    if _original_dispatch_single is not None:
        setattr(RpcDispatcher, "_dispatch_single", _original_dispatch_single)
    if _original_dispatch is not None:
        setattr(RpcDispatcher, "dispatch", _original_dispatch)

    _original_dispatch_single = None
    _original_dispatch = None
    _registry = None
    _enabled = False


def _patch_dispatch_single(
    dispatcher: type[RpcDispatcher],
    *,
    requests_total: Counter,
    request_duration: Histogram,
    errors_total: Counter,
) -> None:
    old = dispatcher._dispatch_single

    async def patched(
        self: RpcDispatcher,
        request: RequestType,
        registry: dict[MethodType, HandlerType],
        http_request: HttpRequest,
    ) -> ResponseType:
        method = request.method
        start = time.perf_counter()

        try:
            result = await old(self, request, registry, http_request)
        except Exception:
            duration = time.perf_counter() - start
            request_duration.labels(method=method).observe(duration)
            requests_total.labels(method=method, result="error").inc()
            raise

        duration = time.perf_counter() - start

        _observe_outcome(
            method=method,
            duration=duration,
            result=result,
            requests_total=requests_total,
            request_duration=request_duration,
            errors_total=errors_total,
        )

        return result

    setattr(dispatcher, "_dispatch_single", patched)


def _patch_dispatch(
    dispatcher: type[RpcDispatcher],
    *,
    requests_total: Counter,
    request_duration: Histogram,
    errors_total: Counter,
) -> None:
    old = dispatcher.dispatch

    async def patched(
        self: RpcDispatcher,
        body: RequestType | BatchType | RpcError,
        registry: dict[MethodType, HandlerType],
        http_request: HttpRequest,
    ) -> ResponseType | BatchResponseType:
        if not isinstance(body, RpcError):
            return await old(self, body, registry, http_request)

        start = time.perf_counter()
        result = await old(self, body, registry, http_request)
        duration = time.perf_counter() - start

        _observe_outcome(
            method="_invalid",
            duration=duration,
            result=result,
            requests_total=requests_total,
            request_duration=request_duration,
            errors_total=errors_total,
        )

        return result

    setattr(dispatcher, "dispatch", patched)


def _observe_outcome(
    method: str,
    duration: float,
    result: ResponseType | BatchResponseType,
    requests_total: Counter,
    request_duration: Histogram,
    errors_total: Counter,
) -> None:
    request_duration.labels(method=method).observe(duration)

    if result is None:
        result_label = "notification"
    elif isinstance(result, ErrorResponse):
        result_label = "error"
        errors_total.labels(
            method=method,
            code=str(result.error.code),
        ).inc()
    else:
        result_label = "success"

    requests_total.labels(method=method, result=result_label).inc()


class MetricsView(View):
    http_method_names = ["get"]

    def get(
        self,
        request: HttpRequest,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        return HttpResponse(
            generate_latest(_active_registry()),
            content_type=CONTENT_TYPE_LATEST,
        )


def _active_registry() -> CollectorRegistry:
    return REGISTRY if _registry is None else _registry
