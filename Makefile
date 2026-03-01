.PHONY: install dev test lint format migrate run docker-up docker-down clean help

# Variables
PYTHON := python3
PIP := pip
UVICORN := uvicorn
ALEMBIC := alembic
DOCKER_COMPOSE := docker-compose -f docker/docker-compose.yml

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed!$(NC)"

dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install black isort mypy pytest-cov
	@echo "$(GREEN)Development dependencies installed!$(NC)"

setup: ## Initial setup (copy example files)
	@echo "$(YELLOW)Setting up configuration files...$(NC)"
	cp -n .env.example .env 2>/dev/null || true
	cp -n config/settings.example.yaml config/settings.yaml 2>/dev/null || true
	cp -n config/personas.example.yaml config/personas.yaml 2>/dev/null || true
	@echo "$(GREEN)Setup complete! Edit .env and config files.$(NC)"

migrate: ## Run database migrations
	@echo "$(YELLOW)Running migrations...$(NC)"
	$(ALEMBIC) upgrade head
	@echo "$(GREEN)Migrations complete!$(NC)"

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	@echo "$(YELLOW)Creating migration...$(NC)"
	$(ALEMBIC) revision --autogenerate -m "$(msg)"
	@echo "$(GREEN)Migration created!$(NC)"

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	$(ALEMBIC) downgrade -1
	@echo "$(GREEN)Rollback complete!$(NC)"

run: ## Run the API server (development)
	@echo "$(YELLOW)Starting API server...$(NC)"
	$(UVICORN) src.api.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the API server (production)
	@echo "$(YELLOW)Starting API server (production)...$(NC)"
	$(UVICORN) src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run tests
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	@echo "$(YELLOW)Running linters...$(NC)"
	$(PYTHON) -m mypy src/ --ignore-missing-imports
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(YELLOW)Formatting code...$(NC)"
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/
	@echo "$(GREEN)Formatting complete!$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(YELLOW)Checking code format...$(NC)"
	$(PYTHON) -m black src/ tests/ --check
	$(PYTHON) -m isort src/ tests/ --check-only

docker-up: ## Start Docker services
	@echo "$(YELLOW)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started!$(NC)"

docker-down: ## Stop Docker services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped!$(NC)"

docker-logs: ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-build: ## Build Docker images
	@echo "$(YELLOW)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Build complete!$(NC)"

docker-restart: docker-down docker-up ## Restart Docker services

db-up: ## Start only database services
	@echo "$(YELLOW)Starting database services...$(NC)"
	$(DOCKER_COMPOSE) up -d db redis
	@echo "$(GREEN)Database services started!$(NC)"

clean: ## Clean up generated files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	@echo "$(GREEN)Cleanup complete!$(NC)"

shell: ## Open Python shell with app context
	$(PYTHON) -c "from src.database.base import *; from src.database.models import *; import asyncio; print('Models imported. Use asyncio.run() for async operations.')"

logs: ## View application logs
	tail -f logs/*.log 2>/dev/null || echo "No log files found"
