run:
ifdef FRAMEWORK
	npm run dev
else
	cd app && uv run python main.py
endif

test:
	cd app && uv run pytest

lint:
	cd app && uv run ruff check .
	cd app && uv run ruff format --check .
