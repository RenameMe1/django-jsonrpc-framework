# Пункт 9. Тесты

## Цель

Проверить идемпотентность, счётчики, коды ошибок и HTTP `/metrics`. Изолировать registry и снимать патч после каждого теста.

## Файлы

- [`tests/unit/prometeus/__init__.py`](tests/unit/prometeus/__init__.py) (пустой, как в `tests/unit/auth/`)
- [`tests/unit/prometeus/conftest.py`](tests/unit/prometeus/conftest.py) — фикстура `fxt_prometheus_registry`
- [`tests/unit/prometeus/test_idempotence.py`](tests/unit/prometeus/test_idempotence.py)
- [`tests/unit/prometeus/test_success.py`](tests/unit/prometeus/test_success.py)
- [`tests/unit/prometeus/test_errors.py`](tests/unit/prometeus/test_errors.py)
- [`tests/unit/prometeus/test_metrics.py`](tests/unit/prometeus/test_metrics.py)

Готовые фикстуры диспетчера: [`tests/unit/conftest.py`](tests/unit/conftest.py)

- `dispatcher`, `registry`
- `valid_request` — успех, method `test`
- `invalid_method_request` — `-32601`
- `internal_handler_error_request` — `-32603`
- `notification_request`

Стиль: [`tests/unit/test_dispathcer.py`](tests/unit/test_dispathcer.py), `pytestmark = pytest.mark.asyncio`.

## Fixture

```python
@pytest.fixture
def prometheus_registry():
    registry = CollectorRegistry()
    enable_prometheus(registry=registry)
    yield registry
    reset_prometheus()
```

Без `reset_prometheus()` патч останется на классе и сломает остальные unit-тесты диспетчера.

## Сценарии

1. **Идемпотентность.** Fixture уже вызвал `enable_prometheus(registry=prometheus_registry)` и повесил патч на класс. Повторный вызов — no-op: ранний `return` по `_enabled`, обёртка не вкладывается, чужой registry не подключается.

До второго вызова сохранить идентичность обоих методов (патч висит и на `_dispatch_single`, и на `dispatch`):

```python
patched_single = RpcDispatcher._dispatch_single
patched_dispatch = RpcDispatcher.dispatch
other = CollectorRegistry()
```

Два повторных вызова, оба должны выйти на `if _enabled: return`:

```python
enable_prometheus()                  # без registry — не переключается на REGISTRY
enable_prometheus(registry=other)    # чужой registry игнорируется
```

Патч — тот же объект, вторая обёртка не появилась:

```python
assert RpcDispatcher._dispatch_single is patched_single
assert RpcDispatcher.dispatch is patched_dispatch
```

Считает только первый registry. Один успешный dispatch:

```python
await dispatcher.dispatch(valid_request, registry, HttpRequest())

assert prometheus_registry.get_sample_value(
    "jsonrpc_requests_total",
    {"method": "test", "result": "success"},
) == 1.0
assert other.get_sample_value(
    "jsonrpc_requests_total",
    {"method": "test", "result": "success"},
) is None
```

Histogram `jsonrpc_request_duration_seconds_count` с `{"method": "test"}` есть только у `prometheus_registry` и равен `1.0`. У `other` — `None`.

Повторный `Counter` на том же registry не создаётся, поэтому `ValueError: Duplicated timeseries` не возникает.

Без проверки `is` тест пропустит двойную обёртку: запрос посчитается дважды (`2.0` на первом registry) либо оба registry останутся пустыми, если второй вызов успел перехватить патч.

2. **Успех.** `await dispatcher.dispatch(valid_request, registry, HttpRequest())`.

```python
assert prometheus_registry.get_sample_value(
    "jsonrpc_requests_total",
    {"method": "test", "result": "success"},
) == 1.0
```

Histogram: `jsonrpc_request_duration_seconds_count` с `{"method": "test"}`.

3. **Ошибки.**

- `invalid_method_request` → `jsonrpc_errors_total{method="invalid", code="-32601"}`
- `internal_handler_error_request` → `code="-32603"`
- плюс `jsonrpc_requests_total{result="error"}`

4. **Parse-ошибка.** Тело уже `RpcError`, `_dispatch_single` не вызывается. Готовой фикстуры нет: передать `ParseError(data="Invalid JSON")` или `validator.validate_body(b"not json")`.

```python
await dispatcher.dispatch(
    ParseError(data="Invalid JSON"),
    registry,
    HttpRequest(),
)
assert prometheus_registry.get_sample_value(
    "jsonrpc_requests_total",
    {"method": "_invalid", "result": "error"},
) == 1.0
assert prometheus_registry.get_sample_value(
    "jsonrpc_errors_total",
    {"method": "_invalid", "code": "-32700"},
) == 1.0
```

Histogram: `jsonrpc_request_duration_seconds_count` с `{"method": "_invalid"}`.

Элемент batch, который уже `RpcError` (`valid_batch_with_errors`), в v1 не проверять.

5. **`GET /metrics`.** `RequestFactory` + `MetricsView.as_view()`:

- status `200`
- `Content-Type` содержит Prometheus content type
- в `response.content` есть `jsonrpc_requests_total` (сначала сделайте один успешный dispatch)

Если Django settings ещё не сконфигурированы:

```python
from django.conf import settings
import django

if not settings.configured:
    settings.configure(SECRET_KEY="test-prometheus", ROOT_URLCONF=__name__)
    django.setup()
```

## Статус

Частично. Тесты в `tests/unit/prometeus/`: `conftest.py`, `test_idempotence.py`, `test_success.py`, `test_errors.py`, `test_metrics.py`. Фикстура `fxt_prometheus_registry`: свой `CollectorRegistry`, `enable_prometheus`, `reset_prometheus` после теста. Функция успеха — `test_sucess` в `test_success.py`.

Сделано:

- Идемпотентность: оба повторных вызова — сначала `enable_prometheus(registry=other)`, затем `enable_prometheus()` без registry — не меняют патч `_dispatch_single` и `dispatch`. `jsonrpc_requests_total{method="test", result="success"}` равен `1.0` только у первого registry, у `other` — `None`. Histogram `jsonrpc_request_duration_seconds_count{method="test"}` == `1.0` у первого registry и `None` у `other`.
- Успех: тот же counter после `valid_request`. Histogram `jsonrpc_request_duration_seconds_count{method="test"}` == `1.0`.
- Ошибки методов: `invalid_method_request` даёт `jsonrpc_requests_total{method="invalid", result="error"}` == `1.0` и `jsonrpc_errors_total{method="invalid", code="-32601"}` == `1.0`.
- Parse-ошибка: `ParseError` → `jsonrpc_errors_total{method="_invalid", code="-32700"}` == `1.0` и `jsonrpc_request_duration_seconds_count{method="_invalid"}` == `1.0`. Batch-элемент `RpcError` не проверяется, как в v1.
- `GET /metrics`: status `200`, `CONTENT_TYPE_LATEST`, в теле есть `jsonrpc_requests_total`. Settings настраиваются внутри теста, если Django ещё не сконфигурирован.

Осталось:

- Parse-ошибка: нет `jsonrpc_requests_total{method="_invalid", result="error"}` на том же `ParseError`. Этот счётчик проверяется отдельно в `test_invalid_request` через `InvalidRequestError`, которого в сценариях плана нет.
- `internal_handler_error_request` не покрыт. `test_internal_error` шлёт уже готовый `InternalError()` (ветка `RpcError`, лейбл `method="_invalid"`) и проверяет только `jsonrpc_errors_total{method="_invalid", code="-32603"}`. Нет `jsonrpc_requests_total{result="error"}`. По плану нужен dispatch фикстуры `internal_handler_error_request`: код `-32603` и counter `result="error"`.

Прогон: семь тестов в `tests/unit/prometeus`. `pytest tests` — 65 passed. Отдельный `pytest tests/unit/prometeus` падает на пяти тестах: `HttpRequest()` требует Django settings, а `settings.configure()` есть только в `test_metrics`. В полном прогоне settings поднимает `tests/unit/test_responserr.py` при импорте.
