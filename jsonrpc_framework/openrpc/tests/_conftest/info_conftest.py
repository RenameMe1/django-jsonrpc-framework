from jsonrpc_framework.openrpc.document.info import (
    OpenRpcInfo,
    OpenRpcContact,
    OpenRpcLicense,
)
from jsonrpc_framework.openrpc.document.info._info import _OpenRpcInfoTD

import pytest

from jsonrpc_framework.openrpc.document.info import (
    OpenRpcContact,
    OpenRpcInfo,
    OpenRpcLicense,
)
from jsonrpc_framework.openrpc.document.info._info import _OpenRpcInfoTD


@pytest.fixture
def openrpc_info() -> OpenRpcInfo:
    return OpenRpcInfo(
        title="Test API",
        version="1.0.0",
        description="Test API description",
        terms_of_service="https://example.com/terms_of_service",
        contact=OpenRpcContact(
            name="Test API contact name",
            email="test@example.com",
            url="https://example.com/contact",
        ),
        license=OpenRpcLicense(
            name="Test API license name",
            url="https://example.com/license",
        ),
    )


@pytest.fixture
def openrpc_info_dict() -> _OpenRpcInfoTD:
    return {
        "title": "Test API",
        "version": "1.0.0",
        "description": "Test API description",
        "termsOfService": "https://example.com/terms_of_service",
        "contact": {
            "name": "Test API contact name",
            "email": "test@example.com",
            "url": "https://example.com/contact",
        },
        "license": {
            "name": "Test API license name",
            "url": "https://example.com/license",
        },
    }


@pytest.fixture
def openrpc_info_minimal_dict() -> _OpenRpcInfoTD:
    return {
        "title": "Test API",
        "version": "1.0.0",
    }


@pytest.fixture
def openrpc_info_minimal() -> OpenRpcInfo:
    return OpenRpcInfo(
        title="Test API",
        version="1.0.0",
    )
