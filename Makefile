.PHONY: help install lint test coverage format format-check run docker-build docker-up docker-down

help:
	@echo "Available targets:"
	@echo "  install       Install development dependencies"
	@echo "  lint          Run ruff lint checks"
	@echo "  test          Run pytest"
	@echo "  coverage      Run pytest with coverage"
	@echo "  format        Format Python files with ruff"
	@echo "  format-check  Check Python formatting with ruff"
	@echo "  run           Run the development server"
	@echo "  docker-build  Build Docker images"
	@echo "  docker-up     Start Docker Compose services"
	@echo "  docker-down   Stop Docker Compose services"

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

lint:
	python -m ruff check .

test:
	python -m pytest

coverage:
	python -m pytest --cov=securebank --cov-report=term-missing

format:
	python -m ruff format .

format-check:
	python -m ruff format --check .

run:
	python -m uvicorn securebank.main:app --reload

docker-build:
	docker compose build

docker-up:
	docker compose up

docker-down:
	docker compose down
