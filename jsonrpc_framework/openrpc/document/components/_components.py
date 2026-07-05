from typing import Annotated, Any, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel
from jsonrpc_framework.openrpc.document.common import (
    OpenRcpContentDescriptorObject,
    OpenRpcErrorObject,
    OpenRpcExampleObject,
    OpenRpcExamplePairingObject,
    OpenRpcLinkObject,
    OpenRpcTag,
)
from jsonrpc_framework.openrpc.document.common._descriptor import (
    _OpenRcpContentDescriptorObjectTD,
)
from jsonrpc_framework.openrpc.document.common._error import (
    _OpenRpcErrorObjectTD,
)
from jsonrpc_framework.openrpc.document.common._example import (
    _OpenRpcExampleObjectTD,
)
from jsonrpc_framework.openrpc.document.common._link import _OpenRpcLinkObjectTD
from jsonrpc_framework.openrpc.document.common._error import _OpenRpcErrorObjectTD
from jsonrpc_framework.openrpc.document.common._example import _OpenRpcExampleObjectTD
from jsonrpc_framework.openrpc.document.common._pairing_object import (
    _OpenRpcExamplePairingObjectTD,
)
from jsonrpc_framework.openrpc.document.common._descriptor import (
    _OpenRcpContentDescriptorObjectTD,
)
from jsonrpc_framework.openrpc.document.common._tag import _OpenRpcTagTD


class OpenRpcComponents(OpenRPCModel):
    """
    Holds a set of reusable objects for different aspects of the OpenRPC.
    All objects defined within the components object will have no effect on
    the API unless they are explicitly referenced from properties outside the
    components object..
    """

    schemas: Annotated[
        dict[str, Any] | None,
        Field(default=None),
        """
        An object to hold reusable Schema Objects.
        """,
    ] = None
    links: Annotated[
        dict[str, OpenRpcLinkObject] | None,
        Field(default=None),
        """
        An object to hold reusable Link Objects.
        """,
    ] = None
    errors: Annotated[
        dict[str, OpenRpcErrorObject] | None,
        Field(default=None),
        """
        An object to hold reusable Error Objects.
        """,
    ] = None
    examples: Annotated[
        dict[str, OpenRpcExampleObject] | None,
        Field(default=None),
        """
        An object to hold reusable Example Objects.
        """,
    ] = None
    examplePairings: Annotated[
        dict[str, OpenRpcExamplePairingObject] | None,
        Field(default=None),
        """
        An object to hold reusable Example Pairing Objects.
        """,
    ] = None
    contentDescriptors: Annotated[
        dict[str, OpenRcpContentDescriptorObject] | None,
        Field(default=None),
        """
        An object to hold reusable Content Descriptor Objects.
        """,
    ] = None
    tags: Annotated[
        dict[str, OpenRpcTag] | None,
        Field(default=None),
        """
        An object to hold reusable Tag Objects.
        """,
    ] = None


class _OpenRpcComponentsTD(TypedDict, total=False):
    schemas: dict[str, Any] | None
    links: dict[str, _OpenRpcLinkObjectTD] | None
    errors: dict[str, _OpenRpcErrorObjectTD] | None
    examples: dict[str, _OpenRpcExampleObjectTD] | None
    examplePairings: dict[str, _OpenRpcExamplePairingObjectTD] | None
    contentDescriptors: dict[str, _OpenRcpContentDescriptorObjectTD] | None
    tags: dict[str, _OpenRpcTagTD] | None
