# Makefile for ContractQuard Static Analyzer MVP

.PHONY: help install install-dev test lint format clean build docs run-example

# Default target
help:
	@echo "ContractQuard Static Analyzer MVP - Development Commands"
	@echo "======================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      Install the package and dependencies"
	@echo "  install-dev  Install in development mode with dev dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  test         Run all tests"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo ""
	@echo "Build Commands:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo ""
	@echo "Usage Commands:"
	@echo "  run-example  Run analysis on example contracts"
	@echo "  init-config  Generate default configuration file"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements.txt

# Testing
test:
	pytest tests/ -v --cov=src/contractquard --cov-report=html --cov-report=term

test-quick:
	pytest tests/ -v -x

# Code quality
lint:
	flake8 src/contractquard tests/
	black --check src/contractquard tests/

format:
	black src/contractquard tests/

type-check:
	mypy src/contractquard

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Usage examples
init-config:
	python -m contractquard.cli init-config

run-example:
	@echo "Creating example vulnerable contract..."
	@mkdir -p examples
	@echo 'pragma solidity ^0.8.0;\n\ncontract Vulnerable {\n    mapping(address => uint256) balances;\n    \n    function withdraw() public {\n        uint256 amount = balances[msg.sender];\n        msg.sender.call{value: amount}("");\n        balances[msg.sender] = 0;\n    }\n}' > examples/vulnerable.sol
	@echo "Running analysis..."
	python -m contractquard.cli analyze examples/vulnerable.sol -v

# Web Interface Commands
web-dev:
	@echo "Starting ContractQuard web interface in development mode..."
	chmod +x scripts/dev-setup.sh
	./scripts/dev-setup.sh

web-build:
	@echo "Building ContractQuard web interface..."
	docker-compose build

web-start:
	@echo "Starting ContractQuard web interface..."
	docker-compose up -d

web-stop:
	@echo "Stopping ContractQuard web interface..."
	docker-compose down

web-logs:
	@echo "Showing ContractQuard web interface logs..."
	docker-compose logs -f

web-deploy:
	@echo "Deploying ContractQuard to production..."
	chmod +x scripts/deploy.sh
	./scripts/deploy.sh

# Frontend specific commands
frontend-install:
	cd web/frontend && npm install

frontend-dev:
	cd web/frontend && npm run dev

frontend-build:
	cd web/frontend && npm run build

frontend-test:
	cd web/frontend && npm test

# Backend specific commands
backend-dev:
	PYTHONPATH=src python -m uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	PYTHONPATH=src python -m pytest tests/ -v

# Development setup
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"
	@echo "Run 'make web-dev' to start web interface"

# Check everything
check-all: lint type-check test
	@echo "All checks passed! ✅"

# Docker commands
docker-build:
	docker-compose build --no-cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f
