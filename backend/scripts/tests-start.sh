#! /usr/bin/env bash
set -e
set -x

python app/scripts/tests_pre_start.py

# Run migrations on test database
# Set RUN_TEST_MIGRATIONS to use test database URI for migrations
export RUN_TEST_MIGRATIONS=1
alembic upgrade head
unset RUN_TEST_MIGRATIONS

coverage run -m pytest
coverage report
coverage html --title "${@-coverage}"
