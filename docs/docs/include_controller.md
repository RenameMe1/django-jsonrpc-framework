# Include Controller

Sometimes we have purpose separate different methods to different controllers and 
use it in one JSONRPC endpoint, to solve this problem we could use `RouteController`, see example below

``` python

from django-jsonrpc import BaseController

class AccountController(BaseController)
    
    def method_rename_account(self): ...
    def method_delete_acoount(self): ...
```

``` python

from django-jsonrpc import RouteController, BaseController

class ProductController(BaseController)

    def method_order_product(self): ...
    def method_deliver_product(self): ...
    def method_pay_product(self): ...
```

After that, we just add `route` to `urls.py`

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

After all, we have a one contoller has, one entrypoint to all controllers methods.
