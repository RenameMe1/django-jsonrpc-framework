# Пункт 8. Пример в `single_file_asgi.py`

## Цель

Показать рабочее подключение рядом с Sentry и OpenRPC.

Файл: [`single_file_asgi.py`](single_file_asgi.py)

## Что добавить

1. Импорт и вызов (после блока Sentry или рядом с ним):

```python
from jsonrpc_framework.integration.prometheus import (
    MetricsView,
    enable_prometheus,
)

enable_prometheus()
```

2. В `urlpatterns`:

```python
urlpatterns = [
    path("jsonrpc", EchoController.as_view()),
    path("openrpc.json", OpenRpcJsonView.as_view(collector=collector)),
    path("docs", OpenRpcDocView.as_view()),
    path("metrics", MetricsView.as_view()),
]
```

## Опционально: не ломать пример без extra

Сейчас `single_file_asgi.py` стартует без `sentry` (Sentry за `SENTRY_DSN`). Жёсткий импорт Prometheus сломает `python single_file_asgi.py runserver` без extra.

Можно так:

```python
try:
    from jsonrpc_framework.integration.prometheus import (
        MetricsView,
        enable_prometheus,
    )
except ImportError:
    MetricsView = None
else:
    enable_prometheus()
```

И добавлять `path("metrics", ...)` только если `MetricsView is not None`.

В доках (пункт 10) показывать прямой happy-path без `try/except`.

## Статус

Не сделано.
