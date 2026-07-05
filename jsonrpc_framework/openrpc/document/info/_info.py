from typing import Annotated, TypedDict

from pydantic import Field

from jsonrpc_framework.openrpc.document._base import (
    OPENRPC_VERSION,
    OpenRPCModel,
)


class OpenRpcLicense(OpenRPCModel):
    """
    License information for the exposed API.
    """

    name: Annotated[
        str,
        """The license name used for the API.
        """,
    ]
    url: Annotated[
        str | None,
        Field(default=None),
        """A URL to the license used for the API. MUST be in the format of a URL.
        """,
    ] = None


class _OpenRpcLicesnceTD(TypedDict, total=False):
    name: str
    url: str | None


class OpenRpcContact(OpenRPCModel):
    """
    Contact information for the exposed API.
    """

    name: Annotated[
        str,
        """The identifying name of the contact person/organization.
        """,
    ]
    email: Annotated[
        str | None,
        Field(default=None),
        """The email address of the contact person/organization. MUST be in the format of an email address.
        """,
    ] = None
    url: Annotated[
        str | None,
        Field(default=None),
        """The URL pointing to the contact information. MUST be in the format of a URL.
        """,
    ] = None


class _OpenRpcContactTD(TypedDict, total=False):
    name: str
    email: str | None
    url: str | None


class OpenRpcInfo(OpenRPCModel):
    """
    The object provides metadata about the API. The metadata MAY be used by
    the clients if needed, and MAY be presented in editing or documentation
    generation tools for convenience.
    """

    title: Annotated[
        str,
        Field(default="OpenRPC API"),
        """REQUIRED. The title of the application.
        """,
    ] = "OpenRPC API"
    description: Annotated[
        str | None,
        Field(default=None),
        """A verbose description of the application.
        Should be used in Markdown format for rich text representation.
        """,
    ] = None
    terms_of_service: Annotated[
        str | None,
        Field(
            default=None,
            serialization_alias="termsOfService",
        ),
        """A URL to the Terms of Service for the API.
        """,
    ] = None
    version: Annotated[
        str,
        Field(default=OPENRPC_VERSION),
        """REQUIRED. The version of the OpenRPC document.
        """,
    ] = OPENRPC_VERSION
    contact: Annotated[
        OpenRpcContact | None,
        Field(default=None),
        """Optional. Contact information for the exposed API.
        """,
    ] = None
    license: Annotated[
        OpenRpcLicense | None,
        Field(default=None),
        """Optional. License information for the exposed API.
        """,
    ] = None


class _OpenRpcInfoTD(TypedDict, total=False):
    title: str
    description: str | None
    termsOfService: str | None
    version: str
    contact: _OpenRpcContactTD | None
    license: _OpenRpcLicesnceTD | None
