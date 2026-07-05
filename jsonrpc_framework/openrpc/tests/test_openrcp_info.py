from jsonrpc_framework.openrpc.document.info import OpenRpcInfo
from jsonrpc_framework.openrpc.document.info._info import _OpenRpcInfoTD


def test_openrpc_info(
    openrpc_info: OpenRpcInfo,
    openrpc_info_dict: _OpenRpcInfoTD,
) -> None:
    _test_openrpc_info(openrpc_info, openrpc_info_dict)


def test_openrpc_info_minimal(
    openrpc_info_minimal: OpenRpcInfo,
    openrpc_info_minimal_dict: _OpenRpcInfoTD,
) -> None:
    _test_openrpc_info(openrpc_info_minimal, openrpc_info_minimal_dict)


def _test_openrpc_info(
    info: OpenRpcInfo,
    info_dict: _OpenRpcInfoTD,
) -> None:
    _model_dict = info.model_dump(by_alias=True, exclude_none=True)

    assert _model_dict == info_dict
