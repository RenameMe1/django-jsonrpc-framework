from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.external_docs._external_docs import (
    _OpenRpcExternalDocTD,
)


def _test_openrpc_external_doc(
    openrpc_external_doc: OpenRpcExternalDoc,
    openrpc_external_doc_dict: _OpenRpcExternalDocTD,
) -> None:
    _model_dict = openrpc_external_doc.model_dump(by_alias=True, exclude_none=True)

    assert _model_dict == openrpc_external_doc_dict


def test_openrpc_external_doc(
    openrpc_external_doc: OpenRpcExternalDoc,
    openrpc_external_doc_dict: _OpenRpcExternalDocTD,
) -> None:
    _test_openrpc_external_doc(openrpc_external_doc, openrpc_external_doc_dict)


def test_openrpc_external_doc_minimal(
    openrpc_external_doc_minimal: OpenRpcExternalDoc,
    openrpc_external_doc_minimal_dict: _OpenRpcExternalDocTD,
) -> None:
    _test_openrpc_external_doc(
        openrpc_external_doc_minimal, openrpc_external_doc_minimal_dict
    )
