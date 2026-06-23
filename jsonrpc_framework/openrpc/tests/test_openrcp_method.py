from jsonrpc_framework.openrpc.document.method import OpenRpcMethod
from jsonrpc_framework.openrpc.document.method._method import _OpenRpcMethodTD


def _test_openrpc_method(
    openrpc_method: OpenRpcMethod,
    openrpc_method_dict: _OpenRpcMethodTD,
) -> None:
    _model_dict = openrpc_method.model_dump(by_alias=True, exclude_none=True)

    assert _model_dict == openrpc_method_dict


def test_openrpc_method(
    openrpc_method: OpenRpcMethod,
    openrpc_method_dict: _OpenRpcMethodTD,
) -> None:
    _test_openrpc_method(openrpc_method, openrpc_method_dict)


def test_openrpc_method_minimal(
    openrpc_method_minimal: OpenRpcMethod,
    openrpc_method_minimal_dict: _OpenRpcMethodTD,
) -> None:
    _test_openrpc_method(openrpc_method_minimal, openrpc_method_minimal_dict)
