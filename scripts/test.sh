#!/bin/bash
docker-compose -f docker-compose.test.yml up --remove-orphans -d postgres_test
sleep 5
docker-compose -f docker-compose.test.yml run --rm api_tests alembic upgrade head
docker-compose -f docker-compose.test.yml up api_tests
docker rm --force postgres_test api_tests
