from __future__ import annotations

from http import HTTPStatus

import pytest
from django.http import HttpRequest
from django.test import RequestFactory
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry

from jsonrpc_framework.core.models import MethodType
from jsonrpc_framework.integration.prometheus import MetricsView
from jsonrpc_framework.logic.dispatcher import HandlerType, RpcDispatcher
from jsonrpc_framework.logic.validator import RequestType

pytestmark = pytest.mark.asyncio


async def test_metrics(
    fxt_prometheus_registry: CollectorRegistry,
    valid_request: RequestType,
    registry: dict[MethodType, HandlerType],
    dispatcher: RpcDispatcher,
) -> None:
    await dispatcher.dispatch(valid_request, registry, HttpRequest())

    request = RequestFactory().get("/metrics")
    response = MetricsView.as_view()(request)

    assert response.status_code == HTTPStatus.OK
    assert CONTENT_TYPE_LATEST in response["Content-Type"]
    assert b"jsonrpc_requests_total" in response.content
