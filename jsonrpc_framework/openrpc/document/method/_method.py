from pydantic import Field

from typing import Annotated, TypedDict

from jsonrpc_framework.openrpc.document._base import OpenRPCModel
from jsonrpc_framework.openrpc.document.server import OpenRpcServer
from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.common import (
    OpenRpcTag,
    OpenRpcReferenceObject,
    OpenRcpContentDescriptorObject,
    OpenRpcErrorObject,
    OpenRpcLinkObject,
    OpenRpcExamplePairingObject,
)
from jsonrpc_framework.openrpc.document.external_docs._external_docs import (
    _OpenRpcExternalDocTD,
)
from jsonrpc_framework.openrpc.document.common._pairing_object import (
    _OpenRpcExamplePairingObjectTD,
)
from jsonrpc_framework.openrpc.document.common._reference import (
    _OpenRpcReferenceObjectTD,
)
from jsonrpc_framework.openrpc.document.common._link import _OpenRpcLinkObjectTD
from jsonrpc_framework.openrpc.document.common._error import _OpenRpcErrorObjectTD
from jsonrpc_framework.openrpc.document.common._descriptor import (
    _OpenRcpContentDescriptorObjectTD,
)
from jsonrpc_framework.openrpc.document.common._tag import _OpenRpcTagTD
from jsonrpc_framework.openrpc.document.server._server import _OpenRpcServerTD


class _OpenRpcMethodTD(TypedDict, total=False):
    name: str
    description: str | None
    summary: str | None
    servers: list[_OpenRpcServerTD] | None
    tags: list[_OpenRpcTagTD] | None
    paramStructure: str | None
    params: list[_OpenRcpContentDescriptorObjectTD | _OpenRpcReferenceObjectTD]
    result: _OpenRcpContentDescriptorObjectTD | _OpenRpcReferenceObjectTD | None
    errors: list[_OpenRpcErrorObjectTD | _OpenRpcReferenceObjectTD] | None
    links: list[_OpenRpcLinkObjectTD | _OpenRpcReferenceObjectTD] | None
    examples: list[_OpenRpcExamplePairingObjectTD | _OpenRpcReferenceObjectTD] | None
    deprecated: bool | None
    externalDocs: _OpenRpcExternalDocTD | None


class OpenRpcMethod(OpenRPCModel):
    name: Annotated[
        str,
        """REQUIRED. The canonical name for the method. The name MUST be unique
        within the methods array.
        """,
    ]
    description: Annotated[
        str | None,
        Field(default=None),
        """A verbose explanation of the method behavior. Markdawn may be used
        for rich text representation.
        """,
    ] = None
    summary: Annotated[
        str | None,
        Field(default=None),
        """A short summary of what the method does.
        """,
    ] = None
    servers: Annotated[
        list[OpenRpcServer] | None,
        Field(default=None),
        """An array of Server Objects, which provide connectivity information
        to a targer server. If the `servers` property is not provided, or is an
        empty array, the default value would be a Server Object with a URL 
        value of `localhost`.
        """,
    ] = None
    tags: Annotated[
        list[OpenRpcTag] | None,
        Field(default=None),
        """A list of tags for API documentation control. Tags can be used for 
        logical grouping of methods by resources or any other qualifier.
        """,
    ] = None
    paramStructure: Annotated[
        str,
        Field(default="either"),
        """Format the server expect the params. Defaults to `either`
        """,
    ] = "either"
    params: Annotated[
        list[OpenRcpContentDescriptorObject | OpenRpcReferenceObject],
        Field(default_factory=list),
        """REQUIRED. A list of parameters that are applicable for this method.
        The list MUST NOT include duplicated parameters and therefore require
        name to be unique. The list can use the Reference Object to link to
        parameters that are defined by the Content Descriptor Object.
        All optional params (content descriptor objects with “required”:
        false) MUST be positioned after all required params in the list.
        """,
    ]
    result: Annotated[
        OpenRcpContentDescriptorObject | OpenRpcReferenceObject | None,
        Field(default=None),
        """The description of the result returned by the method. If defined,
        it MUST be a Content Descriptor or Reference Object.
        If undefined, the method MUST only be used as a notification
        """,
    ] = None
    errors: Annotated[
        list[OpenRpcErrorObject | OpenRpcReferenceObject] | None,
        Field(default=None),
        """A list of custom application defined errors that MAY be returned.
        The Errors MUST have unique error codes.
        """,
    ] = None
    links: Annotated[
        list[OpenRpcLinkObject | OpenRpcReferenceObject] | None,
        Field(default=None),
        """A list of possible links from this method call.
        """,
    ] = None
    examples: Annotated[
        list[OpenRpcExamplePairingObject | OpenRpcReferenceObject] | None,
        Field(default=None),
        """Array of Example Pairing Objects where each example includes a
        valid params-to-result Content Descriptor pairing.
        """,
    ] = None
    deprecated: Annotated[
        bool,
        Field(default=False),
        """Declares this method to be deprecated. Consumers SHOULD refrain from
         usage of the declared method. Default value is false.
        """,
    ] = False
    externalDocs: Annotated[
        OpenRpcExternalDoc | None,
        Field(default=None),
        """Additional external documentation.
        """,
    ] = None
