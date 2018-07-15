# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs

# TODO Klasse testen


class Stock(object):
    """
    Checking if a stock exists and inserting a new stock
    """

    _id = None
    name = None
    typ = None
    isin = None
    wkn = None
    currency = None
    avan_ticker = None
    boerse_name = None

    _currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD',
                   'INR', 'CNY', 'JPY', 'KRW', 'RUB']

    def __init__(self, db, schema):
        self.db = db
        self.schema = schema

    def exists(self, isin):
        """
        Get stock information by ISIN if exists in stock table
        """
        query = """SELECT * FROM %{schema}s.stock WHERE isin = %{isin}s"""
        args = {'schema': AsIs(self.schema.name), 'isin': isin}
        res = self.db.query(query, args, fetch='one')
        if res is None or len(res) < 1:
            return False
        self._id = res[0]
        self.name = res[1]
        self.isin = res[2]
        self.wkn = res[3]
        self.typ = res[4]
        self.currency = res[5]
        self.boerse_name = res[6]
        self.avan_ticker = res[7]
        return True

    def insert(self, name, typ, isin, wkn, currency, avan_ticker, boerse_name):
        """
        Insert new stock after checking whether it already exists
        """
        infos = [name, typ, isin, wkn, currency, avan_ticker, boerse_name]
        if currency not in self._currencies:
            raise ValueError('currency must be one of %s' % self._currencies)
        stock_exists = self.exists(isin)
        if stock_exists:
            print('{name} (isin: {isin}) not inserted, it already exists'
                  .format(name=name, isin=isin))
            return False
        args = {'schema': AsIs(self.schema.name), 'name': name, 'isin': isin,
                'wkn': wkn, 'typ': typ, 'currency': currency,
                'boerse_name': boerse_name, 'avan_ticker': avan_ticker}
        self.db.query(self.schema.table('stock').insert_statement, args)
        self.exists(isin)
        return True
