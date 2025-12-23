install:
	uv sync
	uv run pip install psycopg2-binary python-dotenv validators
# ниже команда для запуска приложения в режиме отладки
dev:
	uv run flask --debug --app page_analyzer:app run

# run: uv run gendiff

test: 
	uv run pytest

# test-coverage: uv run pytest --cov=gendiff --cov-report=xml:coverage.xml

lint:
	uv run ruff check app

check: test lint

build:
	./build.sh

package-install:
	uv tool install dist/*.whl

reinstall:
	uv tool install --force dist/*.whl

uninstall:
	uv tool uninstall hexlet-code

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

# команда для запуска приложения в продакшене
PORT ?= 8000
start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install test lint selfcheck check build package-install reinstall uninstall
