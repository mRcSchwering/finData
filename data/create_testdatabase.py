# This Python file uses the following encoding: utf-8
from data.schemata.schema_init import schema_init as schema  # the current schema
from psycopg2.extensions import AsIs
import psycopg2
import argparse


def connector(dbname, user, host, port, password=""):
    if password == "":
        return psycopg2.connect(dbname=dbname, user=user, host=host, port=port)
    else:
        return psycopg2.connect(dbname=dbname, user=user, host=host, port=port, password=password)


def create(db_name, schema_name, user, host, port, password):
    print("Creating schema...")
    conn = connector(dbname=db_name, user=user, host=host, port=port, password=password)
    schema(schema_name=schema_name, conn=conn)
    


def drop(db_name, schema_name, user, host, port, password):
    print("Dropping schema...")
    conn = connector(dbname=db_name, user=user, host=host, port=port, password=password)
    with conn:
        with conn.cursor() as cur:
                cur.execute("""DROP SCHEMA IF EXISTS %(schema_name)s CASCADE""",
                            {'schema_name': AsIs(schema_name)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create separate schema and fill it with data')
    parser.add_argument('--db', dest='db_name', type=str, help='database name in which schema is created', required=True)
    parser.add_argument('--schema', dest='schema_name', type=str, help='name of new schema', required=True)
    parser.add_argument('--user', dest='user', type=str, help='user name', required=True)
    parser.add_argument('--pass', dest='password', type=str, default="", help='set password if any')
    parser.add_argument('--port', dest='port', type=str, help='set port as str', required=True)
    parser.add_argument('--host', dest='host', type=str, help='set host as str', required=True)
    parser.add_argument('--drop', dest='drop', action='store_const', const=drop, default=create, help='drop this schema instead of creating it')
    args = parser.parse_args()

    args.drop(db_name=args.db_name, schema_name=args.schema_name, user=args.user,
              password=args.password, host=args.host, port=args.port)
