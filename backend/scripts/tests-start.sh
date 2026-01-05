#! /usr/bin/env bash
set -e
set -x

python app/scripts/tests_pre_start.py

# Run migrations on test database
# Set RUN_TEST_MIGRATIONS to use test database URI for migrations
export RUN_TEST_MIGRATIONS=1
alembic upgrade head
unset RUN_TEST_MIGRATIONS

uv run coverage run -m pytest
uv run coverage report
uv run coverage html --title "${@-coverage}"
