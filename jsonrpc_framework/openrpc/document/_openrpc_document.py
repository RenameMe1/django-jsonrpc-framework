from typing import Annotated, Any
from pydantic import ConfigDict, Field, field_validator, ValidationInfo

from jsonrpc_framework.openrpc.document._base import OpenRPCModel, OPENRPC_VERSION
from jsonrpc_framework.openrpc.document.info import OpenRpcInfo
from jsonrpc_framework.openrpc.document.external_docs import OpenRpcExternalDoc
from jsonrpc_framework.openrpc.document.server import OpenRpcServer
from jsonrpc_framework.openrpc.document.method import OpenRpcMethod
from jsonrpc_framework.openrpc.document.components import OpenRpcComponents


class OpenRpcDocument(OpenRPCModel):
    """This is the root object of the OpenRPC document. The contents of this
    object represent a whole OpenRPC document. How this object is constructed
    or stored is outside the scope of the OpenRPC Specification."""

    model_config = ConfigDict(extra="allow")

    @field_validator("*", mode="before")
    @classmethod
    def validate_x_fields(cls, v: Any, info: ValidationInfo) -> Any:
        if info.field_name == "__pydantic_extra__":
            if isinstance(v, dict):
                for key in v.keys():
                    if not key.startswith("x-"):
                        raise ValueError(
                            f"Invalid extra field: {key}, must start with 'x-'"
                        )

        return v

    openrpc: Annotated[
        str,
        Field(default=OPENRPC_VERSION),
        """REQUIRED. This string MUST be the semantic version number of the
        OpenRPC Specification version that the OpenRPC document uses.
        The openrpc field SHOULD be used by tooling specifications and clients
        to interpret the OpenRPC document. This is not related to the API
        info.version string.
        """,
    ] = OPENRPC_VERSION
    info: Annotated[
        OpenRpcInfo,
        """REQUIRED. The object provides metadata about the API. The metadata
        MAY be used by the clients if needed, and MAY be presented in editing
        or documentation generation tools for convenience.
        """,
    ]
    servers: Annotated[
        list[OpenRpcServer] | None,
        Field(default=None),
    ] = None
    methods: Annotated[
        list[OpenRpcMethod],
        Field(default_factory=list),
    ]
    components: Annotated[
        OpenRpcComponents | None,
        Field(default=None),
    ] = None
    external_docs: Annotated[
        OpenRpcExternalDoc | None,
        Field(
            serialization_alias="externalDocs",
            default=None,
        ),
        """Optional. Additional external documentation.
        """,
    ] = None
