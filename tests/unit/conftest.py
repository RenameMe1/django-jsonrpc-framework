from collections.abc import Callable

import pytest

from jsonrpc_framework.core.models import (
    MethodType,
    Notification,
    Request,
    RpcError,
)
from jsonrpc_framework.logic.dispatcher import RpcDispatcher
from jsonrpc_framework.logic.responser import ResponseBuilder
from jsonrpc_framework.controller.auth import AccessType, AccessPolicy
from jsonrpc_framework.logic.validator import RequestValidator

# Validators fixtures


@pytest.fixture
def validator() -> RequestValidator:
    return RequestValidator()


@pytest.fixture
def valid_bytes_request() -> bytes:
    return b'{"jsonrpc": "2.0", "method": "test", "params": [1, 2, 3], "id": 1}'


@pytest.fixture
def valid_bytes_notification() -> bytes:
    return b'{"jsonrpc": "2.0", "method": "test", "params": [1, 2, 3]}'


@pytest.fixture
def invalid_bytes_request() -> bytes:
    return b'{"jsonrpc": "2.0", "params": [1, 2, 3], "id": "1"}'


@pytest.fixture
def valid_batch_contain_invalid_request(
    valid_bytes_request: bytes,
    invalid_bytes_request: bytes,
) -> bytes:
    return b"[" + valid_bytes_request + b"," + invalid_bytes_request + b"]"


@pytest.fixture
def unsupported_version_request() -> bytes:
    return b'{"jsonrpc": "1.0", "method": "test", "params": [1, 2, 3], "id": 1}'


# Dispatcher fixtures


@pytest.fixture
def dispatcher() -> RpcDispatcher:
    return RpcDispatcher(
        resolve_method_access=lambda func: AccessPolicy(
            access=AccessType.PUBLIC, auth=[], permissions=[]
        )
    )




async def async_method() -> str:
    return "Awaitable success"


def sync_method() -> str:
    return "Success"


def internal_handler_error() -> str:
    raise Exception("Internal handler error")


@pytest.fixture
def registry() -> dict[MethodType, Callable]:
    return {
        "test": lambda: "test",
        "sync_method": sync_method,
        "async_method": async_method,
        "internal_handler_error": internal_handler_error,
    }


@pytest.fixture
def valid_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="test",
        id=1,
    )


@pytest.fixture
def invalid_method_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="invalid",
        id=1,
    )


@pytest.fixture
def invalid_params_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="test",
        params=["invalid", "params"],
        id=1,
    )


@pytest.fixture
def async_method_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="async_method",
        id=1,
    )


@pytest.fixture
def sync_method_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="sync_method",
        id=1,
    )


@pytest.fixture
def internal_handler_error_request() -> Request:
    return Request(
        jsonrpc="2.0",
        method="internal_handler_error",
        id=1,
    )


@pytest.fixture
def notification_request() -> Notification:
    return Notification(
        jsonrpc="2.0",
        method="test",
        id=1,
    )


@pytest.fixture
def valid_requests_batch() -> list[Request | Notification]:
    return [
        Request(
            jsonrpc="2.0",
            method="test",
            id=1,
        ),
        Request(
            jsonrpc="2.0",
            method="test",
            id=2,
        ),
    ]


@pytest.fixture
def valid_requests_batch_with_request_and_notification() -> list[
    Request | Notification
]:
    return [
        Request(
            jsonrpc="2.0",
            method="test",
            id=1,
        ),
        Notification(
            jsonrpc="2.0",
            method="test",
        ),
    ]


@pytest.fixture
def valid_batch_with_errors() -> list[Request | RpcError]:
    return [
        Request(
            jsonrpc="2.0",
            method="test",
            id=1,
        ),
        RpcError(
            code=-32601,
            message="Method not found",
            data=None,
        ),
    ]


# Builder fixtures


@pytest.fixture
def response_builder() -> ResponseBuilder:
    return ResponseBuilder()
