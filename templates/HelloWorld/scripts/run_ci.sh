#! /bin/sh -e

docker_compose() {
  docker-compose -f docker-compose.test.yml "$@"
}

docker_compose stop
docker_compose build
docker_compose run --rm test-skygear-plugin pylama
docker_compose down
