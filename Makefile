run:
	uv run python main.py

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
