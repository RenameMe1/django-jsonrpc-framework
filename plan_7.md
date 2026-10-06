# Пункт 7. `MetricsView` — готовый `/metrics`

## Цель

Django `View` с `GET`, который отдаёт Prometheus exposition format. Библиотека URL **не** монтирует: пользователь сам пишет `path("metrics", MetricsView.as_view())`, как для OpenRPC.

## Файлы

- Класс: [`jsonrpc_framework/integration/prometheus/_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py)
- Реэкспорт: [`jsonrpc_framework/integration/prometheus/__init__.py`](jsonrpc_framework/integration/prometheus/__init__.py)

Образец view: [`jsonrpc_framework/controller/openrpc/_openrpc.py`](jsonrpc_framework/controller/openrpc/_openrpc.py) (`OpenRpcJsonView`, `http_method_names = ["get"]`).

## Реализация

```python
class MetricsView(View):
    http_method_names = ["get"]

    def get(
        self,
        request: HttpRequest,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        return HttpResponse(
            generate_latest(_active_registry()),
            content_type=CONTENT_TYPE_LATEST,
        )


def _active_registry() -> CollectorRegistry:
    return REGISTRY if _registry is None else _registry
```

`_active_registry()`:

- после `enable_prometheus()` — тот registry, что сохранили в пункте 4;
- до вызова — `REGISTRY` (process-метрики всё равно будут).

`CONTENT_TYPE_LATEST` обычно `text/plain; version=0.0.4; charset=utf-8`.

## Подключение пользователем

```python
from jsonrpc_framework.integration.prometheus import (
    MetricsView,
    enable_prometheus,
)

enable_prometheus()

urlpatterns = [
    path("jsonrpc", EchoController.as_view()),
    path("metrics", MetricsView.as_view()),
]
```

## Не делать в v1

- auth на `/metrics`
- отдельный порт внутри библиотеки
- автодобавление в `urlpatterns`

В доках (пункт 10) предупредить: эндпоинт лучше закрыть сетью (IP allowlist / отдельный порт), не светить в интернет.

## Статус

Сделано: `MetricsView` отдаёт `generate_latest(_active_registry())` с `CONTENT_TYPE_LATEST` и реэкспортируется из `jsonrpc_framework.integration.prometheus`.
