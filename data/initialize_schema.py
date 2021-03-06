# This Python file uses the following encoding: utf-8
from data.schemata.schema_init2 import schema_init2 as schema
from psycopg2.extensions import AsIs
import psycopg2 as pg
import argparse


def main(db_name, schema_name, user, host, port, password):
    if password == "":
        conn = pg.connect(dbname=db_name, user=user, host=host, port=port)
    else:
        conn = pg.connect(dbname=db_name, user=user, host=host, port=port, password=password)
    with conn:
        schema(schema_name=schema_name, conn=conn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create separate schema and fill it with data')
    parser.add_argument('--db', dest='db_name', type=str, help='database name in which schema is created', required=True)
    parser.add_argument('--schema', dest='schema_name', type=str, help='name of new schema', required=True)
    parser.add_argument('--user', dest='user', type=str, help='user name', required=True)
    parser.add_argument('--pass', dest='password', type=str, default="", help='set password if any')
    parser.add_argument('--port', dest='port', type=str, help='set port as str', required=True)
    parser.add_argument('--host', dest='host', type=str, help='set host as str', required=True)
    args = parser.parse_args()

    main(db_name=args.db_name, schema_name=args.schema_name, user=args.user,
         password=args.password, host=args.host, port=args.port)
