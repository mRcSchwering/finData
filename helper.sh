#!/usr/bin/env bash
# use
# - `helper.sh test [<searchString>]` to run tests [filter for certain tests]
# - `helper.sh start server` to start postgres server with volume attached
# - `helper.sh connect` to psql into database
# - `helper.sh stop server` to stop postgres server
# - `helper.sh create <testSchemaName>` to create a test schema in database
# - `helper.sh drop <testSchemaName>` to drop a test schema in database

DB_NAME="findata"
PG_NAME="postgres_server"
VOL_NAME="postgres_data"

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
        python3 -m data.create_testdatabase \
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
        python3 -m data.create_testdatabase \
          --db "$DB_NAME" \
          --schema "$2" \
          --host "127.0.0.1" \
          --port "5432" \
          --user "postgres" \
          --drop
      fi
      ;;
  esac

# no argument
else
  printf "no argument given\n\n"
fi
