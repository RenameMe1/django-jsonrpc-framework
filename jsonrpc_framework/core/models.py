from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel

from jsonrpc_framework.core.error import RpcError

JSON_RPC_VERSION = "2.0"

type IdType = int | str | None
type ParamType = list[Any] | dict[str, Any] | None
type MethodType = str
type Response = SuccessResponse | ErrorResponse


def _ensure_version(value: str) -> str:
    if value == JSON_RPC_VERSION:
        return value
    raise ValueError(f"Jsonrpc version must be {JSON_RPC_VERSION}")


class _JsonRpcVersion(BaseModel):
    jsonrpc: Annotated[str, AfterValidator(_ensure_version)] = "2.0"


class Request(_JsonRpcVersion):
    method: MethodType
    params: ParamType = None
    id: IdType


class Notification(_JsonRpcVersion):
    method: MethodType
    params: ParamType = None


class SuccessResponse(_JsonRpcVersion):
    result: Any
    id: IdType


class ErrorResponse(_JsonRpcVersion):
    error: RpcError
    id: IdType
