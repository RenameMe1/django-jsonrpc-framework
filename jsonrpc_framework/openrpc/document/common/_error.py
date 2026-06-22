from typing import Annotated, Any, TypedDict
from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel

__all__ = [
    "OpenRpcErrorObject",
]


class _OpenRpcErrorObjectTD(TypedDict):
    code: int
    message: str
    data: Any | None


class OpenRpcErrorObject(OpenRPCModel):
    """Defines an application level error."""

    code: Annotated[
        int,
        """REQUIRED. A Number that indicates the error type that occurred.
        This MUST be an integer. The error codes from and including -32768
        to -32000 are reserved for pre-defined errors. These pre-defined
        errors SHOULD be assumed to be returned from any JSON-RPC api.
        """,
    ]
    message: Annotated[
        str,
        """REQUIRED. A String providing a short description of the error.
        The message SHOULD be limited to a concise single sentence.
        """,
    ]
    data: Annotated[
        Any | None,
        Field(default=None),
        """A Primitive or Structured value that contains additional
        information about the error. This may be omitted. 
        The value of this member is defined by the Server (e.g. detailed error 
        information, nested errors etc.).
        """,
    ] = None
