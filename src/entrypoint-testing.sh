#!/bin/bash
set -e

echo "APPLY MIGRATIONS..."
alembic upgrade head

echo "START TESTING..."
#pytest -vxs --tb=short tests/test_admin.py::TestInactiveUserRestrictions::test_inactive_user_cannot_login
pytest -x
