from typing import Any

from pydantic import BaseModel


class RpcError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class ParseError(RpcError):
    code: int = -32700
    message: str = "Parse error"


class InvalidRequestError(RpcError):
    # The JSON sent is not a valid Request object.
    code: int = -32600
    message: str = "Invalid request"


class MethodNotFoundError(RpcError):
    # The method does not exist / is not available.
    code: int = -32601
    message: str = "Method not found"


class InvalidParamsError(RpcError):
    # Invalid method parameter(s).
    code: int = -32602
    message: str = "Invalid params"


class InternalError(RpcError):
    # Internal JSON-RPC error.
    code: int = -32603
    message: str = "Internal error"


class ParseExcError(Exception): ...


class InvalidRequestExcError(Exception): ...
