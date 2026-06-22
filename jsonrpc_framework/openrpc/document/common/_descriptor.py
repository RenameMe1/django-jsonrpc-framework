from typing import Annotated, TypedDict, NotRequired
from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel
from jsonrpc_framework.openrpc.document.common._schema import OpenRcpTypeSchema
from jsonrpc_framework.openrpc.document.common._schema import _OpenRpcSchemaTD
from jsonrpc_framework.openrpc.document.common._schema import (
    OpenRpcRefSchema,
    OpenRpcDataSchema,
)

__all__ = [
    "OpenRcpContentDescriptorObject",
]


class _OpenRcpContentDescriptorObjectTD(TypedDict):
    name: str
    description: NotRequired[str]
    summary: NotRequired[str]
    schema: _OpenRpcSchemaTD
    required: bool
    deprecated: bool


class OpenRcpContentDescriptorObject(OpenRPCModel):
    """Content Descriptors are objects that do just as they suggest - describe
    content. They are reusable ways of describing either parameters or result.
    They MUST have a schema..
    """

    name: Annotated[
        str,
        """REQUIRED. Name of the content that is being described. If the
        content described is a method parameter assignable by-name, this
        field SHALL define the parameter’s key (ie name).
        """,
    ]
    description: Annotated[
        str | None,
        Field(default=None),
        """A verbose explanation of the content descriptor behavior.
        The Markdown syntax MAY be used for rich text representation.
        """,
    ] = None
    summary: Annotated[
        str | None,
        Field(default=None),
        """A short summary of the content that is being described..
        """,
    ] = None
    schema_: Annotated[
        OpenRcpTypeSchema | OpenRpcRefSchema | OpenRpcDataSchema,
        Field(serialization_alias="schema"),
        """REQUIRED. Schema that describes the content..
        """,
    ]
    required: Annotated[
        bool,
        Field(default=False),
        """Determines if the content is a required field. Default value is false..
        """,
    ] = False
    deprecated: Annotated[
        bool,
        Field(default=False),
        """Specifies that the content is deprecated and SHOULD be transitioned
        out of usage. Default value is false.
        """,
    ] = False
