#!/usr/bin/env bash

PG_NAME="pg_testcontainer"
VOL_NAME="pg_testvolume"

# container name, and hostname inside container
# rm container and all unnamed volumes after stop
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm -d postgres

# explore container with running postgres server and client
sudo docker exec -it "$PG_NAME" bash
ps aux | grep postgres

# exit the container and see running containers, images
sudo docker ps
sudo docker images
sudo docker volume ls

# stop and remove container (already remove cause of --rm at startup)
sudo docker stop "$PG_NAME"

# create volume and check it out
sudo docker volume create "$VOL_NAME"
sudo docker volume ls

# start container and attach docker volume to pg file path
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data postgres

# exec into container and create db
sudo docker exec -it "$PG_NAME" bash
su - postgres
psql
\x # prettyfy output
\l # list databases
CREATE DATABASE my_testdb;

# stop (also removes) container/ volume still there
sudo docker stop "$PG_NAME"
sudo docker ps -a
sudo docker volume ls

# create container again and check database just created
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data postgres
sudo docker exec -it "$PG_NAME" bash
su - postgres
psql
\x
\l # still there! :)

# stop it (and remove it)
sudo docker stop "$PG_NAME"

# now install the postgresql client on host
sudo apt-get update
sudo apt-get install postgresql-client

# this installs a lot... ensure there's no server listening on host
sudo netstat -plunt | grep postgres
sudo netstat -plunt | grep 5432 # postgres port
# ....ok

# now starting container mapping 5432:5432
sudo docker run --name="$PG_NAME" --hostname="$PG_NAME" --rm  -d -v "$VOL_NAME":/var/lib/postgresql/data -p 5432:5432 postgres
sudo netstat -plunt | grep 5432 # port is listening

# connect to server, defining host, port, user, and password -> see db!
psql -h 127.0.0.1 -p 5432 -U postgres -w postgres
\x
\l

# win!
sudo docker stop "$PG_NAME"



docker run -v /var/run/docker.sock:/var/run/docker.sock -ti docker


# circleci mit mehreren Containern
# ich muss "docker-in-docker" machen, wenn ich mit circleci
# 1. einmal builden möchte und dann den build in nachfolgende jobs übergeben möchte
# 2. ich mehrere container miteinerander kommunizieren lassen möchte
#
# TL;DR
# ich nehme ein reines docekr image mit docker-compose als base image (und git)
# ist setze ein docker in docker auf (da gibts ein paar haken)
# ich baue mein env im docker im docker auf wie gehabt
# zum persistieren kann ich jetzt verschiedene optionen nutzen
# hier macht das eienr mit dem circleci cache:
# https://circleci.com/blog/how-to-build-a-docker-image-on-circleci-2-0/
# mir erscheint es aber sinnvoller im äußeren docker (also das base image von circleci)
# docker save zu machen und das entstandene .tar über einen workspace zu persistieren
# das ist ein directory was ich einhängen kann und was über den workflow persistiert wird
# circleci persistieren in workflows:
# https://circleci.com/docs/2.0/workflows/
