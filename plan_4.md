# Пункт 4. `enable_prometheus()`

## Цель

Одноразовый bootstrap интеграции. Без него метрики не пишутся: у Prometheus нет аналога `sentry_sdk.init()`, который сам вызывает `setup_once()`.

Файл: [`jsonrpc_framework/integration/prometheus/_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py)

Это не сбор значений. Сбор — в обёртках пунктов 5–6. Здесь только: выбрать registry → создать метрики → запомнить оригиналы → патч класса → флаг.

## Зачем отдельная функция

Sentry: `sentry_sdk.init(..., integrations=[JsonRpcIntegration()])` → SDK вызывает `setup_once()` и патчит `RpcDispatcher`.

Prometheus pull-based, своего хоста нет. Пользователь вызывает `enable_prometheus()` явно. Иначе `MetricsView` отдаст только process-метрики.

Патч вешается на **класс** `RpcDispatcher`, не на экземпляр. Все контроллеры после вызова пишут в одни метрики. Повторный патч без флага обернёт обёртку ещё раз — каждый запрос посчитается дважды.

## Состояние модуля

```python
_enabled: bool = False
_registry: CollectorRegistry | None = None
_original_dispatch_single = None
_original_dispatch = None
```

## Сигнатура

```python
def enable_prometheus(*, registry: CollectorRegistry | None = None) -> None:
```

Только keyword-only: `enable_prometheus(my_registry)` нельзя, только `enable_prometheus(registry=...)`. Так не путают Prometheus registry с RPC-registry методов.

### Шаг 1. Идемпотентность

```python
global _enabled, _registry, _original_dispatch_single, _original_dispatch

if _enabled:
    return
```

Второй вызов — no-op. Даже с другим `registry` остаются метрики и патч первого вызова. Можно звать и в `single_file_asgi.py`, и в `AppConfig.ready()`, и в тестах.

### Шаг 2. Выбрать registry

```python
if registry is None:
    registry = REGISTRY
_registry = registry
```

- Продакшен: `enable_prometheus()` → глобальный `REGISTRY`. `MetricsView` через `generate_latest` видит JSON-RPC и process/python метрики.
- Тесты: `enable_prometheus(registry=CollectorRegistry())` — счётчики не текут между тестами.

`MetricsView` (пункт 7) должен читать **тот же** `_registry`.

Не создавать Counter/Histogram при импорте модуля: тогда нельзя подставить тестовый registry. Повторный `Counter("jsonrpc_requests_total", ..., registry=тот_же)` без шага 1 упадёт: `ValueError: Duplicated timeseries`.

### Шаг 3. Создать три метрики

См. пункт 3. Передать их в патчи замыканием, не через глобалы другого модуля.

### Шаг 4. Сохранить оригиналы

```python
_original_dispatch_single = RpcDispatcher._dispatch_single
_original_dispatch = RpcDispatcher.dispatch
```

Это unbound function с класса. Сохранять **до** `RpcDispatcher._dispatch_single = patched`. Иначе `reset_prometheus()` нечего восстанавливать.

Патч `dispatch` нужен отдельно: parse-ошибка (`isinstance(body, RpcError)`) не заходит в `_dispatch_single`.

### Шаг 5. Навесить патчи и поднять флаг

```python
_patch_dispatch_single(
    RpcDispatcher,
    requests_total=requests_total,
    request_duration=request_duration,
    errors_total=errors_total,
)
_patch_dispatch(
    RpcDispatcher,
    requests_total=requests_total,
    request_duration=request_duration,
    errors_total=errors_total,
)
_enabled = True
```

`_enabled = True` только **после** успешного патча. Если Counter упал на дубликате, флаг не должен быть true.

Сами `_patch_*` — пункты 5–6. Здесь их только вызвать. Схема как у Sentry: взять `old`, объявить `async def patched`, присвоить на класс.

### Шаг 6. `reset_prometheus()` для тестов

Публично не экспортировать. Нужен pytest, чтобы следующие тесты снова вызвали `enable_prometheus(registry=новый_CollectorRegistry())`.

```python
def reset_prometheus() -> None:
    global _enabled, _registry
    global _original_dispatch_single, _original_dispatch

    if _original_dispatch_single is not None:
        RpcDispatcher._dispatch_single = _original_dispatch_single
    if _original_dispatch is not None:
        RpcDispatcher.dispatch = _original_dispatch

    _original_dispatch_single = None
    _original_dispatch = None
    _registry = None
    _enabled = False
```

Без сброса `_enabled` останется `True`, новый registry не подключится.

## Снаружи

Продакшен:

```python
from jsonrpc_framework.integration.prometheus import enable_prometheus

enable_prometheus()
```

Тест:

```python
registry = CollectorRegistry()
enable_prometheus(registry=registry)
# dispatch ...
assert registry.get_sample_value(
    "jsonrpc_requests_total",
    {"method": "test", "result": "success"},
) == 1.0
reset_prometheus()
```

## Типичные ошибки

1. Патчить экземпляр `self.dispatcher` в `BaseController` — другие контроллеры без метрик.
2. Забыть идемпотентность — двойной счёт или `ValueError` на дубликате имени.
3. Создавать метрики при импорте — нельзя подставить тестовый registry; импорт упадёт без extra.
4. Не сохранить `old` до присваивания — reset восстановит уже патченую функцию.
5. `_enabled = True` до создания метрик — сбой на полпути оставит интеграцию «включённой».

## Статус

Сделано: флаги, идемпотентность, выбор registry, создание трёх метрик.

Осталось: сохранить оригиналы, вызвать `_patch_*`, `_enabled = True`, `reset_prometheus()`.
