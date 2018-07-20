# This Python file uses the following encoding: utf-8
from finData.dbconnector import DBConnector
from finData.schema import Schema
from finData.stock import Stock
from psycopg2.extensions import AsIs
import pickle
import numpy
import pandas as pd

# Setup
db_name = 'findata_test'
schema_name = 'findata_init2'
host = 'localhost'
port = 5432
user = 'postgres'
password = ''

db = DBConnector(db_name, user, host, port, password)
schema = Schema(schema_name, 'stock', db)
stock = Stock(db, schema)

with open('test/testdata/testdata.pkl', 'rb') as inf:
    data = pickle.load(inf)


# Insert Stock
DBK = data.get('DBK.DE')
assert stock.exists(DBK['stock']['isin']) is False

res = stock.insert(DBK['stock']['name'], DBK['stock']['isin'],
                   DBK['stock']['currency'], DBK['stock']['avan_ticker'],
                   DBK['stock']['boerse_name'])
assert res is True

res = stock.insert(DBK['stock']['name'], DBK['stock']['isin'],
                   DBK['stock']['currency'], DBK['stock']['avan_ticker'],
                   DBK['stock']['boerse_name'])
assert res is False

assert stock.exists(DBK['stock']['isin']) is True


# Insert Hist
df = DBK['hist']
for i in range(df.shape[0]):
    row = df.iloc[i].to_dict()
    row['stock_id'] = stock._id
    hist = schema.table('hist_daily')
    assert hist.insertRow(row) is True

# Insert Divid
df = DBK['divid']
for i in range(df.shape[0]):
    row = df.iloc[i].to_dict()
    row['stock_id'] = stock._id
    divid = schema.table('divid_yearly')
    assert divid.insertRow(row) is True

# Insert Fund
fund = schema.table('fundamental_yearly')
df = pd.DataFrame(DBK['guv'])
guv = df[['year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena']]
df = pd.DataFrame(DBK['bilanz'])
bilanz = df[['umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb', 'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote']]
df = pd.DataFrame(DBK['kennza'])
kennza = df[['gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV']]
df = pd.DataFrame(DBK['rentab'])
rentab = df[['umsatzren', 'eigenkapren', 'geskapren', 'dividren']]
df = pd.DataFrame(DBK['person'])
person = df[['personal', 'aufwand', 'umsatz', 'gewinn']]
df = pd.DataFrame(DBK['marktk'])
marktk = df[['zahl_aktien', 'marktkapita']]

df = pd.concat([guv, bilanz, kennza, rentab, person, marktk], axis=1)
df.columns = fund.columns[2:]
for i in range(df.shape[0]):
    row = df.iloc[i].to_dict()
    row['stock_id'] = stock._id
    for key in row:
        if numpy.isnan(row[key]):
            row[key] = AsIs('NULL')
    assert fund.insertRow(row) is True


# Insert Another Stock
data = data.get('ADS.DE')
assert stock.exists(data['stock']['isin']) is False

res = stock.insert(data['stock']['name'], data['stock']['isin'],
                   data['stock']['currency'], data['stock']['avan_ticker'],
                   data['stock']['boerse_name'])
assert res is True

res = stock.insert(data['stock']['name'], data['stock']['isin'],
                   data['stock']['currency'], data['stock']['avan_ticker'],
                   data['stock']['boerse_name'])
assert res is False

assert stock.exists(data['stock']['isin']) is True





sts = """SELECT MAX(datum) FROM findata_init2.hist_daily WHERE stock_id = 2"""
res = db.query(sts, {}, 'all')
res

# ####### OLD CODE ########
def connector(dbname, user, host, port, password=""):
    if password == "":
        return pg.connect(dbname=dbname, user=user, host=host, port=port)
    else:
        return pg.connect(dbname=dbname, user=user, host=host, port=port, password=password)


def insertStatement(schema, table, cols, vals):
    return """INSERT INTO {schema}.{table} ({cols}) VALUES {vals}""" \
           .format(schema=AsIs(schema), table=AsIs(table),
                   cols=cols, vals='({})'.format('),('.join(vals)))


def inserTestdata(data, conn, schema_name):
    # insert stock, DB increments stock id
    cols = ','.join(['name', 'isin', 'wkn', 'typ',
                     'currency', 'boerse_name', 'avan_ticker'])
    vals = [stock_cols.format(**data[t]['stock']) for t in data]
    with conn.cursor() as cur:
        cur.execute(insertStatement(schema_name, 'stock', cols, vals))
        cur.execute("""SELECT id, avan_ticker FROM {schema}.stock"""
                    .format(schema=schema_name))
        stock_ids = cur.fetchall()

    # for each stock get stock id and insert all tables
    for stock in data:
        stock_id = [tup[0] for tup in stock_ids if tup[1] == stock][0]
        with conn.cursor() as cur:
            for tab in tab_cols:
                d = data[stock][tab].fillna('NULL')
                cols = ','.join(['stock_id'] + d.columns.tolist())
                vals = [tab_cols[tab].format(**r) for i, r in d.iterrows()]
                vals = [','.join([str(stock_id), v]) for v in vals]
                cur.execute(insertStatement(schema_name, tab, cols, vals))


def create(db_name, schema_name, user, host, port, password):
    conn = connector(dbname=db_name, user=user, host=host, port=port, password=password)
    with conn:
        print("Creating schema...")
        schema(schema_name=schema_name, conn=conn)
        print("Populating with some data...")
        with open('test/testdata/testdata.pkl', 'rb') as inf:
            data = pickle.load(inf)
        inserTestdata(data, conn, schema_name)


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
