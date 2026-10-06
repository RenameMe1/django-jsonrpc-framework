# Пункт 6. Патч `dispatch()` — parse-ошибки

## Цель

Учесть случаи, когда тело запроса уже `RpcError` и `_dispatch_single` не вызывается.

## Где

Оригинал: [`jsonrpc_framework/logic/dispatcher.py`](jsonrpc_framework/logic/dispatcher.py), ветка:

```python
elif isinstance(body, RpcError):
    return ErrorResponse(id=None, error=body)
```

Обёртка: `_patch_dispatch` в [`_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py).

## Почему нельзя обойтись пунктом 5

`dispatch()` маршрутизирует:

- `Request` / `Notification` → `_dispatch_single` (уже покрыто пунктом 5)
- `list` → `_dispatch_batch` → снова `_dispatch_single`
- `RpcError` → сразу `ErrorResponse`, **без** `_dispatch_single`

Это parse/invalid request после `RequestValidator`: метода нет.

## Логика обёртки

```python
def _patch_dispatch(
    dispatcher_cls: type[RpcDispatcher],
    *,
    requests_total: Counter,
    request_duration: Histogram,
    errors_total: Counter,
) -> None:
    old = dispatcher_cls.dispatch

    async def patched(self, body, registry, http_request):
        if not isinstance(body, RpcError):
            return await old(self, body, registry, http_request)

        start = time.perf_counter()
        result = await old(self, body, registry, http_request)
        _observe_outcome(
            method="_invalid",
            result=result,  # ErrorResponse
            duration=time.perf_counter() - start,
            requests_total=requests_total,
            request_duration=request_duration,
            errors_total=errors_total,
        )
        return result

    dispatcher_cls.dispatch = patched
```

Лейбл метода: `method="_invalid"`.  
`result="error"`.  
`code` из `body.code` / `result.error.code`.

Остальные ветки только проксировать в `old(...)`. Если обернуть успешный single-request и в `dispatch`, и в `_dispatch_single`, метрики задвоятся.

## Что не покрывать в v1

Элементы batch, которые уже `RpcError` внутри `_dispatch_batch` (там `continue` без `_dispatch_single`). План это допускает.

## Статус

Сделано: `_patch_dispatch` пишет метрики для `RpcError` с `method="_invalid"`, остальные ветки проксируются в `old`.
