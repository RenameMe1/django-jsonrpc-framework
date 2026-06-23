import pytest

from jsonrpc_framework.openrpc.document.server import (
    OpenRpcServer,
    OpenRpcServerObjectVariable,
)
from jsonrpc_framework.openrpc.document.server._server import _OpenRpcServerTD


@pytest.fixture
def openrpc_server() -> OpenRpcServer:
    return OpenRpcServer(
        url="https://example.com/server",
        name="Test server",
        description="Test server description",
        summary="Test server summary",
        variables={
            "test_variable": OpenRpcServerObjectVariable(
                default="test_value",
                description="Test variable description",
                enum=["test_value1", "test_value2"],
            ),
        },
    )


@pytest.fixture
def openrpc_server_dict() -> _OpenRpcServerTD:
    return {
        "url": "https://example.com/server",
        "name": "Test server",
        "description": "Test server description",
        "summary": "Test server summary",
        "variables": {
            "test_variable": {
                "default": "test_value",
                "description": "Test variable description",
                "enum": ["test_value1", "test_value2"],
            },
        },
    }


@pytest.fixture
def openrpc_server_minimal() -> OpenRpcServer:
    return OpenRpcServer(
        url="https://example.com/server",
    )


@pytest.fixture
def openrpc_server_minimal_dict() -> _OpenRpcServerTD:
    return {
        "url": "https://example.com/server",
    }
