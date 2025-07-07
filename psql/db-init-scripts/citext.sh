#!/usr/bin/env bash
set -e

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS citext;"
