#!/bin/bash
docker-compose run app alembic revision --autogenerate -m "$1"