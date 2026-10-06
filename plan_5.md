# Пункт 5. Патч `_dispatch_single`

## Цель

Писать метрики на каждый JSON-RPC метод: имя, длительность (включая auth), исход.

Не патчить `@jsonrpc_method` — там только метаданные.  
Batch отдельно не патчить: `_dispatch_batch` уже вызывает `_dispatch_single`.

## Где

Оригинал: [`jsonrpc_framework/logic/dispatcher.py`](jsonrpc_framework/logic/dispatcher.py) (`RpcDispatcher._dispatch_single`).

Обёртка: [`jsonrpc_framework/integration/prometheus/_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py), функция `_patch_dispatch_single`.

Образец патча: [`jsonrpc_framework/integration/sentry.py`](jsonrpc_framework/integration/sentry.py) (`_patch_dispatch_single`).

## Почему этот метод

В нём есть:

- `request.method`
- полный путь (handler lookup, auth, call)
- исход: `SuccessResponse` / `ErrorResponse` / `None` (notification)

`RpcError` чаще **возвращается**, а не бросается: `_call_handler` ловит exception и отдаёт `InternalError()`. Смотреть на return value, не только на `except`.

## Логика обёртки

```python
def _patch_dispatch_single(
    dispatcher_cls: type[RpcDispatcher],
    *,
    requests_total: Counter,
    request_duration: Histogram,
    errors_total: Counter,
) -> None:
    old = dispatcher_cls._dispatch_single

    async def patched(self, request, registry, http_request):
        method = request.method
        start = time.perf_counter()
        try:
            result = await old(self, request, registry, http_request)
        except Exception:
            duration = time.perf_counter() - start
            request_duration.labels(method=method).observe(duration)
            requests_total.labels(method=method, result="error").inc()
            raise

        duration = time.perf_counter() - start
        request_duration.labels(method=method).observe(duration)

        if result is None:
            result_label = "notification"
        elif isinstance(result, ErrorResponse):
            result_label = "error"
            errors_total.labels(
                method=method,
                code=str(result.error.code),
            ).inc()
        else:
            result_label = "success"

        requests_total.labels(method=method, result=result_label).inc()
        return result

    dispatcher_cls._dispatch_single = patched
```

Классификация:

| Return | `result` | Ещё |
|---|---|---|
| `SuccessResponse` | `success` | — |
| `ErrorResponse` | `error` | `jsonrpc_errors_total{code=...}` |
| `None` | `notification` | ошибка notification клиенту не уходит, отдельно не различить |
| exception из `old` | `error` | проброс дальше |

`code` лейбла — `str(...)`: Prometheus labels только строки.

Вынести запись в `_observe_outcome(...)`, чтобы пункт 6 не дублировал логику.

## Статус

Не сделано.
