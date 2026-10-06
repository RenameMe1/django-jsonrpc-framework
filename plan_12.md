# Пункт 12. Инструкция: Prometheus вместе с `django-prometheus`

## Цель

Описать, как приложение с REST и JSON-RPC собирает оба слоя метрик. Пакет по-прежнему не зависит от `django-prometheus` и не ставит HTTP-middleware сам.

Делать после пункта 10: секция в уже созданном [`docs/docs/integrations/prometheus.md`](docs/docs/integrations/prometheus.md). Отдельную страницу и пункт в `mkdocs.yml` не добавлять.

В `pyproject.toml` extra `prometheus` остаётся `prometheus-client`. `django-prometheus` приложение ставит само.

## Что написать

Секция «REST и django-prometheus».

1. Разделение. `django-prometheus` считает HTTP всех view: метод, имя view, статус, длительность. Это REST и сам запрос на `/jsonrpc`. `enable_prometheus()` считает смысл JSON-RPC: метод, `success` / `error` / `notification`, код ошибки. Пакет из пяти вызовов — один HTTP-запрос и пять `jsonrpc_requests_total`.

2. Подключение в приложении. `django_prometheus` в `INSTALLED_APPS`. `PrometheusBeforeMiddleware` первым в `MIDDLEWARE`, `PrometheusAfterMiddleware` последним. `enable_prometheus()` без аргументов, чтобы метрики попали в общий `REGISTRY`.

```python
INSTALLED_APPS = [
    "django_prometheus",
    # ...
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    # остальные middleware
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

from jsonrpc_framework.integration.prometheus import enable_prometheus

enable_prometheus()

urlpatterns = [
    path("", include("django_prometheus.urls")),  # /metrics
    path("jsonrpc", EchoController.as_view()),
]
```

3. Один эндпоинт `/metrics`. При `django-prometheus` свой `MetricsView` не монтировать: экспорт `django-prometheus` читает тот же `REGISTRY`, `jsonrpc_*` попадают в выдачу сами. Два пути на один реестр не нужны.

4. `enable_prometheus(registry=...)` уводит JSON-RPC-метрики из выдачи `django-prometheus`. В проде вызов без `registry`. Свой реестр — для тестов.

5. Несколько воркеров и `PROMETHEUS_MULTIPROC_DIR`: экспорт `django-prometheus`, не `MetricsView`. Свой view multiprocess не собирает.

Имена не пересекаются: `django_*` и `jsonrpc_*`.

## Не делать

- Зависимость `django-prometheus` в этом пакете.
- Свой HTTP-middleware.
- Пример `django-prometheus` в `single_file_asgi.py`.

## Статус

Не сделано.
