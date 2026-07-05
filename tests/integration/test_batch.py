from django.test import Client

# Specification batch tests


def test_all_notifications_batch(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json=[
            {"jsonrpc": "2.0", "method": "test"},
            {
                "jsonrpc": "2.0",
                "method": "test_positional_params",
                "params": [1, 2, 3],
            },
        ],
    )
    assert response.status_code == 204
    assert response.content == b""


def test_batch(client: Client) -> None:
    response = client.post(
        "/jsonrpc",
        json=[
            {
                "jsonrpc": "2.0",
                "method": "test_positional_params",
                "params": [1, 2, 3],
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "method": "test_positional_params",
                "params": [4],
            },
            {
                "jsonrpc": "2.0",
                "method": "test_positional_params",
                "params": [1, 2],
                "id": 3,
            },
            {"foo": "bar"},
            {
                "jsonrpc": "2.0",
                "method": "method.not.found",
                "params": [1, 2, 3],
                "id": 2,
            },
            {"jsonrpc": "2.0", "method": "sum", "params": [5, 6, 7], "id": 5},
        ],
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "jsonrpc": "2.0",
            "result": "test_positional_params: (1, 2, 3)",
            "id": 1,
        },
        {"jsonrpc": "2.0", "result": "test_positional_params: (1, 2)", "id": 3},
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid request",
                "data": None,
            },
            "id": None,
        },
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": "Method method.not.found not found",
            },
            "id": 2,
        },
        {"jsonrpc": "2.0", "result": 18, "id": 5},
    ]


def test_invalid_batch(client: Client) -> None:
    response = client.post("/jsonrpc", json=[1, 2, 3])

    assert response.status_code == 200
    assert response.json() == [
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid request",
                "data": "Invalid JSON-RPC request body <class 'int'>, expected dict",
            },
            "id": None,
        },
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid request",
                "data": "Invalid JSON-RPC request body <class 'int'>, expected dict",
            },
            "id": None,
        },
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid request",
                "data": "Invalid JSON-RPC request body <class 'int'>, expected dict",
            },
            "id": None,
        },
    ]


def test_batch_with_one_invalid_request(client: Client) -> None:
    response = client.post("/jsonrpc", json=[1])

    assert response.status_code == 200
    assert response.json() == [
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid request",
                "data": "Invalid JSON-RPC request body <class 'int'>, expected dict",
            },
            "id": None,
        },
    ]


def test_empty_batch(client: Client) -> None:
    response = client.post("/jsonrpc", json=[])

    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32600,
            "message": "Invalid request",
            "data": "Empty batch",
        },
        "id": None,
    }


def test_batch_with_invalid_json(client: Client) -> None:

    response = client.post(
        "/jsonrpc",
        data=(
            "["
            '{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},'
            '{"jsonrpc": "2.0", "method"'
            "]"
        ),
        content_type="application/json",
    )

    assert response.json() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32700,
            "message": "Parse error",
            "data": "Invalid JSON",
        },
        "id": None,
    }
    assert response.status_code == 200


# Custom batch tests
