#!/bin/bash

DUMP_FILE=latest.dump

if [ ! -f "$DUMP_FILE" ]; then
    heroku pg:backups:download
fi

cat latest.dump | docker exec -i postgres pg_restore --verbose --clean --no-acl --no-owner -h localhost -U postgres -d postgres
