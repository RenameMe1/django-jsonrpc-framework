from typing import Annotated, NotRequired, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel

__all__ = [
    "OpenRpcExampleObject",
]


class _OpenRpcExampleObjectTD(TypedDict):
    summary: NotRequired[str]
    value: str
    description: NotRequired[str]
    name: str


class OpenRpcExampleObject(OpenRPCModel):
    """The Example object is an object that defines an example that is
    intended to match the schema of a given Content Descriptor.
    """

    summary: Annotated[
        str | None,
<<<<<<< HEAD
        Field(default=None, description=("Short description for the example..")),
=======
        Field(
            default=None, description=("Short description for the example..")
        ),
>>>>>>> 041d11d (Ruff format)
    ] = None
    value: Annotated[
        str,
        Field(
            description=(
                "REQUIRED. Embedded literal example. The value field and "
                "externalValue field are mutually exclusive. To represent "
                "examples of media types that cannot naturally represented "
                "in JSON, use a string value to contain the example, "
                "escaping where necessary."
            )
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "A verbose explanation of the example. GitHub Flavored "
                "Markdown syntax MAY be used for rich text representation.",
            ),
        ),
    ] = None
    name: Annotated[
        str,
        Field(
            description=("REQUIRED. Cannonical name of the example."),
        ),
    ]
