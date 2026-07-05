import secrets
import sys
from typing import TypedDict

from django.conf import settings
from django.core.management import execute_from_command_line
from django.urls import path

from jsonrpc_framework.controller import BaseController
from jsonrpc_framework.controller.decor import jsonrpc_method
from jsonrpc_framework.controller.openrpc._openrpc import (
    OpenRpcDocView,
    OpenRpcJsonView,
)
from jsonrpc_framework.controller.openrpc.collectors import OpenRpcCollector
from jsonrpc_framework.core.error import RpcError
from jsonrpc_framework.openrpc.document.info import (
    OpenRpcContact,
    OpenRpcLicense,
)


class CustomError(RpcError):
    code: int = -4000
    message: str = "Custom error"


if not settings.configured:
    settings.configure(
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS="*",
        DEBUG=True,
        INSTALLED_APPS=[
            "django_jsonrpc",
            "django.contrib.staticfiles",
        ],
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
        SECRET_KEY=secrets.token_hex(),
        DJANGO_JSONRPC_DOCS={
            "FILE_PATH": "openrpc.json",
            "THEME_MODE": "dark",
            "SCHEMA_PATH": "/openrpc.json",
        },
    )


class TypedResult(TypedDict):
    name: str
    age: int


class TypedParams(TypedDict):
    name: str
    age: int


class EchoController(BaseController):
    # async def method_echo1(self, *name: tuple[str]) -> str:
    #     """Echo first"""
    #     return f"Echo first {name}"

    # @jsonrpc_method
    # def echo2(self) -> str:
    #     """SIMPLE"""
    #     return "Echo second"

    # @jsonrpc_method(
    #     "echo3",
    #     tags=['test'])
    # def wrong_name(self) -> str:
    #     """DOCA DOCA"""
    #     return "Echo third"

    @jsonrpc_method(
        "printing",
        summary="Printing",
        description="Printing description",
        tags=["test", "test2"],
    )
    def printing(self, name: str, count: int = 0) -> str:
        return f"Printing {name} {count} times"

    @jsonrpc_method
    def typed_dict(
        self,
        data: TypedParams,
    ) -> TypedResult | CustomError:

        if data["name"] == "error":
            return CustomError(data="Custom error")

        return {
            "name": "John",
            "age": 20,
        }


collector = OpenRpcCollector(
    EchoController,
    title="Test API",
    version="1.0.0",
    description="Test API description",
    terms_of_service="https://example.com/terms_of_service",
    contact=OpenRpcContact(
        name="Test API contact name",
        email="test@example.com",
        url="https://example.com/contact",
    ),
    license=OpenRpcLicense(
        name="Test API license name", url="https://example.com/license"
    ),
)

urlpatterns = [
    path("jsonrpc", EchoController.as_view()),
    path("openrpc.json", OpenRpcJsonView.as_view(collector=collector)),
    path("docs", OpenRpcDocView.as_view()),
]

if __name__ == "__main__":
    # Use `python THIS_FILE_NAME.py runserver` to run the example.
    execute_from_command_line(sys.argv)
