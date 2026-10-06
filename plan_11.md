# Пункт 11. Проверка

## Цель

Убедиться, что метрики пишутся, `/metrics` отдаётся, тесты и типы зелёные.

## Команды

```bash
uv sync --extra jwt --extra prometheus --all-groups
make test
make mypy
```

CI extra уже добавлен в [`.github/workflows/checks.yml`](.github/workflows/checks.yml).

## Ручная проверка

1. `python single_file_asgi.py runserver` (нужен extra, если импорт не обёрнут в `try/except`).
2. POST на `/jsonrpc`, например method `printing`.
3. `curl http://127.0.0.1:8000/metrics`

В теле должны быть:

- `jsonrpc_requests_total`
- `jsonrpc_request_duration_seconds`
- `jsonrpc_errors_total` (после ошибки)
- стандартные process/python метрики, если использовали `REGISTRY`

## Регрессии

После тестов Prometheus остальные `tests/unit/test_dispathcer.py` не должны видеть патч. Если падают — в fixture нет `reset_prometheus()` (пункт 9).

## Вне скоупа этой итерации

- `django-prometheus`
- multiprocess (`PROMETHEUS_MULTIPROC_DIR`)
- auth на `/metrics`
- автомонтирование URL
- хуки в декораторе `@jsonrpc_method`

## Статус

Не сделано. Делать последним, когда пункты 4–10 закрыты.
