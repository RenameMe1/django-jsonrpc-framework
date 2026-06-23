import json
from typing import Any

from pydantic import ValidationError

from jsonrpc_framework.core.error import (
    InvalidRequestError,
    ParseError,
    RpcError,
)
from jsonrpc_framework.core.models import Notification, Request

type RequestType = Request | Notification
type BatchType = list[Request | Notification | RpcError]


class RequestValidator:
<<<<<<< HEAD
    def validate_body(self, body: bytes | Any) -> RequestType | BatchType | RpcError:
=======
    def validate_body(
        self, body: bytes | Any
    ) -> RequestType | BatchType | RpcError:
>>>>>>> 041d11d (Ruff format)
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError:
            return ParseError(data="Invalid JSON")

        if json_body == []:
            return InvalidRequestError(data="Empty batch")

        if isinstance(json_body, dict):
            return self._validate_single(json_body)
        elif isinstance(json_body, list):
            return self._validate_batch(json_body)

        return InvalidRequestError(
            data=f"Invalid JSON-RPC request body {type(json_body)}, expected dict or list"
        )

    def _validate_batch(self, json_body: list[Any]) -> BatchType:
        batch: BatchType = []

        for item in json_body:
            if not isinstance(item, dict):
                batch.append(
                    InvalidRequestError(
                        data=f"Invalid JSON-RPC request body {type(item)}, expected dict"
                    )
                )
            else:
                batch.append(self._validate_single(item))

        return batch

    def _validate_single(
        self, json_body: dict[str, Any]
    ) -> RequestType | RpcError:

        try:
            request = self._validate_request_type(json_body)
        except ValidationError:
            return InvalidRequestError()

        return request

    def _validate_request_type(self, json_body: dict[str, Any]) -> RequestType:
        if json_body.get("id") is None:
            return Notification.model_validate(json_body)
        else:
            return Request.model_validate(json_body)
