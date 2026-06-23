from django.test import Client

# Specification request tests


def test_invalid_request_object(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json={"jsonrpc": "2.0", "method": 1, "params": "bar"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "error": {"code": -32600, "message": "Invalid request", "data": None},
        "id": None,
    }


def test_prc_call_with_invalid_json(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        data='{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]',
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32700,
            "message": "Parse error",
            "data": "Invalid JSON",
        },
        "id": None,
    }


def test_call_non_existent_method(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "non_existent_method",
            "params": [1, 2, 3],
            "id": 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found",
            "data": "Method non_existent_method not found",
        },
        "id": 1,
    }


def test_notification_call(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json={"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 3]},
    )
    assert response.status_code == 204
    assert response.content == b""


def test_call_with_named_params(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "test_named_params",
            "params": {"a": 1, "b": 2, "c": 3},
            "id": 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "result": 6,
        "id": 1,
    }


def test_call_with_positional_params(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "test_positional_params",
            "params": [1, 2, 3],
            "id": 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "result": "test_positional_params: (1, 2, 3)",
        "id": 1,
    }


# Custom request tests
