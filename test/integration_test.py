# This Python file uses the following encoding: utf-8
from finData.dbconnector import DBConnector
from finData.schema import Schema
from finData.stock import Stock
from psycopg2.extensions import AsIs
import psycopg2 as pg
import argparse
import sys
import io
import re


# used several times
ADIDAS = {'name': 'Adidas', 'isin': 'DE000A1EWWW0', 'currency': 'EUR',
          'boerse_name': 'Adidas-Aktie', 'avan_ticker': 'ADS.DE'}


# visually separating tests
def _log(msg):
    print("\n\n" + msg + "\n" + "#" * 40 + "\n")


# silencing
class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


def main(db_name, schema_name, user, host, port, password):

    _log("Set up classes")
    db = DBConnector(db_name, user, host, port, password)
    schema = Schema(schema_name, 'stock', db)
    stock = Stock(db, schema)

    _log("Query stock using DBConnector")
    query = """SELECT id FROM {}.stock""".format(schema_name)
    res = db.query(query, {}, 'all')
    assert len(res) == 7

    _log("Trying to insert doublicate stock using schema")
    try:
        schema.table('stock').insertRow(ADIDAS)
    except pg.IntegrityError:
        _log("IntegrityError raised, UNIQUE constraint enforced")
    else:
        raise AssertionError("UNIQUE constraint was not enforced")

    _log("Trying to insert doublicate stock using stock")
    with catchStdout():
        stock.insert(ADIDAS['name'], ADIDAS['isin'], ADIDAS['currency'],
                     ADIDAS['avan_ticker'], ADIDAS['boerse_name'])
    assert stock.name == ADIDAS['name']
    assert stock.isin == ADIDAS['isin']
    assert stock.currency == ADIDAS['currency']
    assert stock.boerse_name == ADIDAS['boerse_name']
    assert stock.avan_ticker == ADIDAS['avan_ticker']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run integration tests')
    parser.add_argument('--db', dest='db_name', type=str, help='database name in which schema is created', required=True)
    parser.add_argument('--schema', dest='schema_name', type=str, help='name of new schema', required=True)
    parser.add_argument('--user', dest='user', type=str, help='user name', required=True)
    parser.add_argument('--pass', dest='password', type=str, default="", help='user password if any')
    parser.add_argument('--port', dest='port', type=str, help='set port as str', required=True)
    parser.add_argument('--host', dest='host', type=str, help='set host as str', required=True)
    args = parser.parse_args()

    main(db_name=args.db_name, schema_name=args.schema_name, user=args.user,
         password=args.password, host=args.host, port=args.port)
