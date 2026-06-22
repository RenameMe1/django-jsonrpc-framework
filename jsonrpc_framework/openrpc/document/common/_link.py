from typing import Annotated, Any, TypedDict
from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel
from jsonrpc_framework.openrpc.document.common._link_server import (
    OpenRpcLinkObjectServer,
    _OpenRpcLinkObjectServerTD,
)


__all__ = [
    "OpenRpcLinkObject",
]


class _OpenRpcLinkObjectTD(TypedDict):
    name: str
    summary: str | None
    method: str | None
    description: str | None
    params: dict[str, Any] | None
    server: _OpenRpcLinkObjectServerTD


class OpenRpcLinkObject(OpenRPCModel):
    """A server object to be used by the target method."""

    name: Annotated[str, """Cannonical name of the link."""]
    summary: Annotated[
        str | None, Field(default=None), """A short summary of the link."""
    ] = None
    method: Annotated[
        str | None,
        Field(default=None),
        """The name of an existing, resolvable OpenRPC method, as defined
        with a unique method. This field MUST resolve to a unique Method
        Object. As opposed to Open Api, Relative method values
        ARE NOT permitted.
        """,
    ] = None
    description: Annotated[
        str | None,
        Field(default=None),
        """A description of the link. GitHub Flavored Markdown syntax
        MAY be used for rich text representation.
        """,
    ] = None
    params: Annotated[
        dict[str, Any] | None,
        Field(default=None),
        """A map representing parameters to pass to a method as specified 
        with method. The key is the parameter name to be used, whereas 
        the value can be a constant or a runtime expression to be evaluated
         and passed to the linked method.""",
    ] = None
    server: Annotated[
        OpenRpcLinkObjectServer,
        """A server object to be used by the target method.
        """,
    ]
