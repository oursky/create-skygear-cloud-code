#! /bin/sh

rm -f docker-compose.override.yml
ln -s docker-compose.development.yml docker-compose.override.yml
docker-compose build
docker-compose up -d postgres
sleep 15
docker-compose run --rm skygear-plugin alembic upgrade head
docker-compose stop
