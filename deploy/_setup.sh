#!/usr/bin/env bash
# setup postgres database on host using docker volume
# from finData root directory

PG_NAME="postgres_server"
VOL_NAME="findata"
LOCK_TAG="DO_NOT_DELETE_ME"
DB_NAME="findata"
SCHEMA_NAME="findata_init"


# create docker volume and secure it against
# accidental pruning by attaching a container to it
sudo docker volume create "$VOL_NAME"
sudo docker run \
  --name="$LOCK_TAG"_"$VOL_NAME" \
  -v "$VOL_NAME":/mnt alpine


# start postgres server container with volume attached
# and port exposed to host
sudo docker run \
  --name="$PG_NAME" \
  -d \
  --rm \
  -v "$VOL_NAME":/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:9.5.12-alpine
#netstat -plunt | grep 5432


# create database using psql client
# TODO: this could be a docker container as well
# install psql client if needed
#sudo apt-get update
#sudo apt-get install postgresql-client
createdb -h 127.0.0.1 -p 5432 "$DB_NAME" -U postgres


# initialize schema using python3 psycopg2
# this is form finData root directory
python3 -m data.initialize_schema \
  --db "$DB_NAME" \
  --schema "$SCHEMA_NAME" \
  --host 127.0.0.1 \
  --port 5432 \
  --user postgres
#psql -h 127.0.0.1 -p 5432 -U postgres "$DB_NAME"

# stop server
sudo docker stop "$PG_NAME"
