lint:
	uv run mypy .
	uv run ruff check . --fix
	uv run ruff format .

test:
	uv run pytest tests -s -vv
	uv run pytest jsonrpc_framework/openrpc/tests -vvv -s

docs_:
	uv run mkdocs serve -f docs/mkdocs.yml
