# Authentication & Authorization

## Authentication

### Authentication levels

Methods have three access levels:

- **PUBLIC** (default for controller): Ordinary public method, always returns a result
- **PRIVATE**: Ordinary private method, returns a result only if authentication and authorization checks are successful
- **OPTIONAL**: Special level. If a request does not have credentials, the method behaves as PUBLIC (anonymous); if a request has credentials, the method behaves as PRIVATE

> [!WARNING]
> An OPTIONAL private level can expose your sensitive data. We created it for temporary use when you
> need to make an existing method private without blocking front-end development.

See below how to get access to different access levels.

| Level     | Access with credentials    | Access without credentials | Access with wrong credentials | 
| :---      | :---:                     | :---:                      | :---:                         | 
| Public    | ✅                        | ✅                        | ✅                            |
| Private   | ✅                        | ❌                        | ❌                            |
| Optional  | ✅                        | ✅                        | ❌                            |

### Authentication & Authorization matrix

All authentication errors return an Unauthorized error; see the example below.

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

See below when authorization checks occur.

| Level     |  with credentials    | without credentials | with wrong credentials | 
| :---      | :---:                     | :---:                     | :---:                        | 
| Public    | ❌                        | ❌                        | ❌                           |
| Private   | ✅                        | ✅                         | ✅                            |
| Optional  | ✅                        | ❌                        | ✅                            |


All authorization errors return a Forbidden error; see the example below.

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

If you use several auth or permission backends (or an empty list), this table helps to understand what is going on.

| Level             | All passed | One passed, other failed | All failed | Empty backends list |
| :---              | :---:      | :---:                    | :---:     |  :---:              |
| Authentication    | ✅         | ✅                       | ❌         |         ❌          |
| Authorization     | ✅         | ❌                       | ❌         |         ✅          |

As you can see, authentication uses OR, while authorization uses AND.

### Install with JWT support

Install extras to enable JWT support.


```
pip install django-jsonrpc-framework[jwt]
```

### Creating authentication backend

`BaseController` allows you to configure authentication settings. You can create your own authentication backend or use an existing one. Currently, only one backend is available: Bearer.

Bearer authentication expects the `Authorization` header with `Bearer <token>` content. Any issue raises an Unauthorized error.


First, create a `BearerToken` model to validate token content and a function to decode the token.


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

After that, create an authentication backend using a factory: `make_bearer_auth_backend` for sync implementation, `make_async_bearer_auth_backend` for async implementation. We create both for learning purposes. A controller supports both backend types (sync and async) at the same time.


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



After preparing authentication backends, we can use them in `BaseController`.

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
> Authentication checks follow the order of the structure you provide. If you use `list` or `tuple`, auth backends are executed from index `0` onward. If you use other `Sequence` structures, make sure you understand their element order.


The next step is to define an access level either at controller level or at method level.

Controller access level applies to all methods that do not have their own permission level.

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


You can also set up method-specific authentication backends; method authentication backends override controller rules.

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

Authorization setup looks similar to authentication setup.

First, create helper functions and permission backends using factories: `make_permission_backend` for a sync backend and `make_async_permission_backend` for an async backend.

``` python
from pydantic import BaseModel
from jsonrpc_framework.controller.auth.bearer import make_permission_backend, make_async_permission_backend


class BearerToken(BaseModel):
    sub: str
    admin: bool
    exp: float

def permission_checker(token: BearerToken) -> bool:
    return token.admin is True

async def async_permission_checker(token: BearerToken) -> bool:
    return token.admin is True

AdminPermission = make_permission_backend(
    token_model=BearerToken,
    permission_checker=permission_checker,
)


AsyncAdminPermission = make_async_permission_backend(
    token_model=BearerToken,
    permission_checker=async_permission_checker,
)
```

The next step is to add permission backends to your controller.


``` python

from jsonrpc_framework.controller.auth import AccessType
from jsonrpc_framework.controller import BaseController

class ControllerAccess(BaseController):
    default_access = AccessType.PRIVATE
    auth_backends = [SyncAuthBackend, AsyncAuthBackend]
    permission_backends = [AdminPermission, AsyncAdminPermission]

    def method_any(self) -> None: ...

```


You can also set up method-specific authorization backends; method authorization backends override controller rules.

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

The full batch specification is supported.

Authentication and authorization are performed independently for each batch element. One batch may contain successful responses, default JSON-RPC errors, authorization errors, and authentication errors. See the example below.

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

To create your own authentication backends, follow the protocol examples below:

``` python

from django.http import HttpRequest
from jsonrpc_framework.controller.auth import AuthResult

class BaseAuthentication(Protocol):
    def has_credentials(self, request: HttpRequest) -> bool:
        """
        Return True if the user tries to authenticate with this backend.
        Return False if the user does not try to authenticate with this backend.
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
        Return True if the user tries to authenticate with this backend.
        Return False if the user does not try to authenticate with this backend.
        """
        ...

    async def authenticate(self, request: HttpRequest) -> AuthResult | None:
        """
        If has_credentials returns True, this method must be called to authenticate the user.

        Return AuthResult if the user is authenticated, otherwise return None.
        """
        ...

```

> [!WARNING]
> Be careful when implementing `has_credentials`: if you use OPTIONAL access level,
> a mistake inside this method can open anonymous access to a method.

Permission backends look like this:


``` python

from django.http import HttpRequest
from jsonrpc_framework.controller.auth import AuthResult, AccessPolicy

class BasePermission(Protocol):
    def has_permission(
        self,
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...


class AsyncBasePermission(Protocol):
    async def has_permission(
        self,
        access_policy: AccessPolicy,
        request: HttpRequest,
        auth_result: AuthResult,
    ) -> bool:
        """
        Return True if the user has permission to access the handler, otherwise return False.
        """
        ...
```


> [!WARNING]
> Suppress all expected exceptions in backends to return `False`. The runner does not treat backend exceptions as `False` results.
