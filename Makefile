.PHONY: build run run-local stop

# Docker commands
build:
	docker-compose build

run:
	docker-compose up

stop:
	docker-compose down

# Development commands
install:
	poetry install

# Testing commands
test:
	poetry run pytest -v

coverage:
	poetry run pytest --cov=src tests/ --cov-report=term-missing

coverage-html:
	poetry run pytest --cov=src tests/ --cov-report=html

# Linting commands
lint:
	poetry run flake8 src