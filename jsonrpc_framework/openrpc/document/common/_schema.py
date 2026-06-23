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
<<<<<<< HEAD
    elif isinstance(v, dict):
        return "object"
    elif isinstance(v, type):
        return "object"
    elif is_typeddict(v):
=======
    elif isinstance(v, dict) or isinstance(v, type) or is_typeddict(v):
>>>>>>> 041d11d (Ruff format)
        return "object"
    else:
        raise ValueError(f"Invalid type: {type(v)}")


_OpenRpcSchemaTD = TypedDict(
    "_OpenRpcSchemaTD",
    {
<<<<<<< HEAD
        "type": Literal["string", "integer", "number", "boolean", "array", "object"],
=======
        "type": Literal[
            "string", "integer", "number", "boolean", "array", "object"
        ],
>>>>>>> 041d11d (Ruff format)
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
