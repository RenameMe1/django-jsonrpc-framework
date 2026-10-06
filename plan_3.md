# Пункт 3. Три метрики на `CollectorRegistry`

## Цель

Собрать минимум JSON-RPC метрик без high-cardinality лейблов (`id` запроса не использовать).

## Где создавать

Внутри `enable_prometheus()` на переданном `registry`, не при импорте модуля. Иначе нельзя подставить тестовый `CollectorRegistry`.

Файл: [`jsonrpc_framework/integration/prometheus/_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py)

## Набор

| Имя | Тип | Лейблы |
|---|---|---|
| `jsonrpc_requests_total` | Counter | `method`, `result` |
| `jsonrpc_request_duration_seconds` | Histogram | `method` |
| `jsonrpc_errors_total` | Counter | `method`, `code` |

`result`: `success` / `error` / `notification`.  
`code`: строка JSON-RPC кода (`"-32601"`, `"-32603"`, кастомные).

API клиента: `labelnames=`, не `labels=`.

## Пример создания

```python
requests_total = Counter(
    "jsonrpc_requests_total",
    "Total JSON-RPC requests",
    labelnames=("method", "result"),
    registry=_registry,
)
request_duration = Histogram(
    "jsonrpc_request_duration_seconds",
    "JSON-RPC request duration in seconds",
    labelnames=("method",),
    registry=_registry,
)
errors_total = Counter(
    "jsonrpc_errors_total",
    "Total JSON-RPC errors",
    labelnames=("method", "code"),
    registry=_registry,
)
```

Эти объекты передать в патчи замыканием (пункты 5–6), не хранить как импорт-синглтоны в отдельном `_metrics.py`.

`/metrics` дополнительно отдаст process/python метрики `prometheus-client`, если registry — глобальный `REGISTRY`. Это нормально.

## Не делать в v1

- multiprocess (`PROMETHEUS_MULTIPROC_DIR`)
- HTTP-middleware / `django-prometheus`
- лейбл `id`

## Статус

Сделано: три метрики создаются в `enable_prometheus()`.
