#!/bin/bash
docker-compose -f docker-compose.test.yml up --remove-orphans -d mongo
sleep 5
docker-compose -f docker-compose.test.yml up app
docker rm --force mongo app
