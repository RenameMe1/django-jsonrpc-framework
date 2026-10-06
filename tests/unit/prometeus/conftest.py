from __future__ import annotations

from collections.abc import Iterator

import django
import pytest
from django.conf import settings
from prometheus_client import CollectorRegistry

from jsonrpc_framework.integration.prometheus import (
    enable_prometheus,
    reset_prometheus,
)


def _configure_django_if_needed() -> None:
    if settings.configured:
        return

    settings.configure(SECRET_KEY="test-prometheus", ROOT_URLCONF=__name__)
    django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_settings() -> None:
    _configure_django_if_needed()


@pytest.fixture
def fxt_prometheus_registry() -> Iterator[CollectorRegistry]:
    registry = CollectorRegistry()
    enable_prometheus(registry=registry)
    yield registry
    reset_prometheus()