from jsonrpc_framework.core.error import InvalidRequestError, ParseError
from jsonrpc_framework.core.models import Notification, Request
from jsonrpc_framework.logic.validator import RequestValidator


def test_valid_single_request(
    validator: RequestValidator,
    valid_bytes_request: bytes,
) -> None:
    result = validator.validate_body(valid_bytes_request)

    assert isinstance(result, Request)

    assert result.jsonrpc == "2.0"
    assert result.method == "test"
    assert result.params == [1, 2, 3]
    assert result.id == 1


def test_valid_single_notification(
    validator: RequestValidator,
    valid_bytes_notification: bytes,
) -> None:
    result = validator.validate_body(valid_bytes_notification)

    assert isinstance(result, Notification)

    assert result.jsonrpc == "2.0"
    assert result.method == "test"
    assert result.params == [1, 2, 3]


def test_parse_error(
    validator: RequestValidator,
) -> None:
    result = validator.validate_body(b"invalid json")

    assert isinstance(result, ParseError)
    assert result.code == -32700
    assert result.message == "Parse error"


def test_validate_empty_batch(
    validator: RequestValidator,
) -> None:
    result = validator.validate_body(b"[]")

    assert isinstance(result, InvalidRequestError)
    assert result.code == -32600
    assert result.message == "Invalid request"


def test_validate_batch(
    validator: RequestValidator,
    valid_batch_contain_invalid_request: bytes,
) -> None:

    result = validator.validate_body(valid_batch_contain_invalid_request)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Request)
    assert isinstance(result[1], InvalidRequestError)


def test_validate_wrong_version(
    validator: RequestValidator,
    unsupported_version_request: bytes,
) -> None:
    result = validator.validate_body(unsupported_version_request)

    assert isinstance(result, InvalidRequestError)
    assert result.code == -32600
    assert result.message == "Invalid request"
