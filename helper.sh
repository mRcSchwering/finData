#!/usr/bin/env bash
# see README.md for use

PG_NAME="postgres_server"
VOL_NAME="findata_test"
DB_NAME="findata_test"
SCHEMA_NAME="findata_init2"

# argument
if [ $1 ]; then
  case $1 in

    # test
    test)
      printf "Running tests...\n"
      if  [ $2 ]; then
        printf "looking for tests with '*test_$2*'...\n\n"
        python3 -m unittest discover -s finData -v -p "*test_$2*"
      else
        printf "running all tests ...\n\n"
        python3 -m unittest discover -s finData -v
      fi
      ;;

    # start
    start)
      if [ $2 ] && [ $2 = "server" ]; then
        printf "Starting server $PG_NAME with attached volume $VOL_NAME...\n"
        printf "need root\n"
        sudo docker run \
          --rm -d \
          --name="$PG_NAME" \
          --hostname="$PG_NAME" \
          -v "$VOL_NAME":/var/lib/postgresql/data \
          -p 5432:5432 \
          postgres:9.5.12-alpine
        printf "\n... server started\n"
        printf "Reach via '-h 127.0.0.1 -p 5432 -U postgres'\n\n"
      fi
      ;;

    # stop
    stop)
      if [ $2 ] && [ $2 = "server" ]; then
        printf "Stopping server $PG_NAME\n"
        printf "need root\n"
        sudo docker stop "$PG_NAME"
      fi
      ;;

    # connect
    connect)
      printf "Connecting to $DB_NAME\n"
      psql -h 127.0.0.1 -p 5432 -U postgres "$DB_NAME"
      ;;

    # create
    create)
      if [ $2 ]; then
        printf "Creating $2 in database $DB_NAME\n"
        printf "hopefully you already started the server\n\n"
        python3 -m test.create_testdatabase \
          --db "$DB_NAME" \
          --schema "$2" \
          --host "127.0.0.1" \
          --port "5432" \
          --user "postgres"
        printf "$2 created\n\n"
      fi
      ;;

    # drop
    drop)
      if [ $2 ]; then
        printf "Dropping $2 in database $DB_NAME\n"
        printf "hopefully you already started the server\n\n"
        python3 -m test.create_testdatabase \
          --db "$DB_NAME" \
          --schema "$2" \
          --host "127.0.0.1" \
          --port "5432" \
          --user "postgres" \
          --drop
      fi
      ;;

      # integration
      integration)
        printf "Integration testing\n\n"
        printf "Running docker-compose up (w/ build)...\n\n"
        printf "need root\n"
        sudo docker-compose build app
        sudo docker-compose up -d
        sleep 5
        printf "\n\nCreating DB $DB_NAME with schema $SCHEMA_NAME...\n\n"
        sudo docker-compose run client "CREATE DATABASE $DB_NAME;"
        sudo docker-compose run app test.create_testdatabase \
          --db "$DB_NAME" \
          --schema "$SCHEMA_NAME" \
          --host server \
          --port 5432 \
          --user postgres
        printf "\n\nRunning integration tests...\n\n"
        sudo docker-compose run app test.integration_test \
          --db "$DB_NAME" \
          --schema "$SCHEMA_NAME" \
          --host server \
          --port 5432 \
          --user postgres
        printf "\n\nStopping...\n\n"
        sudo docker-compose down
      ;;
  esac

# no argument
else
  printf "no argument given\n\n"
fi
