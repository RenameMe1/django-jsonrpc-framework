# Include Controller

Sometimes we need to separate methods into different controllers and
use them in one JSON-RPC endpoint. To solve this problem, we can use `RouteController`, see the example below.

``` python

from django-jsonrpc import BaseController

class AccountController(BaseController):
    
    def method_rename_account(self): ...
    def method_delete_account(self): ...
```

``` python

from django-jsonrpc import RouteController, BaseController

class ProductController(BaseController):

    def method_order_product(self): ...
    def method_deliver_product(self): ...
    def method_pay_product(self): ...
```

After that, we just add `route` to `urls.py`.

``` python
from django.urls import path

from jsonrpc_framework.controller import RouteController

from .product import ProductController
from .account import AccountController

route = RouteController(
    path="jsonrpc",
    controllers=[
        ProductController,
        AccountController,
    ],
)

urlpatterns = [
    path(route.path, route.as_view()),
]
```

As a result, we have one controller entry point for methods from multiple controllers.
