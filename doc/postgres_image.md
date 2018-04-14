# Setup Postgres Server

```
PG_NAME="postgres_server"
VOL_NAME="postgres_data"
```

###### Create docker volume

As long as there is a container using this volume, it will be persisted.
If the last container using it is removed, its _dangling_.

```
sudo docker volume create "$VOL_NAME"
```

###### Download and Run Postgres Image

Run docker image (and download if not on host)
as container with name (and hostname of container).

```
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data -p 5432:5432 postgres:9.5.12-alpine
```

- `postgres` runs latest postgres
- `--rm` container will be deleted after stop (good for trying out)
- `-v` flag for defining volume or bind mount in short form
- `vol_name:/path/within/container` volume _vol_name_ must be created before
- `-p` map port `within_container:host_machine`

###### Install Postgres Client

```
sudo apt-get update
sudo apt-get install postgresql-client
```

###### Connect to Postgres Server via Client

`psql` connect to `localhost:5432` with username and password where Postgres server is listening.


```
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
```

###### Look into Running Container

Exec into container starting bash.

```
sudo docker exec -it "$PG_NAME" bash
```

###### Stop Container

```
sudo docker stop "$PG_NAME"
```

This will also remove the container entirely (not the volume though)
because I started the container with `--rm`.
Nice for trying out without persisting every single fucking container.


# Create Database

###### Start Postgres Server

As above, start the created postgres server in a docker container with
ports and volume set.

```
PG_NAME="postgres_server"
VOL_NAME="postgres_data"
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data -p 5432:5432 postgres:9.5.12-alpine
```

###### Create Database and Schema

There is a command tool for logging in and creating a database at once:

```
createdb -h 127.0.0.1 -p 5432 findata -U postgres -w postgres
```

For creating a schema I have to log in.

```
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
```
then
```
\l
\c findata
CREATE SCHEMA IF NOT EXISTS findata_init;
SELECT schema_name FROM information_schema.schemata; # doublechek
```


###### Python API

Creating the tables will be done from python3 using an API.
This will be something that is automated.
Files for table creation and testdata is in `data/`.
Here is some general information about the API.

I'm using `psycopg2` module which commits psql to the server.
The login is quite straight forward.
I have to define host, port and so on, but it looks like using psql.

```
conn = psycopg2.connect("dbname=findata user=postgres password=postgres host=127.0.0.1 port=5432")
with conn:
    with conn.cursor() as curs:
        curs.execute("""CREATE ...""", data)
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


###### Stop Server

```
sudo docker stop "$PG_NAME"
```

# Troubleshooting

###### Check Docker

```
sudo docker ps -a
sudo docker images
sudo docker volume ls
```

###### Check Container and Network

Check all containers (also stopped), images, and volumes

```
sudo docker exec -it "$PG_NAME" bash
```

See postgres server and network status on postgres port.

```
sudo netstat -plunt | grep postgres
sudo netstat -plunt | grep 5432
```

###### Check Database

log into the database...

```
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
```

then psql around...

```
\l
\c findata
\dt
SELECT ...;
```
