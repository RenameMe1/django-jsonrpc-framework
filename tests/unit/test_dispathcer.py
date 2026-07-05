from collections.abc import Callable

import pytest
from django.http import HttpRequest

from jsonrpc_framework.core.models import (
    ErrorResponse,
    MethodType,
    Notification,
    Request,
    RpcError,
    SuccessResponse,
)
from jsonrpc_framework.logic.dispatcher import RpcDispatcher

pytestmark = pytest.mark.asyncio


async def test_method_finding(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    valid_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        valid_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, SuccessResponse)
    assert result.id == valid_request.id
    assert result.result == "test"


async def test_method_not_found(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    invalid_method_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        invalid_method_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, ErrorResponse)
    assert result.id == invalid_method_request.id
    assert result.error.code == -32601
    assert result.error.message == "Method not found"


async def test_invalid_params(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    invalid_params_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        invalid_params_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, ErrorResponse)
    assert result.id == invalid_params_request.id
    assert result.error.code == -32602
    assert result.error.message == "Invalid params"


async def test_async_method(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    async_method_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        async_method_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, SuccessResponse)
    assert result.id == async_method_request.id
    assert result.result == "Awaitable success"


async def test_sync_method(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    sync_method_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        sync_method_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, SuccessResponse)
    assert result.id == sync_method_request.id
    assert result.result == "Success"


async def test_internal_handler_error(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    internal_handler_error_request: Request,
) -> None:
    result = await dispatcher.dispatch(
        internal_handler_error_request, registry, http_request=HttpRequest()
    )

    assert isinstance(result, ErrorResponse)
    assert result.id == internal_handler_error_request.id
    assert result.error.code == -32603
    assert result.error.message == "Internal error"


async def test_notification_response(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    notification_request: Notification,
) -> None:
    result = await dispatcher.dispatch(
        notification_request, registry, http_request=HttpRequest()
    )

    assert result is None


async def test_valid_requests_batch_dispatching(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    valid_requests_batch: list[Request],
) -> None:
    result = await dispatcher.dispatch(
        valid_requests_batch, registry, http_request=HttpRequest()
    )

    assert isinstance(result, list)
    assert len(result) == len(valid_requests_batch)
    assert all(isinstance(item, SuccessResponse) for item in result)

    assert result[0].id == valid_requests_batch[0].id
    assert result[1].id == valid_requests_batch[1].id


async def test_valid_batch_with_request_and_notification(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    valid_requests_batch_with_request_and_notification: list[
        Request | Notification
    ],
) -> None:
    result = await dispatcher.dispatch(
        valid_requests_batch_with_request_and_notification,
        registry,
        http_request=HttpRequest(),
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert all(isinstance(item, SuccessResponse) for item in result)

    assert (
        result[0].id == valid_requests_batch_with_request_and_notification[0].id
    )


async def test_batch_with_errors(
    dispatcher: RpcDispatcher,
    registry: dict[MethodType, Callable],
    valid_batch_with_errors: list[Request | RpcError],
) -> None:
    result = await dispatcher.dispatch(
        valid_batch_with_errors, registry, http_request=HttpRequest()
    )

    assert isinstance(result, list)
    assert len(result) == len(valid_batch_with_errors)

    assert isinstance(result[0], SuccessResponse)
    assert result[0].id == valid_batch_with_errors[0].id

    assert isinstance(result[1], ErrorResponse)
    assert result[1].id is None
    assert result[1].error.code == -32601
    assert result[1].error.message == "Method not found"
