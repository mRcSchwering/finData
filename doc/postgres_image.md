# Postgres Image

### Setup

```
PG_NAME="postgres_server"
VOL_NAME="postgres_data"
```


### Create docker volume

As long as there is a container using this volume, it will be persisted.
If the last container using it is removed, its _dangling_.

```
sudo docker volume create "$VOL_NAME"
```

### Download and Run Postgres Image

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

### Check Container and Network

Check all containers (also stopped), images, and volumes

```
sudo docker ps -a
sudo docker images
sudo docker volume ls
```

See postgres server and network status on postgres port.

```
sudo netstat -plunt | grep postgres
sudo netstat -plunt | grep 5432
```

### Install Postgres Client

```
sudo apt-get update
sudo apt-get install postgresql-client
```

### Connect to Postgres Server via Client

`psql` connect to `localhost:5432` with username and password where Postgres server is listening.


```
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
```

### Look into Running Container

Exec into container starting bash.

```
sudo docker exec -it "$PG_NAME" bash
```

### Stop Container

```
sudo docker stop "$PG_NAME"
```

This will also remove the container entirely (not the volume though)
because I started the container with `--rm`.
Nice for trying out without persisting every single fucking container.
