import pytest

from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.external_docs._external_docs import (
    _OpenRpcExternalDocTD,
)


@pytest.fixture
def openrpc_external_doc() -> OpenRpcExternalDoc:
    return OpenRpcExternalDoc(
        url="https://example.com/external_docs",
        description="Test external docs description",
    )


@pytest.fixture
def openrpc_external_doc_dict() -> _OpenRpcExternalDocTD:
    return {
        "url": "https://example.com/external_docs",
        "description": "Test external docs description",
    }


@pytest.fixture
def openrpc_external_doc_minimal() -> OpenRpcExternalDoc:
    return OpenRpcExternalDoc(
        url="https://example.com/external_docs",
    )


@pytest.fixture
def openrpc_external_doc_minimal_dict() -> _OpenRpcExternalDocTD:
    return {
        "url": "https://example.com/external_docs",
    }
