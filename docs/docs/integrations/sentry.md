# Sentry

Jsonrpc_framework has ourself Sentry integration. To enable it:

- Intall sentry package

```
pip install django-jsonrpc-framework[sentry]
```

- Enable sentry configuration


```
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from jsonrpc_framework.integration.sentry import JsonRpcIntegration

if dsn := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            DjangoIntegration(),
            JsonRpcIntegration(),
        ],
    )
```
