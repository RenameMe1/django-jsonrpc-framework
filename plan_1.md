# Пункт 1. Зависимость `prometheus-client`

## Цель

Сделать `prometheus-client` опциональным extra пакета, как `jwt` и `sentry`. В основные `dependencies` его не добавлять.

## Файлы

- [`pyproject.toml`](pyproject.toml)
- [`uv.lock`](uv.lock)
- [`.github/workflows/checks.yml`](.github/workflows/checks.yml)

## Что сделать

1. В `[project.optional-dependencies]` добавить:

```toml
prometheus = ["prometheus-client>=0.21"]
```

2. Зафиксировать lockfile и поставить extra локально:

```bash
uv lock
uv sync --extra prometheus --all-groups
```

3. В CI оба job (`test` и `mypy`) должны ставить extra, иначе тесты интеграции не найдут пакет:

```yaml
uv sync --extra jwt --extra prometheus --all-groups
```

## Статус

Сделано: extra в `pyproject.toml`, `--extra prometheus` в CI.

Проверить: после `uv lock` в `uv.lock` появился `prometheus-client`.
