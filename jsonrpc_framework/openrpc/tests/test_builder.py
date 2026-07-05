import json

from jsonrpc_framework.openrpc.builder.builder import OpenRpcBuilder
from jsonrpc_framework.openrpc.document.components import OpenRpcComponents
from jsonrpc_framework.openrpc.document.external_docs._external_docs import (
    _OpenRpcExternalDocTD,
)
from jsonrpc_framework.openrpc.document.server._server import _OpenRpcServerTD
from jsonrpc_framework.openrpc.document.method._method import _OpenRpcMethodTD
from jsonrpc_framework.openrpc.document.components._components import (
    _OpenRpcComponentsTD,
)
from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.info._info import _OpenRpcInfoTD
from jsonrpc_framework.openrpc.document.method import OpenRpcMethod
from jsonrpc_framework.openrpc.document.method._method import _OpenRpcMethodTD
from jsonrpc_framework.openrpc.document.server import OpenRpcServer
from jsonrpc_framework.openrpc.document.server._server import _OpenRpcServerTD


def test_builder(
    openrpc_builder: OpenRpcBuilder,
    openrpc_method: OpenRpcMethod,
    openrpc_server: OpenRpcServer,
    openrpc_external_doc: OpenRpcExternalDoc,
    openrpc_info_dict: _OpenRpcInfoTD,
    openrpc_method_dict: _OpenRpcMethodTD,
    openrpc_server_dict: _OpenRpcServerTD,
    openrpc_external_doc_dict: _OpenRpcExternalDocTD,
    openrpc_components: OpenRpcComponents,
    openrpc_components_dict: _OpenRpcComponentsTD,
) -> None:
    openrpc_builder.add_method(openrpc_method)
    openrpc_builder.add_server(openrpc_server)
    openrpc_builder.add_external_doc(openrpc_external_doc)
    openrpc_builder.add_components(openrpc_components)

    document = openrpc_builder.build_json()

    assert json.loads(document) == {
        "openrpc": "1.3.2",
        "info": openrpc_info_dict,
        "methods": [openrpc_method_dict],
        "servers": [openrpc_server_dict],
        "externalDocs": openrpc_external_doc_dict,
        "components": openrpc_components_dict,
    }
