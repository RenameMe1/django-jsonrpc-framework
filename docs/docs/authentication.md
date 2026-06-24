# Authentication & Autorization

## Authentication

### Authentification levels

Methods has three private levels:

- **PUBLIC** (Default to controller): Ordinary public method, always glad to return result
- **PRIVATE**: Ordinary private controller, return result only if authentification and authorization cheks is successful
- **OPTIONAL**: Specical level. If request don't have credentials make method PUBLIC, if request have credentials make method PRIVATE

> [!WARNING]
> An OPTIONAL private level can expose your sensitive data. We created it for temporary use when you
> need to make an existing method private without blocking front-end development.

See below when occir authentification checks

| Level     | Acess with credentials    | Acess without credentials | Acess with wrong credentials | 
| :---      | :---:                     | :---:                      | :---:                         | 
| Public    | ✅                        | ✅                        | ✅                            |
| Private   | ✅                        | ❌                        | ❌                            |
| Optional  | ✅                        | ✅                        | ❌                            |

### Authentification & Authorization matrix

All authorize error, return Unathorized error, see example below

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Unauthorized",
    "data": "Method {__name__} is private and credentials are incorrect or not present"
  }
}
```

See below when occur authorization checks

| Level     |  with credentials    | without credentials | with wrong credentials | 
| :---      | :---:                     | :---:                     | :---:                        | 
| Public    | ❌                        | ❌                        | ❌                           |
| Private   | ✅                        | ❌                        | ❌                           |
| Optional  | ✅                        | ❌                        | ❌                           |


All authorization error, return a Forbidden error, see example below

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32003,
    "message": "Forbidden",
    "data": "Forbidden access to method {__name__}"
  }
}

```


### Checks 

If you use several or empty auth and authorize backend, this table will be helpful to understading what going on.

| Level             | All passed | One passed Other fauled | All Failed | empty backends list |
| :---              | :---:      | :---:                    | :---:     |  :---:              |
| Authentification  | ✅         | ✅                       | ❌         |         ❌          |
| Authorization     | ✅         | ❌                       | ❌         |         ✅          |

### install with JWT support

Install extras to enable support JWT


```
pip install django-jsonrpc-framework[jwt]
```

### Creating authentification backend

The `BaseController` has possibility to set up authentification settings. You can create your own authorization backend, or use existing. Currenty ready only one backend - Bearer


Firstly we create a BearerToken model to validate token content, and create
a function to decode our token


``` python
from pydantic import BaseModel

class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float

def jwt_decoder(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, key=test_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None

async def async_jwt_decoder(token: str) -> dict[str, Any] | None:
    # You can use await in this func
    try:
        return jwt.decode(token, key=test_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None

```

After that we create a authentification backend using a factory: `make_bearer_auth_backend` - to sync implementation, `make_async_bearer_auth_backend` - to async implementation. We create both to learning goal.


```python
from jsonrpc_framework.controller.auth.bearer import make_bearer_auth_backend, make_async_bearer_auth_backend

SyncAuthBackend = make_bearer_auth_backend(
    token_model=BearerToken,
    token_decoder=jwt_decoder,
    )
AsyncAuthBackend = make_async_bearer_auth_backend(
    token_model=BearerToken,
    token_decoder=async_jwt_decoder,
)
```



After preparing our authentification backend, we can use its to BaseControllers

``` python

    from jsonrpc_framework.controller._base import BaseController

    class TestController(BaseController):
        auth_backends = [SyncAuthBackend, AsyncAuthBackend]

```

> [!WARNING]
> Access to a private method is granted if at least one of the specified auth_backends successfully authenticates the 
request.

> [!NOTE]
> Currently, there is no support for requiring approval from all specified auth_backends. Access to a private method is granted if at least one of the provided auth_backends successfully authenticates the request.

> [!WARNING]
> Authentification checks use in order their structure. If you use `list` or `tuple` auth backend will be execute from 0 to .... If you use other Sequence structures, please be sure you understand their elements order.


Following step we need define private level on Controller level either method level.

Controller access level apply to all methods which doesn't have a its own permission level

``` python

from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController

class ControllerAccess(BaseController):
    default_access = AccessType.PRIVATE
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]

    def method_any(self) -> None: ...

```

``` python
from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method

class MethodAccess(BaseController):
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]

    @jsonrpc_method(access=AccessType.PRIVATE)
    def method_any(self) -> None: ...

```


Also you can set up method specific authentification backends, method authentification backends
rewrite Controller rules.

``` python
from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method

class MethodAccess(BaseController):
    default_access = AccessType.PRIVATE
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]

    @jsonrpc_method(auth=[SyncAuthBackend])
    def method_sync(self) -> None: ...

    @jsonrpc_method(auth=[AsyncAuthBackend])
    async def method_async(self) -> None: ...

    @jsonrpc_method # both auth will be used
    def method_default(self) -> None: ...

```

## Authorization

Set up authorization looks like setup authentification.

Firstly we creaete a helper functions and create Permission backens using a factory: `make_permission_backend` - to sync backend and `make_async_permission_backend` to create async backend.

``` python
from pydantic import BaseModel
from jsonrpc_framework.controller.auth.bearer import make_permission_backend, make_async_permission_backend


class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float

def permission_checker(token: BearerToken) -> bool:
    return token.admin is True

async def async_permission_cheker(token: BearerToken) -> bool:
    return token.admin is True

AdminPermission = make_permission_backend(
    token_model=BearerToken,
    permission_checker=permission_checker,
)


AsyncAdminPermission = make_async_permission_backend(
    token_model=BearerToken,
    permission_checker=async_permission_cheker,
)
```

Next step add permittion backends to your Controller


``` python

from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController

class ControllerAccess(BaseController):
    default_access = AccessType.PRIVATE
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]
    permission_backends = [AdminPermission, AsyncAdminPermission]

    def method_any(self) -> None: ...

```


Also you can set up method specific authorization backends, method authorization backends
rewrite Controller rules.

``` python
from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method

class MethodAccess(BaseController):
    default_access = AccessType.PRIVATE
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]
    permission_backends = [AdminPermission, AsyncAdminPermission]

    @jsonrpc_method(permissions=[AdminPermission])
    def method_sync(self) -> None: ...

    @jsonrpc_method(permissions=[AsyncAdminPermission])
    async def method_async(self) -> None: ...

    @jsonrpc_method # Both permissions will be used
    def method_default(self) -> None: ...

```


### Batch support

