from typing import Annotated, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel
<<<<<<< HEAD
from jsonrpc_framework.openrpc.document.common._example import OpenRpcExampleObject
from jsonrpc_framework.openrpc.document.common._reference import OpenRpcReferenceObject
from jsonrpc_framework.openrpc.document.common._example import _OpenRpcExampleObjectTD
from jsonrpc_framework.openrpc.document.common._reference import (
=======
from jsonrpc_framework.openrpc.document.common._example import (
    OpenRpcExampleObject,
    _OpenRpcExampleObjectTD,
)
from jsonrpc_framework.openrpc.document.common._reference import (
    OpenRpcReferenceObject,
>>>>>>> 041d11d (Ruff format)
    _OpenRpcReferenceObjectTD,
)

__all__ = [
    "OpenRpcExamplePairingObject",
]


class _OpenRpcExamplePairingObjectTD(TypedDict, total=False):
    name: str
    description: str | None
    params: list[_OpenRpcExampleObjectTD | _OpenRpcReferenceObjectTD]
    result: _OpenRpcExampleObjectTD | _OpenRpcReferenceObjectTD | None


class OpenRpcExamplePairingObject(OpenRPCModel):
    """The Example Pairing object consists of a set of example params and
    result. The result is what you can expect from the JSON-RPC service
    given the exact params.
    """

    name: Annotated[
        str,
        Field(description=("REQUIRED. Name for the example pairing.")),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            description=("A verbose explanation of the example pairing."),
        ),
    ] = None
    params: Annotated[
        list[OpenRpcExampleObject | OpenRpcReferenceObject],
        Field(description=("REQUIRED. Example parameters.")),
    ]
    result: Annotated[
        OpenRpcExampleObject | OpenRpcReferenceObject | None,
        Field(
            default=None,
            description=(
                "Example result. When not provided, the example pairing "
                "represents usage of the method as a notification."
            ),
        ),
    ] = None
