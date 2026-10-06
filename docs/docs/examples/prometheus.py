import secrets
import sys

from django.conf import settings
from django.core.management import execute_from_command_line
from django.urls import path

from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.integration.prometheus import (
    MetricsView,
    enable_prometheus,
)

enable_prometheus()


if not settings.configured:
    settings.configure(
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS="*",
        DEBUG=True,
        INSTALLED_APPS=[
            "jsonrpc_framework",
        ],
        SECRET_KEY=secrets.token_hex(),
    )


class EchoController(BaseController):
    @jsonrpc_method
    def echo(self, name: str) -> str:
        return f"Echo {name}"


urlpatterns = [
    path("jsonrpc", EchoController.as_view()),
    path("metrics", MetricsView.as_view()),
]


if __name__ == "__main__":
    # Use `python THIS_FILE_NAME.py runserver` to run the example.
    execute_from_command_line(sys.argv)
