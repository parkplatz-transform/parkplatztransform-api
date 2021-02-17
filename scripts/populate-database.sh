#!/bin/bash

heroku pg:backups:download
cat latest.dump | docker exec -i postgres pg_restore --verbose --clean --no-acl --no-owner -h localhost -U postgres -d postgres
