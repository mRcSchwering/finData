# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import finData.connect as fDc
import argparse
import sys
import io
import re


# used several times
adidas = ['Adidas', 'DE000A1EWWW0', 'A1EWWW', 'Aktie', 'EUR', 'Adidas-Aktie', 'ADS.DE']


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


# reduce updates
class testConnect(fDc.Connector):

    update_limit = 2


def main(db_name, schema_name, user, host, port, password):
    X = testConnect(db_name=db_name, schema_name=schema_name,
                    user=user, host=host, port=port, password=password)

    _log("Show databases have findata")
    res = X._customSQL("SELECT id FROM %s.stock" % schema_name, fetch=True)
    assert len(res) == 7

    _log("Unsafe insert stock douplicate")
    try:
        X._unsaveInsertStock(*adidas)
    except pg.IntegrityError:
        _log("IntegrityError raised, UNIQUE constraint enforced")
    else:
        raise AssertionError("UNIQUE constraint was not enforced")

    _log("Safe insert stock douplicate")
    with catchStdout() as cap:
        X.insertStock(*adidas)
        capture = cap
    expected = '{name} (isin: {isin}) not inserted, it already exists\n' \
               .format(name=adidas[0], isin=adidas[1])
    assert capture.getvalue() == expected

    _log("Insert bad NULL into stock")
    colNames = 'name,isin,wkn,typ,currency,boerse_name,avan_ticker'
    vals = """'test',NULL,'test','test','test','test','test'"""
    try:
        X._customSQL("""INSERT INTO {schema}.stock ({cols}) VALUES ({vals})"""
                     .format(schema=AsIs(schema_name), cols=colNames, vals=vals))
    except pg.IntegrityError:
        _log("IntegrityError raised, NOT NULL constraint enforced")
    else:
        raise AssertionError("NOT NULL constraint was not enforced")

    _log("Get Adidas stock id by ISIN")
    stockId = X.stockIdFromISIN(adidas[1])[0]
    res = X._customSQL("""SELECT isin FROM {schema}.stock WHERE id = {id}"""
                       .format(schema=AsIs(schema_name), id=stockId), fetch=True)
    assert adidas[1] == res[0][0]

    _log("Update Data")
    with catchStdout() as cap:
        X.updateData()
        capture = cap
    print(capture.getvalue())
    # should be at least 40 days behind (for years can be below 2..)
    days = re.findall('([0-9]+) missing days', capture.getvalue())
    years = re.findall('([0-9]+) missing years', capture.getvalue())
    assert 2 * len(days) == len(years)
    assert len(days) == 7
    assert [int(day) >= 40 for day in days] == [True] * len(days)

    _log("Unnecessary data update")
    with catchStdout() as cap:
        X.updateData()
        capture = cap
    print(capture.getvalue())
    # now days and years should be lower because they were updated before
    days = re.findall('([0-9]+) missing days', capture.getvalue())
    years = re.findall('([0-9]+) missing years', capture.getvalue())
    assert 2 * len(days) == len(years)
    assert len(days) == 7
    assert 2 * len(days) == len(years)
    assert [int(day) <= 2 for day in days] == [True] * len(days)
    assert [int(year) <= 1 for year in years] == [True] * len(years)


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
