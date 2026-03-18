set dotenv-load

PROJECT_NAME := "celan_arch_prototype"
PYTHON_VERSION := "3.14"


# Print help
default:
    @just --list


# Start local development server
[working-directory: 'src']
[group('dev')]
run:
    uv run uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000


# Run tests
[working-directory: 'src']
[group('dev')]
test:
    uv run pytest


# Run linter
[group('dev')]
lint:
    uv run ruff check src/app


# Format code
[group('dev')]
format:
    uv run ruff format src/app


# Install dependencies
[group('dev')]
install:
    uv sync --dev


# Update dependencies
[group('dev')]
update:
    uv lock --upgrade


# Build Docker image
[working-directory: 'deploy']
[group('docker')]
build:
    docker compose build


# Run Docker container
[working-directory: 'deploy']
[group('docker')]
rund:
    docker compose up


[working-directory: 'deploy']
[group('docker')]
rundd:
    docker compose up -d


# Build and run tests in container
[working-directory: 'deploy']
[group('docker')]
testd:
    docker compose -f compose-testing.yml up --build --abort-on-container-exit


# Build test image only
[working-directory: 'deploy']
[group('docker')]
buildtestd:
    docker compose -f compose-testing.yml build


# Stop containers
[working-directory: 'deploy']
[group('docker')]
stopd:
    docker compose down


# Make migrations with docker
[working-directory: 'deploy']
[group('docker')]
migrated:
    docker compose exec app alembic upgrade head


# Apply migration with docker
[working-directory: 'deploy']
[group('docker')]
migrationd MESSAGE="no message":
    docker compose exec app alembic revision --autogenerate -m '{{MESSAGE}}'


# Show container logs
[working-directory: 'deploy']
[group('docker')]
logsd:
    docker compose logs -f --tail 100


# Run database migrations
[working-directory: 'src']
[group('db')]
migrate:
    uv run alembic upgrade head


# Create new migration
[working-directory: 'src']
[group('db')]
migration MESSAGE="no message":
    uv run alembic revision --autogenerate -m '{{MESSAGE}}'


# Downgrade one migration
[working-directory: 'src']
[group('db')]
downgrade:
    uv run alembic downgrade -1


# Show environment variables
[group('env')]
env-show:
    printenv | grep ^APP_


# Clean Python cache
[group('clean')]
clean-pyc:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name ".pytest_cache" -delete
    find . -type d -name ".mypy_cache" -delete


# Clean ruff cache
[group('clean')]
clean-ruff:
    rm -rf .ruff_cache


# Clean all
[group('clean')]
clean: clean-pyc clean-ruff
