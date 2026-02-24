run:
ifdef FRAMEWORK
	npm run dev
else
	uv run python main.py
endif

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
