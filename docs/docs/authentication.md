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

See below how get access to different private levels

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
| Private   | ✅                        | ✅                         | ✅                            |
| Optional  | ✅                        | ❌                        | ✅                            |


All authorization error, return a Forbidden error, see example below

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32002,
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

Bearer authentification expected header "Authorization" with "Bearer <token>" content


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

All batch specification supported.

Every batch element authentification and authorization happen apart. One batch may contain as Success reposnses,
default jsonrpc Error so Authorization and authentification error. See example below.

```json
[
  {
    "jsonrpc": "2.0",
    "id": 1,
    "result": 7    // Successful response: e.g. calling `sum` method with params [3, 4]
  },
  {
    "jsonrpc": "2.0",
    "id": 2,
    "error": {
      "code": -32601,
      "message": "Method get_ntfund not found"
    }
  },
  {
    "jsonrpc": "2.0",
    "id": 3,
    "error": {
      "code": -32600,
      "message": "Invalid Request"
    }
  },
  {
    "jsonrpc": "2.0",
    "id": 4,
    "error": {
      "code": -32001,
      "message": "Unauthorized",
      "data": "Method get_smth is private and credentials are incorrect or not present"
    }
  },
  {
    "jsonrpc": "2.0",
    "id": 5,
    "error": {
      "code": -32002,
      "message": "Forbidden",
      "data": "Forbidden access to method update_smth"
    }
  }
]
```


### Notification behavior

According to the JSON-RPC specification, Notification requests do not return any response to the client, even in cases of authentication or authorization errors. No errors or results will be sent back for notifications, regardless of whether an error occurred during processing.

This behavior is also supported within batch requests: notification elements in a batch will not produce any responses, including when authentication or authorization fails for those elements.

### Creating your own backend

To create your own authentification backends you must follow next protocol examples:

``` python

from django.http import HttpRequest
from jsonrcp_framework.controller.auth import AuthResult

class BaseAuthentication(Protocol):
    def has_credentials(self, request: HttpRequest) -> bool:
        """
        Return True if user try to authenticate with this backend.
        Return False if user not try to authenticate with this backend.
        """
        ...

    def authenticate(self, request: HttpRequest) -> AuthResult | None:
        """
        If has_credentials returns True, this method must be called to authenticate the user.

        Return AuthResult if the user is authenticated, otherwise return None.
        """
        ...


class AsyncBaseAuthentication(Protocol):
    async def has_credentials(self, request: HttpRequest) -> bool:
        """
        Return True if user try to authenticate with this backend.
        Return False if user not try to authenticate with this backend.
        """
        ...

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        """
        If has_credentials returns True, this method must be called to authenticate the user.

        Return AuthResult if the user is authenticated, otherwise return None.
        """
        ...

```

Permission backends look like


``` python

from django.http import HttpRequest
from jsonrcp_framework.controller.auth import AuthResult, AccessPolicy

class BasePermission(Protocol):
    def has_permission(
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...


class AsyncBasePermission(Protocol):
    async def has_permission(
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...
```