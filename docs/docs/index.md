# Getting Started

## Instalation 

```
pip install django-jsonrpc
```

## Quickstart

To quickstart we create a single page Django Application

``` python
import secrets
import sys
import uuid

import pydantic
from django.conf import settings
from django.core.management import execute_from_command_line
from django.urls import include, path

from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method

if not settings.configured:
    settings.configure(
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS="*",
        DEBUG=False,
        INSTALLED_APPS=["django_jsonrpc", "django.contrib.staticfiles"],
        STATIC_URL="/static/",
        STATICFILES_FINDERS=[
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ],
        TEMPLATES=[
            {
                "APP_DIRS": True,
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            },
        ],
        # Secret key for tests, will be new on each run,
        # in production it must be the same token, kept in secret:
        SECRET_KEY=secrets.token_hex(),
    )


class EchoController(BaseController):
    async def method_echo1(self, *name: tuple[str]) -> str:
        return f"Echo first {name}"

    @jsonrpc_method
    def echo2(self) -> str:
        return "Echo second"

    @jsonrpc_method("echo3")
    def wrong_name(self) -> str:
        return "Echo third"


urlpatterns = [
    path(EchoController.path, EchoController.as_view()),
]

if __name__ == "__main__":
    # Use `python THIS_FILE_NAME.py runserver` to run the example.
    execute_from_command_line(sys.argv)
```

After create single file app, just run it

```
python single_file_asgi.py runserver
```