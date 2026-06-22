from django.conf import settings
from jsonrpc_framework.logic.responser import ResponseBuilder
from jsonrpc_framework.core.models import SuccessResponse
from jsonrpc_framework.core.error import MethodNotFoundError
from jsonrpc_framework.core.models import ErrorResponse

settings.configure()


def test_build_none_response(response_builder: ResponseBuilder) -> None:
    response = response_builder.build_response(None)

    assert response.status_code == 204
    assert response.content == b""


def test_success_response(response_builder: ResponseBuilder) -> None:
    response = response_builder.build_response(SuccessResponse(id=1, result=1))

    assert response.status_code == 200
    assert response.content == b'{"jsonrpc": "2.0", "result": 1, "id": 1}'


def test_error_response(response_builder: ResponseBuilder) -> None:
    response = response_builder.build_response(
        ErrorResponse(id="1", error=MethodNotFoundError(data="test"))
    )

    assert response.status_code == 200
    assert (
        response.content
        == b'{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found", "data": "test"}, "id": "1"}'
    )


def test_batch_response(response_builder: ResponseBuilder) -> None:
    response = response_builder.build_response(
        [
            SuccessResponse(id=1, result=1),
            ErrorResponse(id="2", error=MethodNotFoundError(data="test")),
        ]
    )

    assert response.status_code == 200
    assert (
        response.content
        == (
            '[{"jsonrpc": "2.0", "result": 1, "id": 1}, '
            '{"jsonrpc": "2.0", "error": '
            '{"code": -32601, "message": "Method not found", "data": "test"}, '
            '"id": "2"}]'
        ).encode()
    )
