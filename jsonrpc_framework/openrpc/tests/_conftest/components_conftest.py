import pytest

from jsonrpc_framework.openrpc.document.components import OpenRpcComponents
from jsonrpc_framework.openrpc.document.components._components import (
    _OpenRpcComponentsTD,
)
from jsonrpc_framework.openrpc.document.common import (
    OpenRpcLinkObject,
    OpenRpcErrorObject,
    OpenRpcExamplePairingObject,
    OpenRcpContentDescriptorObject,
    OpenRpcTag,
    OpenRpcDataSchema,
    OpenRpcExampleObject,
)
from jsonrpc_framework.openrpc.document.common import OpenRcpTypeSchema


@pytest.fixture
def openrpc_components(
    openrpc_link: OpenRpcLinkObject,
    openrpc_error: OpenRpcErrorObject,
    openrpc_example_pairing: OpenRpcExamplePairingObject,
    openrpc_params: OpenRcpContentDescriptorObject,
    openrpc_tag: OpenRpcTag,
) -> OpenRpcComponents:
    return OpenRpcComponents(
        schemas={"test_schema": OpenRcpTypeSchema(type="string")},
        links={"test_link": openrpc_link},
        errors={"test_error": openrpc_error},
        examples={
            "test_example": OpenRpcExampleObject(
                name="test_example",
                description="Test example description",
                value="test_value",
                schema=OpenRpcDataSchema(type="string"),
            )
        },
        examplePairings={"test_example_pairing": openrpc_example_pairing},
        contentDescriptors={"test_content_descriptor": openrpc_params},
        tags={"test_tag": openrpc_tag},
    )


@pytest.fixture
def openrpc_components_dict() -> _OpenRpcComponentsTD:
    return {
        "schemas": {
            "test_schema": {"type": "string"},
        },
        "links": {
            "test_link": {
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
                            "enum": [
                                "test_value1",
                                "test_value2",
                            ],
                        },
                    },
                },
                "summary": "Test link summary",
            },
        },
        "errors": {
            "test_error": {
                "code": 1000,
                "message": "Test error message",
                "data": "Test error data",
            },
        },
        "examples": {
            "test_example": {
                "name": "test_example",
                "description": "Test example description",
                "value": "test_value",
            },
        },
        "examplePairings": {
            "test_example_pairing": {
                "name": "test_example_pairing",
                "description": "Test example pairing description",
                "params": [
                    {
                        "name": "test_example",
                        "description": "Test example description",
                        "summary": "Test example summary",
                        "value": "test_value",
                    },
                ],
                "result": {
                    "name": "test_example",
                    "description": "Test example description",
                    "summary": "Test example summary",
                    "value": "test_value",
                },
            },
        },
        "contentDescriptors": {
            "test_content_descriptor": {
                "name": "test_param",
                "description": "Test param description",
                "schema": {"type": "string"},
                "required": False,
                "deprecated": False,
            },
        },
        "tags": {
            "test_tag": {
                "name": "test_tag",
                "description": "Test tag description",
                "externalDocs": {
                    "description": "Test external docs description",
                    "url": "https://example.com/external_docs",
                },
            },
        },
    }
