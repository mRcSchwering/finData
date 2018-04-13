
# start server
PG_NAME="postgres_server"
VOL_NAME="postgres_data"
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data -p 5432:5432 postgres:9.5.12-alpine


# create db findata
createdb -h 127.0.0.1 -p 5432 findata -U postgres -w postgres

# login
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
\l
\c findata



# create schema
CREATE SCHEMA IF NOT EXISTS findata_init;
SELECT schema_name FROM information_schema.schemata;

# create tables
CREATE TABLE IF NOT EXISTS findata_init.stock (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  isin        VARCHAR(50) UNIQUE NOT NULL,
  wkn         VARCHAR(50) UNIQUE NOT NULL,
  typ         VARCHAR(10) NOT NULL,
  currency    VARCHAR(5) NOT NULL,
  boerse_name VARCHAR(50) UNIQUE NOT NULL,
  avan_ticker VARCHAR(50) UNIQUE NOT NULL
);






# Postgres container

# TODO test envir für loader designen


# docker in docker

# Build -> Test fan out
# siehe circleci/config.yml
# build basiert auf einem docker base image was wiederum mit der dockerfile in . ein image baut
# das ist dann die app, die auf mein docker hub gepusht wird
# damit docker-indocker keine probleme macht wird vorher remote_docker eingestellt (circleci einstellung)
# das gepushte image kann ich dann wiederum als base image laden
# das mache ich im job unittest-scraper-new (funktioniert!)

# integration tests
# hier brauch ich ja mehrere container
# sollte ähnlich gehen, nur halt mit docker compose
# vllt brauche ich da auch den "workspace" von circleci (da kann man dirs zwischen jobs sharen)
# oder einfach mehrere container innerhalb eines docker base images laufen lassen...
