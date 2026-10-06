from __future__ import annotations

import pytest
from django.http import HttpRequest
from prometheus_client import CollectorRegistry

from jsonrpc_framework.core.error import ParseError
from jsonrpc_framework.core.models import MethodType
from jsonrpc_framework.logic.dispatcher import HandlerType, RpcDispatcher
from jsonrpc_framework.logic.validator import RequestType

REQUESTS_TOTAL = "jsonrpc_requests_total"
ERRORS_TOTAL = "jsonrpc_errors_total"
REQUEST_DURATION = "jsonrpc_request_duration_seconds_count"

PARSE_REQUEST_LABELS = {"method": "_invalid", "result": "error"}
PARSE_ERROR_LABELS = {"method": "_invalid", "code": "-32700"}
PARSE_DURATION_LABELS = {"method": "_invalid"}

INVALID_METHOD_LABELS = {"method": "invalid", "result": "error"}
INVALID_METHOD_ERROR_LABELS = {"method": "invalid", "code": "-32601"}

INTERNAL_REQUEST_LABELS = {
    "method": "internal_handler_error",
    "result": "error",
}
INTERNAL_ERROR_LABELS = {
    "method": "internal_handler_error",
    "code": "-32603",
}

pytestmark = pytest.mark.asyncio


async def test_parse_error(
    fxt_prometheus_registry: CollectorRegistry,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
) -> None:
    await dispatcher.dispatch(
        ParseError(data="Invalid JSON"),
        registry,
        HttpRequest(),
    )

    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUESTS_TOTAL,
            PARSE_REQUEST_LABELS,
        )
        == 1.0
    )
    assert (
        fxt_prometheus_registry.get_sample_value(
            ERRORS_TOTAL,
            PARSE_ERROR_LABELS,
        )
        == 1.0
    )
    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUEST_DURATION,
            PARSE_DURATION_LABELS,
        )
        == 1.0
    )


async def test_invalid_method(
    fxt_prometheus_registry: CollectorRegistry,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
    invalid_method_request: RequestType,
) -> None:
    await dispatcher.dispatch(invalid_method_request, registry, HttpRequest())

    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUESTS_TOTAL,
            INVALID_METHOD_LABELS,
        )
        == 1.0
    )
    assert (
        fxt_prometheus_registry.get_sample_value(
            ERRORS_TOTAL,
            INVALID_METHOD_ERROR_LABELS,
        )
        == 1.0
    )


async def test_internal_error(
    fxt_prometheus_registry: CollectorRegistry,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
    internal_handler_error_request: RequestType,
) -> None:
    await dispatcher.dispatch(
        internal_handler_error_request,
        registry,
        HttpRequest(),
    )

    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUESTS_TOTAL,
            INTERNAL_REQUEST_LABELS,
        )
        == 1.0
    )
    assert (
        fxt_prometheus_registry.get_sample_value(
            ERRORS_TOTAL,
            INTERNAL_ERROR_LABELS,
        )
        == 1.0
    )
