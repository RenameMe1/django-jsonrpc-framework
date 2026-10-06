# Пункт 10. Документация и changelog

## Цель

Задокументировать extra и зафиксировать фичу в changelog. Версию пакета `0.2.0` в `pyproject.toml` бампать до `0.2.1`.

## Файлы

- новый [`docs/docs/integrations/prometheus.md`](docs/docs/integrations/prometheus.md)
- новый [`docs/docs/examples/prometheus.py`](docs/docs/examples/prometheus.py)
- [`docs/mkdocs.yml`](docs/mkdocs.yml)
- [`CHANGELOG.md`](CHANGELOG.md)

Страница подключает пример сниппетом. В `docs/mkdocs.yml` уже есть `pymdownx.snippets` с `base_path: ["."]`.

## `prometheus.md`

Содержание:

1. Короткое введение: Prometheus собирает метрики приложения.
2. Установка: `pip install django-jsonrpc-framework[prometheus]`
3. Секция Configuration. Текст: `enable_prometheus()` в `settings.py`, затем `MetricsView` в `urlpatterns`. Код — один сниппет:

```python linenums="1" hl_lines="10-13 15 38"
--8<-- "docs/docs/examples/prometheus.py"
```

Подсветка: импорт `MetricsView` и `enable_prometheus`, вызов `enable_prometheus()`, строка `path("metrics", ...)`.

4. Проверка: `curl` на `POST http://127.0.0.1:8000/jsonrpc` с методом `echo` и ссылка на `http://127.0.0.1:8000/metrics`.
5. Таблица метрик: `jsonrpc_requests_total`, `jsonrpc_request_duration_seconds`, `jsonrpc_errors_total` и лейблы.
6. Предупреждение: `/metrics` лучше закрыть сетью (IP allowlist / отдельный порт), не публиковать в интернет.
7. Не описывать multiprocess и auth на `/metrics`. Совместную работу с `django-prometheus` пишет пункт 12, в этот пункт её не включать.

Happy-path без `try/except`.

## `examples/prometheus.py`

Один запускаемый файл, не два отдельных блока в markdown:

- импорт `MetricsView`, `enable_prometheus` и вызов `enable_prometheus()`
- `settings.configure`, если Django ещё не сконфигурирован
- `EchoController` с методом `echo`
- `urlpatterns`: `path("jsonrpc", EchoController.as_view())` и `path("metrics", MetricsView.as_view())`
- `if __name__`: `execute_from_command_line`

## `mkdocs.yml`

Рядом с Sentry, путь в том же регистре:

```yaml
  - Integrations:
    - Sentry: integrations/sentry.md
    - Prometheus: integrations/prometheus.md
```

Файл лежит в `docs/docs/integrations/`.

## `CHANGELOG.md`

Секция `[0.2.1] - 2026-10-06` сверху, перед `[0.2.0]`, стиль как у `0.2.0`:

```md
## [0.2.1] - 2026-10-06

### Added
- Added optional Prometheus metrics integration in `jsonrpc_framework/integration/`.
- Added Prometheus documentation in `docs/docs/integrations/prometheus.md`.
- Added optional dependency extra `prometheus` in `pyproject.toml`.
```

## Статус

Сделано. Проверено по файлам, расхождений с пунктом нет.

- `docs/docs/integrations/prometheus.md`: введение, установка extra `prometheus`, секция Configuration со сниппетом, `curl` на `/jsonrpc`, ссылка на `/metrics`.
- Сниппет `docs/docs/examples/prometheus.py`: `enable_prometheus()`, `settings.configure`, `EchoController.echo`, `urlpatterns` с `EchoController.as_view()` и `MetricsView.as_view()`, запуск через `execute_from_command_line`.
- Таблица трёх метрик с верными лейблами: `jsonrpc_requests_total` — `method`, `result`; `jsonrpc_request_duration_seconds` — `method`; `jsonrpc_errors_total` — `method`, `code`.
- Предупреждение про IP allowlist, отдельный порт и запрет публиковать `/metrics` в интернет. Нет `try/except`, multiprocess, auth и секции про `django-prometheus`.
- В `docs/mkdocs.yml` пункт Prometheus стоит рядом с Sentry, путь `integrations/prometheus.md`.
- В `CHANGELOG.md` секция `[0.2.1] - 2026-10-06` сверху, перед `[0.2.0]`. Три пункта Added: интеграция, документация, extra `prometheus`.
- В `pyproject.toml` версия `0.2.1`, extra `prometheus` есть. Бамп с `0.2.0` сделан.

Осталось: ничего.
