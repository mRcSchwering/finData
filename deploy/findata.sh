#!/usr/bin/env bash
# see README.md for use

# vars
PG_NAME="postgres_server"
VOL_NAME="findata"
DB_NAME="findata"
SCHEMA_NAME="findata_init"

# api key aus config.json
ALPHAVANTAGE_API_KEY=$(ruby -rjson -e 'j = JSON.parse(File.read("../config.json")); puts j["ALPHAVANTAGE_API_KEY"]')

# TODO -m function for reading csv of stock inserts
# (TODO -m function for customSQL)
# TODO bash function for using docker-compose
# TODO failsave api key

sudo docker-compose up -d

# insert stock
sudo docker-compose run \
  --rm \
  -e ALPHAVANTAGE_API_KEY="$ALPHAVANTAGE_API_KEY" \
  app \
  finData.connect \
  --db "$DB_NAME" \
  --schema "$SCHEMA_NAME" \
  --host server \
  --port 5432 \
  --user postgres \
  insert \
  "Adidas" "DE000A1EWWW0" "A1EWWW" "EUR" "Adidas-Aktie" "ADS.DE"

# update all data
sudo docker-compose run \
  --rm \
  -e ALPHAVANTAGE_API_KEY="$ALPHAVANTAGE_API_KEY" \
  app \
  finData.connect \
  --db "$DB_NAME" \
  --schema "$SCHEMA_NAME" \
  --host server \
  --port 5432 \
  --user postgres \
  update

sudo docker-compose down
