#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

rm -f ./*.pid

# FOR PRODUCTION
# printf "Checking PostgreSQL availability...\n"
# until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q
# do
#   printf "Database unavailable, waiting 1 second...\n"
#   sleep 1;
# done
# printf "Database available!\n"

exec "$@"