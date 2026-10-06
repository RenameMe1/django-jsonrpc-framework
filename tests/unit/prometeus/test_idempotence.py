from __future__ import annotations

import pytest

from jsonrpc_framework.logic.dispatcher import RpcDispatcher
from jsonrpc_framework.integration.prometheus import enable_prometheus
from prometheus_client import CollectorRegistry
from jsonrpc_framework.logic.validator import RequestType
from jsonrpc_framework.logic.dispatcher import HandlerType
from django.http import HttpRequest
from jsonrpc_framework.core.models import MethodType

REQUESTS_TOTAL = "jsonrpc_requests_total"
SUCCESS_LABELS = {"method": "test", "result": "success"}

REQUEST_DURATION = 'jsonrpc_request_duration_seconds_count'
REQUEST_DURATION_LABELS = {'method': "test"}


pytestmark = pytest.mark.asyncio


async def test_idempotence(
    fxt_prometheus_registry: CollectorRegistry,
    valid_request: RequestType,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
):
    patched_single = RpcDispatcher._dispatch_single
    patched_dispatch = RpcDispatcher.dispatch

    other = CollectorRegistry()
    enable_prometheus(registry=other)
    enable_prometheus()

    assert RpcDispatcher._dispatch_single is patched_single
    assert RpcDispatcher.dispatch is patched_dispatch

    await dispatcher.dispatch(valid_request, registry, HttpRequest())

    assert fxt_prometheus_registry.get_sample_value(
        REQUESTS_TOTAL,
        SUCCESS_LABELS,
    ) == 1.0
    assert other.get_sample_value(
        REQUESTS_TOTAL,
        SUCCESS_LABELS,
    ) is None


    assert fxt_prometheus_registry.get_sample_value(
        REQUEST_DURATION,
        REQUEST_DURATION_LABELS,
    ) == 1.0

    assert other.get_sample_value(
        REQUEST_DURATION,
        REQUEST_DURATION_LABELS,
    ) is None