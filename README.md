# Overview

- `_docker` Dockerfiles of some images used
- `.circleci/config.yml` circleci workflow (build, test, deploy)
- `data` file for setting up database
- `doc` some documentation
- `finData` the actual app
- `test` integration tests
- `helper.sh` helpful commands for development
- `Dockerfile` used to build the app
- `requirements.txt` used by `Dockerfile`
- `docker-compose.yml`s for develop, build, deploy

# helper.sh

Helper for developing.
Use:
- `helper.sh test [<searchString>]` to run tests [filter for certain tests]
- `helper.sh start server` to start postgres server (with volume attached)
- `helper.sh stop server` to stop postgres server (with volume attached)
- `helper.sh connect` to psql into database (on host)
- `helper.sh create <testSchemaName>` to create a test schema in database (on host)
- `helper.sh drop <testSchemaName>` to drop a test schema in database (on host)
- `helper.sh integration` docker compose up, run integration tests, docker compose down (DB in memory)

# docker-compose

Service _app_ has the actual `findata` app, _server_ is the postgres server,
_client_ is a `psql` client.
There are different docker-compose files:
- `docker-compose.yml` for development, always builds service _app_ new
- `docker-compose_build.yml` takes _build_-tagged image for _app_
- `docker-compose_deploy.yml` takes _deploy_-tagged image for _app_, doesn't have _client_, and _server_ has the database volume mounted (TODO...)

# config.json

Any keys for development.
The relevant functions should look for the `config.json` first,
then for environment variables if they didn't find the key.

```
{
  "ALPHAVANTAGE_API_KEY": ""
}
```
