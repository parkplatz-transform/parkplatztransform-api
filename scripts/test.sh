#!/bin/bash
docker-compose -f docker-compose.test.yml up --remove-orphans -d postgres
bash -c 'until docker exec postgres /usr/bin/pg_isready ; do sleep 10 ; done'
docker-compose -f docker-compose.test.yml run --rm app alembic upgrade head
docker-compose -f docker-compose.test.yml up app
docker rm --force postgres app
