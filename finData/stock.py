# This Python file uses the following encoding: utf-8


class Stock(object):
    """
    Checking if a stock exists and inserting a new stock
    """

    _id = None
    name = None
    isin = None
    currency = None
    avan_ticker = None
    boerse_name = None

    _currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD',
                   'INR', 'CNY', 'JPY', 'KRW', 'RUB']

    def __init__(self, db, schema):
        self._db = db
        self._schema = schema

    def exists(self, isin):
        """
        Get stock information by ISIN if exists in stock table
        """
        query = """SELECT * FROM {schema}.stock WHERE isin = %(isin)s""" \
                .format(schema=self._schema.name)
        args = {'isin': isin}
        res = self._db.query(query, args, fetch='one')
        if res is None or len(res) < 1:
            return False
        self._id = res[0]
        self.name = res[1]
        self.isin = res[2]
        self.currency = res[3]
        self.boerse_name = res[4]
        self.avan_ticker = res[5]
        return True

    def insert(self, name, isin, currency, avan_ticker, boerse_name):
        """
        Insert new stock after checking whether it already exists
        """
        infos = [name, isin, currency, avan_ticker, boerse_name]
        if currency not in self._currencies:
            raise ValueError('currency must be one of %s' % self._currencies)
        stock_exists = self.exists(isin)
        if stock_exists:
            print('{name} (isin: {isin}) not inserted, it already exists'
                  .format(name=self.name, isin=self.isin))
            return False
        args = {'name': name, 'isin': isin, 'currency': currency,
                'boerse_name': boerse_name, 'avan_ticker': avan_ticker}
        res = self._schema.table('stock').insertRow(args)
        if res:
            self.exists(isin)
            return True
        raise ValueError('Nothing inserted, given values were: %s' % infos)
