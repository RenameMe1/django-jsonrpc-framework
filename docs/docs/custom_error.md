# Custom error

You can create your own error or use one that already exists in your code, see the example below.


``` python
from jsonrpc_framework import BaseController
from jsonrpc_framework.core import RpcError, InternalError


class DoesntSupportError(RpcError):
    code: int = -4000
    message: str = "Doesn't support"


class MyController(BaseController):
    def method_default_error(self) -> RpcError | ...:
        ...

        if flag:
            return InternalError(data="Doesn't support")

        ...

    def method_custom_error(self) -> RpcError | ...:
        ...

        if flag:
            return DoesntSupportError()

        ...
``` 
