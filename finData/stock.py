# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs


class Stock(object):

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

    def exists(self):
        pass

    def insert(self, name, typ, isin, wkn, currency, avan_ticker, boerse_name):
        if currency not in self._currencies:
            raise ValueError('currency must be one of %s' % self._currencies)
        res = self._queryISIN(isin, name)
        if res not None and len(res) > 0:
            print('{name} (isin: {isin}) not inserted, it already exists'
                  .format(name=name, isin=isin))
        else:
            res = self._insertNewStock(name, typ, isin, wkn,
                                       currency, avan_ticker, boerse_name)
        self._id = res[0]
        self.name = res[1]
        self.isin = res[2]
        self.wkn = res[3]
        self.typ = res[4]
        self.currency = res[5]
        self.boerse_name = res[6]
        self.avan_ticker = res[7]
        return True

    def _queryISIN(self, isin, name):
        query = """SELECT * FROM %{schema}s.stock WHERE isin = %{isin}s"""
        args = {'schema': AsIs(self.schema.name), 'isin': isin}
        return self.db.query(query, args, fetch='one')

    def _insertNewStock(self, name, typ, isin, wkn, currency,
                        avan_ticker, boerse_name):
        query = """INSERT INTO %{schema}s.stock () VALUES ()"""
        self.db.query(query, args)
