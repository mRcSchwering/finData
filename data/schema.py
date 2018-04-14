# This Python file uses the following encoding: utf-8
import psycopg2
from psycopg2.extensions import AsIs

schema_name = 'findata_init'
conn_string = 'dbname=findata user=postgres password=postgres host=127.0.0.1 port=5432'


def main():
    conn = psycopg2.connect(conn_string)

    with conn:
        with conn.cursor() as curs:
                curs.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.%(table_name)s (
                      id          INTEGER PRIMARY KEY,
                      name        VARCHAR(50) NOT NULL,
                      isin        VARCHAR(50) UNIQUE NOT NULL,
                      wkn         VARCHAR(50) UNIQUE NOT NULL,
                      typ         VARCHAR(10) NOT NULL,
                      currency    VARCHAR(5) NOT NULL,
                      boerse_name VARCHAR(50) UNIQUE NOT NULL,
                      avan_ticker VARCHAR(50) UNIQUE NOT NULL
                    );
                """, {'schema_name': AsIs(schema_name), 'table_name': AsIs('stock')})

    conn.close()


if __name__ == '__main__':
    main()
