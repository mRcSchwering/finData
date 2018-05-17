# Setup Postgres Server

This is the host setup of the database.
1. create a docker volume
2. download and start postgres image

```
PG_NAME="postgres_server"
VOL_NAME="postgres_data"

docker volume create "$VOL_NAME"
docker run \
  --name="$PG_NAME" \
  --hostname="$PG_NAME" \
  -d \
  -v "$VOL_NAME":/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:9.5.12-alpine
```

Checkout running containers and postgres port.

```
netstat -plunt | grep postgres
netstat -plunt | grep 5432
docker ps
```

Troubleshoot by jumping into the container via `docker exec -it "$PG_NAME" bash`.


# Postgres client

Install via package manager and connect to database.
Here the database is on the host `localhost:543` with user _postgres_.

```
sudo apt-get update
sudo apt-get install postgresql-client

psql -h 127.0.0.1 -p 5432 -U postgres
```


# Create Database

Create database, then log into it.

```
createdb -h 127.0.0.1 -p 5432 findata -U postgres
psql -h 127.0.0.1 -p 5432 -U postgres findata
```

# Secure Docker Volume

A `docker volume prune`, and all volumes without an attached container are gone.
So, I create a throw away container that should lock the volume.

```
docker run \
  --name="DO_NOT_DELETE_ME" \
  -v "$VOL_NAME":/mnt \
  alpine
```

As long as this container exists -- even if it's not running -- the volume
won't get pruned.
But I need to be careful with not deleting the container.



# Psycopg2

Creating the tables will be done from python3 using an API.
This will be something that is automated.
Files for table creation and testdata is in `data/`.
Here is some general information about the API.

I'm using `psycopg2` module which commits psql to the server.
The login is quite straight forward.
I have to define host, port and so on, but it looks like using psql.

```
conn = psycopg2.connect(dbname="findata", user="postgres", host="127.0.0.1", port="5432")
with conn:
    with conn.cursor() as cur:
        cur.execute("""CREATE ...""", data)
conn.close()
```
- Commiting transactions can be done inside `with` statements.
That ensures a rollback if some exception was raised.
- Connection `conn` has to be closed explicitly though.
- For passing data use the second argument of `execute`, that ensures escaping nasty stuff.
They are passed as `dict`.
- Stuff like `datetime` is also handled.

There is another thing... passing a _e.g._ name as parameter needs extra caution
to not add quotes.

```
from psycopg2.extensions import AsIs
curs.execute("""
    CREATE TABLE IF NOT EXISTS %(schema_name)s.%(table_name)s (...)
""", {'schema_name': AsIs('findata_init'), 'table_name': AsIs('stock')})
```

TODO: There is also Two-Phase Commit support... I should use that at some point.
