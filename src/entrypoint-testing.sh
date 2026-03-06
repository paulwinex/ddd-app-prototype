#!/bin/bash
set -e

echo "APPLY MIGRATIONS..."
alembic upgrade head

echo "START TESTING..."
pytest -v --tb=short
