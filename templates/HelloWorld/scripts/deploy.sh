#! /bin/sh

set -e

docker-compose run -e SCHEMA_NAME="$APP_SCHEMA" -e DATABASE_URL="$DATABASE_URL" --rm skygear-plugin alembic upgrade head

rm -rf "$HOME/.skycli"
rm -f skygear.json

ln -s skygear."$ENV".json skygear.json
SKYCLI_EMAIL="$SKYCLI_EMAIL" SKYCLI_PASSWORD="$SKYCLI_PASSWORD" skycli --environment "$SKYCLI_ENV" login
skycli --environment "$SKYCLI_ENV" deploy
