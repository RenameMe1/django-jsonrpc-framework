# Creating method

We have several ways to create JSON-RPC methods.

## Registering a method based on prefix


`BaseController` defines all methods that start with `method_` as JSON-RPC methods,
and registers their names without that prefix, see the example below:

```python
from jsonrpc_framework import BaseController


class MyController(BaseController):
    def method_sync_example(self) -> str:
        return self._send("sync_example")

    async def method_async_example(self) -> str:
        return self._send("async_example")

    def _send(self, data: str) -> None:
        print(data)
```

`MyController` registers two JSON-RPC methods: `sync_example` and `async_example`.
The `_send` method is not registered as a JSON-RPC method and is used as a helper function.


## Using a decorator to register methods

We can also use a decorator to register methods. The decorator uses the current
method name to register it, see the example below:

``` python
from jsonrpc_framework import BaseController, jsonrpc_method

class MyController(BaseController):

    @jsonrpc_method
    def sync_example(self) -> str:
        return self._send("sync_example")
    
    @jsonrpc_method
    async def async_example(self) -> str:
        return self._send("async_example")

    def _send(self, data: str) -> None:
        print(data)

```

Now, `MyController` also has two JSON-RPC methods: `sync_example` and `async_example`.

## Rename method name

The `jsonrpc_method` decorator also helps you set a custom method name or rename an existing
method.


``` python
from jsonrpc_framework import BaseController, jsonrpc_method

class MyController(BaseController):

    @jsonrpc_method("sync.send")
    def sync_example(self) -> str:
        return self._send("sync_example")
    
    @jsonrpc_method("async.send")
    async def async_example(self) -> str:
        return self._send("async_example")

    def _send(self, data: str) -> None:
        print(data)

```

At this point, `MyController` has two JSON-RPC methods named `sync.send` and `async.send`.
