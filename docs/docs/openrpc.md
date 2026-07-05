# OpenRpc

Django-jsonrpc has a complete implementation of the OpenRPC 1.3.2 specification using `Pydantic`.

!!! warning
    But only a small part is connected with the user API, see the table below.
 
 | Part of documentation specification    | Implementation Status | 
 | ---------------------------------------| -------------------- |
 | Info                                   | Full                 |
 | Servers                                | None                 |
 | Methods                                | Partially            |
 | Components                             | Only for library use |
 | externalDocs                           | None


## How to enable

The OpenRPC documentation works only if you have an OpenRPC JSON view. Let's connect it first.

``` python
from jsonrpc_framework.controller.openrpc._openrpc import OpenRpcJsonView, OpenRpcDocView
from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector

collector = OpenRpcCollector(EchoController)

urlpatterns = [
    ...
    path('openrpc.json', OpenRpcJsonView.as_view(collector=collector)),
]
```

The `OpenRpcCollector` creates a JSON structure of your API and provides it to your endpoint using `OpenRpcJsonView`.

The next step is connecting `OpenRpcDocView`, which uses `/openrpc.json` to
render your API visualization. Just add it below.

``` python
urlpatterns = [
    ...
    path('openrpc.json', OpenRpcJsonView.as_view(collector=collector)),
    path('docs', OpenRpcDocView.as_view()),
]
```

### Pre-generation openrpc file

To improve startup performance, you can pre-generate your schema
to decrease your application's startup time.

Just use this command with your arguments.

```
python manage.py generate_openrpc --collector myproject.openrpc.collector --output my_openrpc.json
```

Next, set up the file path setting.

```
DJANGO_JSONRPC_DOCS: {
    "SCHEMA_PATH": "my_openrpc.json"
}
```


### Custom path to openrpc file

If you have another endpoint for your `openrpc.json` file, you need to change
`OpenRpcDocView` settings to your path.

```
DJANGO_JSONRPC_DOCS: {
    "SCHEMA_PATH": "my_path/openrpc.json"
}
```

## Info

While creating an `OpenRpcCollector`, you can define `Info` about
your project, see below.

``` python
from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector
from jsonrpc_framework.openrpc.document.info import OpenRpcContact, OpenRpcLicense

class EchoController(BaseController):

    def method_echo1(self, *name: tuple[str]) -> str:
        return f"Echo first {name}"

collector = OpenRpcCollector(
    EchoController,
    title="Echo Api",
    version="1.0.0",
    description="API echo methods",
    terms_of_service="https://example.com/terms_of_service",
    contact=OpenRpcContact(name="ExampleName", email="expert@example.com", url="https://example.com/contact"),
    license=OpenRpcLicense(name="Example License", url="https://example.com/license"),
)
```

After opening the docs page, you should see the result below. If loading takes too long,
you may have a problem with CDN access, try disabling VPN or use
self-hosted CDN files.

![OpenRPC docs](./docs.png)
