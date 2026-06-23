from typing import Annotated, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel


class OpenRpcExternalDoc(OpenRPCModel):
    """
    Additional external documentation.
    """

    url: Annotated[
        str,
        Field(default="https://example.com/docs"),
        """The URL for the target documentation. Value MUST be in the format of a URL.
        """,
    ]
    description: Annotated[
        str | None,
        Field(default=None),
        """A verbose explanation of the documentation.
        SHOULD be in Markdown format for rich text representation.
        """,
    ] = None


class _OpenRpcExternalDocTD(TypedDict, total=False):
    description: str | None
    url: str
