from typing import Annotated, Any, Literal, TypedDict, is_typeddict

from pydantic import BeforeValidator, Field

from jsonrpc_framework.openrpc.document._base import OpenRPCModel

__all__ = [
    "OpenRpcRefSchema",
    "OpenRpcSchema",
]


def validate_type(v: Any) -> str:
    if isinstance(v, str):
        return "string"
    elif isinstance(v, int):
        return "integer"
    elif isinstance(v, float):
        return "number"
    elif isinstance(v, bool):
        return "boolean"
    elif isinstance(v, list):
        return "array"
    elif isinstance(v, dict) or isinstance(v, type) or is_typeddict(v):
        return "object"
    else:
        raise ValueError(f"Invalid type: {type(v)}")


_OpenRpcSchemaTD = TypedDict(
    "_OpenRpcSchemaTD",
    {
        "type": Literal[
            "string", "integer", "number", "boolean", "array", "object"
        ],
        "required": list[str] | None,
        "properties": dict[str, dict[str, str]] | None,
        "$ref": str | None,
    },
    total=False,
)


class OpenRpcDataSchema(OpenRPCModel):
    type: Annotated[str, BeforeValidator(validate_type)]
    required: list[str] | None = None
    properties: dict[str, dict[str, str]] | None = None


class OpenRpcRefSchema(OpenRPCModel):
    ref: Annotated[str, Field(serialization_alias="$ref")]


class OpenRcpTypeSchema(OpenRPCModel):
    type: Literal["string", "integer", "number", "boolean", "array", "object"]


type OpenRpcSchema = OpenRpcDataSchema | OpenRpcRefSchema | OpenRcpTypeSchema
