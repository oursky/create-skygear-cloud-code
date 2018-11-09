#! /bin/sh

set -e

APP_SCHEMA="$APP_SCHEMA" DATABASE_URL="$DATABASE_URL" alembic upgrade head

rm -rf "$HOME/.skycli"
rm -f skygear.json

ln -s skygear."$ENV".json skygear.json
SKYCLI_EMAIL="$SKYCLI_EMAIL" SKYCLI_PASSWORD="$SKYCLI_PASSWORD" skycli --environment "$SKYCLI_ENV" login
skycli --environment "$SKYCLI_ENV" deploy
