#! /bin/sh

docker_compose() {
  docker-compose -f docker-compose.test.yml "$@"
}

docker_compose stop
docker_compose build
docker_compose up -d test-postgres
echo 'sleep 10'
sleep 10

docker_compose run --rm test-skygear-plugin alembic upgrade head
docker_compose stop
docker_compose up -d
echo 'sleep 10'
sleep 10

docker_compose run --rm test-skygear-plugin pytest
docker_compose stop
