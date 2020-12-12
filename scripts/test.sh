#!/bin/bash
docker-compose -f docker-compose.test.yml up -d postgres_test
docker-compose -f docker-compose.test.yml run --rm api_tests alembic upgrade head
docker-compose -f docker-compose.test.yml up api_tests
docker rm --force postgres_test
docker rm --force api_tests
