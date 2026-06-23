from typing import Annotated, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel


class OpenRpcServerObjectVariable(OpenRPCModel):
    """An object representing a Server Variable for server URL
    template substitution.
    """

    default: Annotated[
        str,
        """REQUIRED. The default value to use for substitution, which
        SHALL be sent if an alternate value is not supplied. Note this 
        behavior is different than the Schema Object's treatment of 
        default values, because in thise cases parameter values are optional.
        """,
    ]
    description: Annotated[
        str | None,
        Field(default=None),
        """An optional description for the server variable. Should used 
        the MARKDOWN format for rich text representation.
        """,
    ]
    enum: Annotated[
        list[str],
        """An enumeration of string values to be used if the substitution 
        options are from a liimited set.
        """,
    ]


class _OpenRpcServerObjectVariableTD(TypedDict, total=False):
    default: str
    description: str | None
    enum: list[str]


class OpenRpcServer(OpenRPCModel):
    """A object representing a Server."""

    url: Annotated[
        str,
        Field(default="https://example.com/api"),
        """REQUIRED. A URL to the target host. 
        This URL supports Server Variables and MAY be relative, to indicate
        that the host location is relative to the location where the OpenRPC
        document is being served. Server Variables are passed into the runtime
        expression to produce a server URL.
        """,
    ] = "https://example.com/api"
    name: Annotated[
        str | None,
        Field(default=None),
        """An optional string describing the name of the server. Should used 
        the MARKDOWN format for rich text representation.
        """,
    ] = None
    description: Annotated[
        str | None,
        Field(default=None),
        """An optional string describing the host designated by the URL. 
        Should be in the MARKDOWN format for rich text representation.
        """,
    ] = None
    summary: Annotated[
        str | None,
        Field(default=None),
        """A short summary of what the server is.
        """,
    ] = None
    variables: Annotated[
        dict[str, OpenRpcServerObjectVariable] | None,
        Field(default=None),
        """A map between a variable name and its value.
        The value is passed into the Runtime Expression to produce a server URL.
        """,
    ] = None


class _OpenRpcServerTD(TypedDict, total=False):
    url: str
    name: str | None
    description: str | None
    summary: str | None
    variables: dict[str, _OpenRpcServerObjectVariableTD] | None
