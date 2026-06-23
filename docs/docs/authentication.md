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

### Creating authentification backend

The `BaseController` has possibility to set up authentification settings. You can create your own authorization backend, or use existing. Currenty ready only one backend - Bearer

Install extras to enable support JWT


```
pip install django-jsonrpc-framework[jwt]
```

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

```

    from jsonrpc_framework.controller._base import BaseController

    class TestController(BaseController):
        auth_backends = [SyncAuthBackend, AsyncAuthBackend]

```

