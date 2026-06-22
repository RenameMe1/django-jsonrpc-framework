lint:
	uv run pre-commit run --all-files

test:
	uv run pytest tests -s -vv
	uv run pytest jsonrpc_framework/openrpc/tests -vv -s

docs_:
	uv run mkdocs serve -f docs/mkdocs.yml
