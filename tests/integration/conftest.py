import pytest

import json as jsonlib
import django
from django.conf import settings
from django.test import Client
from django.test.utils import override_settings

INTEGRATION_URLCONF = "tests.integration.urls"


class JsonClient(Client):
    def post(self, path: str, *args: tuple, json: dict | None = None, **kwargs: dict):
        if json is not None:
            kwargs["data"] = jsonlib.dumps(json)
            kwargs["content_type"] = "application/json"

        return super().post(path, *args, **kwargs)


def _configure_django_if_needed() -> None:
    if settings.configured:
        return

    settings.configure(
        ROOT_URLCONF=INTEGRATION_URLCONF,
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["testserver", "localhost"],
        INSTALLED_APPS=["django_jsonrpc"],
    )
    django.setup()


@pytest.fixture
def client() -> Client:
    _configure_django_if_needed()
    with override_settings(ROOT_URLCONF=INTEGRATION_URLCONF):
        yield JsonClient()
