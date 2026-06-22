import pytest

from jsonrpc_framework.openrpc.document.method._method import (
    _OpenRpcMethodTD,
    OpenRpcMethod,
)
from jsonrpc_framework.openrpc.document.common import (
    OpenRpcTag,
    OpenRcpContentDescriptorObject,
    OpenRpcErrorObject,
    OpenRpcLinkObjectServer,
    OpenRpcLinkObject,
    OpenRpcExamplePairingObject,
    OpenRpcExampleObject,
)
from jsonrpc_framework.openrpc.document.server import (
    OpenRpcServer,
    OpenRpcServerObjectVariable,
)
from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.common import OpenRcpTypeSchema

from jsonrpc_framework.openrpc.builder.builder import OpenRpcBuilder
from jsonrpc_framework.openrpc.document.info import OpenRpcContact, OpenRpcLicense


@pytest.fixture
def openrpc_builder() -> OpenRpcBuilder:
    return OpenRpcBuilder(
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
def openrpc_method(
    openrpc_server: OpenRpcServer,
    openrpc_tag: OpenRpcTag,
    openrpc_params: OpenRcpContentDescriptorObject,
    openrpc_result: OpenRcpContentDescriptorObject,
    openrpc_error: OpenRpcErrorObject,
    openrpc_link: OpenRpcLinkObject,
    openrpc_example_pairing: OpenRpcExamplePairingObject,
    openrpc_external_doc: OpenRpcExternalDoc,
) -> OpenRpcMethod:
    return OpenRpcMethod(
        name="test_method",
        description="Test method description",
        summary="Test method summary",
        servers=[openrpc_server],
        tags=[openrpc_tag],
        paramStructure="either",
        params=[openrpc_params],
        result=openrpc_result,
        errors=[openrpc_error],
        links=[openrpc_link],
        examples=[openrpc_example_pairing],
        deprecated=False,
        externalDocs=openrpc_external_doc,
    )


@pytest.fixture
def openrpc_method_dict() -> _OpenRpcMethodTD:
    return {
        "name": "test_method",
        "description": "Test method description",
        "summary": "Test method summary",
        "servers": [
            {
                "description": "Test server description",
                "name": "Test server",
                "summary": "Test server summary",
                "url": "https://example.com/server",
                "variables": {
                    "test_variable": {
                        "default": "test_value",
                        "description": "Test variable description",
                        "enum": ["test_value1", "test_value2"],
                    },
                },
            }
        ],
        "tags": [
            {
                "description": "Test tag description",
                "externalDocs": {
                    "url": "https://example.com/external_docs",
                    "description": "Test external docs description",
                },
                "name": "test_tag",
            }
        ],
        "paramStructure": "either",
        "params": [
            {
                "required": False,
                "deprecated": False,
                "name": "test_param",
                "description": "Test param description",
                "schema": {
                    "type": "string",
                },
            }
        ],
        "result": {
            "required": False,
            "deprecated": False,
            "name": "test_result",
            "description": "Test result description",
            "schema": {
                "type": "string",
            },
        },
        "errors": [
            {
                "code": 1000,
                "message": "Test error message",
                "data": "Test error data",
            }
        ],
        "links": [
            {
                "description": "Test link description",
                "method": "test_method",
                "name": "test_link",
                "params": {
                    "test_param": "test_value",
                },
                "server": {
                    "description": "Test server description",
                    "name": "Test server",
                    "summary": "Test server summary",
                    "url": "https://example.com/server",
                    "variables": {
                        "test_variable": {
                            "default": "test_value",
                            "description": "Test variable description",
                            "enum": ["test_value1", "test_value2"],
                        },
                    },
                },
                "summary": "Test link summary",
            }
        ],
        "examples": [
            {
                "description": "Test example pairing description",
                "name": "test_example_pairing",
                "params": [
                    {
                        "summary": "Test example summary",
                        "value": "test_value",
                        "description": "Test example description",
                        "name": "test_example",
                    }
                ],
                "result": {
                    "summary": "Test example summary",
                    "value": "test_value",
                    "description": "Test example description",
                    "name": "test_example",
                },
            }
        ],
        "deprecated": False,
        "externalDocs": {
            "url": "https://example.com/external_docs",
            "description": "Test external docs description",
        },
    }


@pytest.fixture
def openrpc_method_minimal() -> OpenRpcMethod:
    return OpenRpcMethod(
        name="test_method",
        description="Test method description",
        summary="Test method summary",
        params=[],
    )


@pytest.fixture
def openrpc_method_minimal_dict() -> _OpenRpcMethodTD:
    return {
        "name": "test_method",
        "description": "Test method description",
        "summary": "Test method summary",
        "deprecated": False,
        "paramStructure": "either",
        "params": [],
    }


@pytest.fixture
def openrpc_tag() -> OpenRpcTag:
    return OpenRpcTag(
        name="test_tag",
        description="Test tag description",
        externalDocs=OpenRpcExternalDoc(
            url="https://example.com/external_docs",
            description="Test external docs description",
        ),
    )


@pytest.fixture
def openrpc_params() -> OpenRcpContentDescriptorObject:
    return OpenRcpContentDescriptorObject(
        name="test_param",
        description="Test param description",
        schema_=OpenRcpTypeSchema(type="string"),
        required=False,
        deprecated=False,
    )


@pytest.fixture
def openrpc_result() -> OpenRcpContentDescriptorObject:
    return OpenRcpContentDescriptorObject(
        name="test_result",
        description="Test result description",
        schema_=OpenRcpTypeSchema(type="string"),
        required=False,
        deprecated=False,
    )


@pytest.fixture
def openrpc_error() -> OpenRpcErrorObject:
    return OpenRpcErrorObject(
        code=1000,
        message="Test error message",
        data="Test error data",
    )


@pytest.fixture
def openrpc_server_link() -> OpenRpcLinkObjectServer:
    return OpenRpcLinkObjectServer(
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
def openrpc_link(openrpc_server_link: OpenRpcLinkObjectServer) -> OpenRpcLinkObject:
    return OpenRpcLinkObject(
        name="test_link",
        summary="Test link summary",
        method="test_method",
        description="Test link description",
        params={
            "test_param": "test_value",
        },
        server=openrpc_server_link,
    )


@pytest.fixture
def openrpc_example_pairing() -> OpenRpcExamplePairingObject:
    return OpenRpcExamplePairingObject(
        name="test_example_pairing",
        description="Test example pairing description",
        params=[
            OpenRpcExampleObject(
                summary="Test example summary",
                value="test_value",
                description="Test example description",
                name="test_example",
            )
        ],
        result=OpenRpcExampleObject(
            summary="Test example summary",
            value="test_value",
            description="Test example description",
            name="test_example",
        ),
    )
