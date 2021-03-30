#!/bin/bash
docker-compose -f docker-compose.test.yml up --remove-orphans -d postgres
sleep 7
docker-compose -f docker-compose.test.yml run --rm app alembic upgrade head
docker-compose -f docker-compose.test.yml up app
docker rm --force postgres app
