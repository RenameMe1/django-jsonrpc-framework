from __future__ import annotations

import pytest
from django.http import HttpRequest
from prometheus_client import CollectorRegistry

from jsonrpc_framework.core.models import MethodType
from jsonrpc_framework.logic.dispatcher import HandlerType, RpcDispatcher
from jsonrpc_framework.logic.validator import RequestType

REQUESTS_TOTAL = "jsonrpc_requests_total"
REQUEST_DURATION = "jsonrpc_request_duration_seconds_count"

SUCCESS_LABELS = {"method": "test", "result": "success"}
REQUEST_DURATION_LABELS = {"method": "test"}

pytestmark = pytest.mark.asyncio


async def test_success(
    fxt_prometheus_registry: CollectorRegistry,
    valid_request: RequestType,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
):

    await dispatcher.dispatch(valid_request, registry, HttpRequest())

    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUESTS_TOTAL,
            SUCCESS_LABELS,
        )
        == 1.0
    )

    assert (
        fxt_prometheus_registry.get_sample_value(
            REQUEST_DURATION,
            REQUEST_DURATION_LABELS,
        )
        == 1.0
    )
