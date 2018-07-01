# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import finData.connect as fDc
import argparse
import sys
import io


adidas = ['Adidas', 'DE000A1EWWW0', 'A1EWWW', 'Aktie', 'EUR', 'Adidas-Aktie', 'ADS.DE']


def _log(msg):
    print("\n\n" + msg + "\n" + "#" * 40 + "\n")


class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


def main(db_name, schema_name, user, host, port, password):
    X = fDc.Connector(db_name=db_name, schema_name=schema_name,
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
