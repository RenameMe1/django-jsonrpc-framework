from jsonrpc_framework.openrpc.document.server import OpenRpcServer
from jsonrpc_framework.openrpc.document.server._server import _OpenRpcServerTD


def _test_openrpc_server(
    openrpc_server: OpenRpcServer,
    openrpc_server_dict: _OpenRpcServerTD,
) -> None:
    _model_dict = openrpc_server.model_dump(by_alias=True, exclude_none=True)

    assert _model_dict == openrpc_server_dict


def test_openrpc_server(
    openrpc_server: OpenRpcServer,
    openrpc_server_dict: _OpenRpcServerTD,
) -> None:
    _test_openrpc_server(openrpc_server, openrpc_server_dict)


def test_openrpc_server_minimal(
    openrpc_server_minimal: OpenRpcServer,
    openrpc_server_minimal_dict: _OpenRpcServerTD,
) -> None:
    _test_openrpc_server(openrpc_server_minimal, openrpc_server_minimal_dict)
