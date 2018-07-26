# This Python file uses the following encoding: utf-8
from data.schemata.schema_init2 import schema_init2 as schema
from psycopg2.extensions import AsIs
import psycopg2 as pg
import pandas as pd
import argparse
import pickle
import numpy


def connector(dbname, user, host, port, password=""):
    if password == "":
        return pg.connect(dbname=dbname, user=user, host=host, port=port)
    else:
        return pg.connect(dbname=dbname, user=user, host=host, port=port, password=password)


def insert(schema, table, args, conn):
    keys = list(args.keys())
    keys.sort()
    cols = ','.join(keys)
    vals = '%({})s'.format(')s,%('.join(keys))
    query = """INSERT INTO {schema}.{table} ({cols}) VALUES ({vals})""" \
        .format(schema=schema, table=table, cols=cols, vals=vals)
    with conn.cursor() as cur:
        cur.execute(query, args)


def insertStock(stock, conn, schema_name):

        # insert stock
        info = stock.get('stock')
        args = {
            'name': info['name'], 'isin': info['isin'],
            'currency': info['currency'], 'boerse_name': info['boerse_name'],
            'avan_ticker': info['avan_ticker']}
        insert(schema_name, 'stock', args, conn)

        # get inserted stock id
        query = "SELECT id FROM {}.stock WHERE isin = %(isin)s".format(schema_name)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, {'isin': info['isin']})
                stock_id = cur.fetchone()[0]

        # insert hist
        df = stock['hist']
        for i in range(df.shape[0]):
            row = df.iloc[i].to_dict()
            row['stock_id'] = stock_id
            insert(schema_name, 'hist_daily', row, conn)

        # insert divid
        df = stock['divid']
        for i in range(df.shape[0]):
            row = df.iloc[i].to_dict()
            row['stock_id'] = stock_id
            insert(schema_name, 'divid_yearly', row, conn)

        # get fund columns
        query = ("""SELECT column_name FROM information_schema.columns """
                 """WHERE table_schema = %(schema)s AND table_name = %(tab)s""")
        args = {'schema': schema_name, 'tab': 'fundamental_yearly'}
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, args)
                res = cur.fetchall()
        fund_columns = [d[0] for d in res]

        # insert fund
        df = pd.DataFrame(stock['guv'])
        guv = df[['year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena']]
        df = pd.DataFrame(stock['bilanz'])
        bilanz = df[['umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb', 'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote']]
        df = pd.DataFrame(stock['kennza'])
        kennza = df[['gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV']]
        df = pd.DataFrame(stock['rentab'])
        rentab = df[['umsatzren', 'eigenkapren', 'geskapren', 'dividren']]
        df = pd.DataFrame(stock['person'])
        person = df[['personal', 'aufwand', 'umsatz', 'gewinn']]
        df = pd.DataFrame(stock['marktk'])
        marktk = df[['zahl_aktien', 'marktkapita']]

        df = pd.concat([guv, bilanz, kennza, rentab, person, marktk], axis=1)
        df.columns = fund_columns[2:]
        for i in range(df.shape[0]):
            row = df.iloc[i].to_dict()
            row['stock_id'] = stock_id
            for key in row:
                if numpy.isnan(row[key]):
                    row[key] = AsIs('NULL')
            insert(schema_name, 'fundamental_yearly', row, conn)


def create(db_name, schema_name, user, host, port, password):
    conn = connector(dbname=db_name, user=user, host=host, port=port, password=password)
    print("Creating schema...")
    with conn:
        schema(schema_name=schema_name, conn=conn)
    print("Populating with some data...")
    with open('test/testdata/testdata.pkl', 'rb') as inf:
        data = pickle.load(inf)
    for ticker in data:
        stock = data.get(ticker)
        insertStock(stock, conn, schema_name)


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
