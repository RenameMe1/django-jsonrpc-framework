from jsonrpc_framework.openrpc.document.components import OpenRpcComponents
from jsonrpc_framework.openrpc.document.components._components import (
    _OpenRpcComponentsTD,
)


def test_openrpc_components(
    openrpc_components: OpenRpcComponents,
    openrpc_components_dict: _OpenRpcComponentsTD,
) -> None:
    _open_rpc_components = openrpc_components.model_dump(
        by_alias=True, exclude_none=True
    )

    assert _open_rpc_components == openrpc_components_dict
