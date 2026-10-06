# Пункт 2. Модуль интеграции

## Цель

Положить Prometheus-интеграцию рядом с Sentry, с понятным публичным импортом. Если extra не установлен — сразу сказать, как его поставить.

## Файлы

- [`jsonrpc_framework/integration/prometheus/__init__.py`](jsonrpc_framework/integration/prometheus/__init__.py)
- [`jsonrpc_framework/integration/prometheus/_prometheus.py`](jsonrpc_framework/integration/prometheus/_prometheus.py)

Образцы:

- патч диспетчера: [`jsonrpc_framework/integration/sentry.py`](jsonrpc_framework/integration/sentry.py)
- ошибка без extra: [`jsonrpc_framework/controller/auth/bearer.py`](jsonrpc_framework/controller/auth/bearer.py)

## Что сделать

1. Пакет `jsonrpc_framework.integration.prometheus` (не один файл `prometheus.py` — структура уже выбрана).
2. В `_prometheus.py` импорт клиента обернуть в `try/except ImportError` с текстом:

```text
prometheus-client is not installed, please install it with
`pip install django-jsonrpc-framework[prometheus]`
```

3. Из `__init__.py` реэкспортировать публичный API, когда он появится:

```python
from jsonrpc_framework.integration.prometheus._prometheus import (
    MetricsView,
    enable_prometheus,
)

__all__ = ["MetricsView", "enable_prometheus"]
```

Пользователь должен писать:

```python
from jsonrpc_framework.integration.prometheus import (
    MetricsView,
    enable_prometheus,
)
```

4. Не импортировать `prometheus_client` в других модулях пакета без той же проверки. Иначе `import jsonrpc_framework.integration.prometheus` упадёт раньше, чем сработает `try/except` в `_prometheus.py`.

## Статус

Сделано: пакет, `try/except` в `_prometheus.py`.

Осталось: реэкспорт в `__init__.py` после пунктов 4 и 7.
