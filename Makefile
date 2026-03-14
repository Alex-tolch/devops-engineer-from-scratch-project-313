run:
ifdef FRAMEWORK
	npm run dev
else
	uv run python app/main.py
endif

test:
	uv run pytest

lint:
	uv run ruff check app
	uv run ruff format --check app
