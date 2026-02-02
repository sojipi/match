# AI Matchmaker Development Makefile

.PHONY: help install dev build test clean docker-build docker-up docker-down

# Default target
help:
	@echo "AI Matchmaker Development Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup            Set up development environment (Windows: scripts/setup-dev.bat)"
	@echo "  install          Install all dependencies (frontend + backend)"
	@echo "  install-frontend Install frontend dependencies"
	@echo "  install-backend  Install backend dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev              Start development environment with Docker"
	@echo "  dev-local        Start development servers locally"
	@echo "  frontend-dev     Start frontend development server"
	@echo "  backend-dev      Start backend development server"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests"
	@echo "  test-frontend    Run frontend tests"
	@echo "  test-backend     Run backend tests"
	@echo "  lint             Run linting for all code"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-up        Start services with Docker Compose"
	@echo "  docker-down      Stop Docker services"
	@echo "  docker-logs      View Docker logs"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-migrate       Run database migrations"
	@echo "  db-reset         Reset database"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean            Clean build artifacts"
	@echo "  format           Format all code"

# Installation
install: install-frontend install-backend

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-backend:
	@echo "Installing backend dependencies..."
	pip install -r requirements.txt

# Development
dev: 
	@echo "Starting local development servers..."
	@echo "Use scripts/start-dev.bat on Windows"
	@echo "Backend: http://localhost:8000, Frontend: http://localhost:3000"

dev-local: 
	@echo "Starting local development servers..."
	@echo "Make sure remote PostgreSQL and Redis are accessible"
	@echo "Starting backend server..."
	cd backend && py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend server..."
	cd frontend && npm run dev

frontend-dev:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

backend-dev:
	@echo "Starting backend development server..."
	cd backend && py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Testing
test: test-frontend test-backend

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test

test-backend:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v

lint:
	@echo "Running linting..."
	cd frontend && npm run lint
	flake8 ai_matchmaker backend --max-line-length=88

format:
	@echo "Formatting code..."
	cd frontend && npm run format
	black ai_matchmaker backend
	isort ai_matchmaker backend

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started. Frontend: http://localhost:3000, Backend: http://localhost:8000"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

# Database
db-migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres redis
	sleep 5
	cd backend && alembic upgrade head

# Utilities
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Production build
build:
	@echo "Building for production..."
	cd frontend && npm run build
	docker-compose -f docker-compose.prod.yml build

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@curl -f http://localhost:3000 || echo "Frontend not responding"

# Setup
setup:
	@echo "Setting up development environment..."
	@echo "On Windows, run: scripts\\setup-dev.bat"
	@echo "On Unix systems, ensure Python 3.11+ and Node.js 18+ are installed"