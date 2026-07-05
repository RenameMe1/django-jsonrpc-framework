# Creating method

We have a several way to create the jsonrpc method

## Registering a method based on prefix


The BaseController define all methods startwith `method_` as jsonrpc method,
and registered its name without that prefix, see example below:

```python
from jsonrpc_framework import BaseConroller


class MyController(BaseController):
    def method_sync_example(self) -> str:
        return self._send("sync_example")

    async def method_async_example(self) -> str:
        return self._send("async_example")

    def _send(self, data: str) -> None:
        print(data)
```

The MyController registered two JSONRPC methods `sync_example` & `async_example`, method `_send`
doesn't registered as JSONRPC method and using as helpful func


## Use decorator to registring methods

We also could use decorator to regitering methods, the decorator use current 
method name to registered him, see example below:

``` python
from jsonrpc_framework import BaseController, jsonrpc_method

class MyController(BaseController):

    @jsonrpc_method
    def sync_example(self) -> str:
        return self._send("sync_example)
    
    @jsonrpc_method
    async def async_example(self) -> str:
        return self._send("sync_example)

    def _send(self, data: str) -> None
        print(data)

```

Now, The MyConroller also have two JSONRPC method `sync_example` & `async_example`

## Rename method name

The decorator `jsonrpc_method` also help you make special method name or just rename exist
method


``` python
from jsonrpc_framework import BaseController, jsonrpc_method

class MyController(BaseController):

    @jsonrpc_method("sync.send")
    def sync_example(self) -> str:
        return self._send("sync_example)
    
    @jsonrpc_method("async.send")
    async def async_example(self) -> str:
        return self._send("sync_example)

    def _send(self, data: str) -> None
        print(data)

```

In current state, MyController has two JSONRPC method named `sync.send` and `async.send`
