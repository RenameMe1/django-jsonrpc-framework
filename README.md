# Django jsonrpc implementation

## Install

```
pip install django-jsonrpc-framework
```

## Advantages

- Complete support for JSON-RPC 2.0 (Request, Notification, Batch)
- Auto-generation of `openrpc.json` (OpenRPC 1.3.2)
- Auto-generation of OpenRPC documentation (like Swagger)
- Async support

## Create methods

We provide several ways to create methods.

- Using `method_` prefix
- Using `jsonrpc_method` decorator
- Rename an existing function to a new name

``` python
from jsonrpc_framework import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method


class EchoController(BaseController):
    def method_echo_hello(self, name: str) -> str:
        return f"hello {name}"

    @jsonrpc_method
    def echo_goodbye(self, name: str) -> str:
        return f"goodbye {name}"

    @jsonrpc_method("echo_see_you")
    def wrong_name(self, name) -> str:
        return "See you from echo_see_you method"
```

## Adding several controllers to one controller

``` python
from jsonrpc_framework import RouteController


class PrintController(BaseController):
    async def method_print_hello(self, name) -> None:
        print(f"hello {name}")

    @jsonrpc_method
    async def print_goodbye(self, name) -> None:
        print(f"goodbye {name}")


route = RouteController(
    "jsonrpc",
    controllers=[
        PrintController,
        EchoController,
    ],
)
```

## Generating openrpc.json and OpenRPC documentation

``` python
from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector

collector = OpenRpcCollector(
    PrintController, EchoController, title="My mini API"
)


urlpatterns = [
    path("echorpc", EchoController, as_view),
    path("jsonrpc", route.as_view()),
    path("openrpc.json", OpenRpcJsonView.as_view(collector=collector)),
    path("docs", OpenRpcDocView.as_view()),
]
```

### OpenRPC.json example

![OpenRPC docs](docs/docs/openrpcjson.png)

## OpenRPC doc example

![OpenRPC docs](docs/docs/docs.png)
