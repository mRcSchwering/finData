# This Python file uses the following encoding: utf-8
from finData.dbconnector import DBConnector
from finData.schema import Schema
from finData.stock import Stock
from finData.history import History
import psycopg2 as pg
import datetime as dt
import argparse
import sys
import io


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
        res = stock.insert(ADIDAS['name'], ADIDAS['isin'], ADIDAS['currency'],
                           ADIDAS['avan_ticker'], ADIDAS['boerse_name'])
    assert res is False
    assert stock.name == ADIDAS['name']
    assert stock.isin == ADIDAS['isin']
    assert stock.currency == ADIDAS['currency']
    assert stock.boerse_name == ADIDAS['boerse_name']
    assert stock.avan_ticker == ADIDAS['avan_ticker']

    _log('Creating db history of stock')
    history = History(schema, stock._id)
    history.today = dt.date(2018, 7, 29)

    _log('Checking fundamental_yearly table history')
    history.table('fundamental_yearly')
    assert history.update_rate == 'yearly'
    assert history.last_update == 2017
    assert history.years_missing == 1

    _log('Checking divid_yearly table history')
    history.table('divid_yearly')
    assert history.update_rate == 'yearly'
    assert history.last_update == dt.date(2018, 5, 10)
    assert history.years_missing == 0

    _log('Checking hist_daily table history')
    history.table('hist_daily')
    assert history.update_rate == 'daily'
    assert history.last_update == dt.date(2018, 5, 16)
    assert history.days_missing == dt.timedelta(74)

    _log('All good')


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
