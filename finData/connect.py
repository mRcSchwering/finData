# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import datetime as dt
import pandas as pd
import finData.scrape as fDs
import argparse

# # ./helper.sh start server
# # load conector
# x = Connector('findata', 'testdb', 'postgres', '127.0.0.1', 5432)
#
# # test adding 2018 hist data
# res = x._customSQL("SELECT * FROM testdb.hist WHERE EXTRACT(year FROM datum) = 2018 AND stock_id = 1", fetch=True)
# x._customSQL("""DELETE FROM testdb.hist WHERE EXTRACT(year FROM datum) = 2018 AND stock_id = 1""")
# df = x.updateData()
#
# # test adding 2017 marktk data
# year_tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk']
# res = x._customSQL("SELECT * FROM testdb.marktk WHERE year = 2017 AND stock_id = 1", fetch=True)
# for tab in year_tables:
#         x._customSQL("DELETE FROM testdb.{tab} WHERE year = 2017 AND stock_id = 1".format(tab=tab))
# df = x.updateData()
#
# # test adding 2017 divid data
# res = x._customSQL("SELECT * FROM testdb.divid WHERE EXTRACT(year FROM datum) = 2017 AND stock_id = 1", fetch=True)
# x._customSQL("DELETE FROM testdb.divid WHERE EXTRACT(year FROM datum) = 2017 AND stock_id = 1")
# df = x.updateData()

# traded currencies
currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD', 'INR', 'CNY', 'JPY', 'KRW', 'RUB']


class Connector(object):
    """DB Connector for SELECTing and INSERTing data"""

    # update limit in years (going into the past from today)
    update_limit = 20

    # tables with yearly or daily indices (and updates)
    # or with a date index which represents the whole year
    year_tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk']
    day_tables = ['hist']
    date_tables = ['divid']

    # column definitions as in DB schema
    col_def = {
        'guv': ['stock_id', 'year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena'],
        'bilanz': ['stock_id', 'year', 'umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb', 'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote'],
        'kennza': ['stock_id', 'year', 'gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV'],
        'rentab': ['stock_id', 'year', 'umsatzren', 'eigenkapren', 'geskapren', 'dividren'],
        'person': ['stock_id', 'year', 'personal', 'aufwand', 'umsatz', 'gewinn'],
        'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita'],
        'divid': ['stock_id', 'datum', 'dividende', 'veraenderu', 'rendite'],
        'hist': ['stock_id', 'datum', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'divid_amt', 'split_coef']
    }

    def __init__(self, db_name, schema_name, user, host, port, password=""):
        self.schema_name = str(schema_name)
        self.db_name = str(db_name)
        self.user = str(user)
        self.host = str(host)
        self.port = int(port)
        self.password = str(password)
        self.insert_statements = Connector._prepareInsertStatements()
        self.minimum_date = Connector.todayMinusUpdateLimit()
        self.conn = self._connect()

    def insertStock(self, name, isin, wkn, typ, currency, boerse_name, avan_ticker):
        """Insert stock symbol into stocks table if not already exists"""
        res = self.stockIdFromISIN(isin)
        if res is not None and len(res) > 0:
            with self.conn as con:
                print('{name} (isin: {isin}) not inserted, it already exists'
                      .format(name=name, isin=isin))
                self.stock_id = res[0]
        else:
            self._unsaveInsertStock(name, isin, wkn, typ, currency,
                                    boerse_name, avan_ticker)
            res = self.stockIdFromISIN(isin)
            print('{name} (isin: {isin}) inserted'.format(name=name, isin=isin))
            self.stock_id = res[0]

    def updateData(self):
        """Bring data for each stock symbol in database up to todays date"""
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute("""SELECT id, name, isin FROM %(schema)s.stock""",
                            {'schema': AsIs(self.schema_name)})
                stockIds = cur.fetchall()
        n = len(stockIds)
        for i in range(n):
            print("\n[{i}/{n}]\tUpdating {name} ({isin})..."
                  .format(i=i+1, n=n, name=stockIds[i][1], isin=stockIds[i][2]))
            self.updateSingleStock(stockIds[i][0])
        print("...done")
        return True

    def stockIdFromISIN(self, isin):
        """Get database primary key for stock from ISIN"""
        query = """SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s"""
        args = {'schema': AsIs(self.schema_name), 'isin': isin}
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(query, args)
                return cur.fetchone()

    def updateSingleStock(self, stockId):
        """Bring data for a single stock symbol up to todays date"""
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute("""SELECT * FROM %(schema)s.stock WHERE id = %(id)s""",
                            {'schema': AsIs(self.schema_name), 'id': stockId})
                res = cur.fetchone()[1:]
        stockInfo = {
            'name': res[0],
            'isin': res[1],
            'wkn': res[2],
            'typ': res[3],
            'currency': res[4],
            'boerse_name': res[5],
            'avan_ticker': res[6]
        }
        stock = fDs.Scraper(name=stockInfo['name'], isin=stockInfo['isin'],
                            currency=stockInfo['currency'], wkn=stockInfo['wkn'],
                            boerse_name=stockInfo['boerse_name'], typ=stockInfo['typ'],
                            avan_ticker=stockInfo['avan_ticker'])
        self.updateYearTables(stock, stockId)
        self.updateDateTables(stock, stockId)
        self.updateDayTables(stock, stockId)

    def updateDayTables(self, stock, stockId):
        """Bring tables with dayly entries up to todays date for a single stock symbol"""
        today = dt.date.today()
        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.day_tables)
        lastEnteredDay = max(x for x in dates + [self.minimum_date] if x is not None)
        nMissingDays = today - lastEnteredDay
        missingDays = [today - dt.timedelta(days=x) for x in range(1, nMissingDays.days)]
        Connector.printMissingTimepoints(missingDays, 'days')
        if len(missingDays) > 0:
            #print('\t{n} missing days...'.format(n=len(missingDays)))
            if len(missingDays) > 100:
                stock.getHistoricPrices(onlyLast100=False)
            else:
                stock.getHistoricPrices(onlyLast100=True)
            self._updateTables(stock, stockId, 'day', missingDays)

    def updateDateTables(self, stock, stockId):
        """Bring tables with yearly entries based on a single date up to todays date for a single stock symbol"""
        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.date_tables)
        years = [d.year for d in dates] + [self.minimum_date.year]
        lastEnteredYear = max(x for x in years if x is not None)
        missingYears = list(range(lastEnteredYear + 1, dt.date.today().year + 1))
        Connector.printMissingTimepoints(missingYears, 'years')
        if len(missingYears) > 0:
            stock.getDividendTable()
            self._updateTables(stock, stockId, 'date', missingYears)

    def updateYearTables(self, stock, stockId):
        """Bring tables with yearly entries up to todays date for a single stock symbol"""
        years = self._getLastEnteredTimepoints('year', stockId, Connector.year_tables)
        highestYear = max(x for x in years + [self.minimum_date.year] if x is not None)
        missingYears = list(range(highestYear + 1, dt.date.today().year + 1))
        Connector.printMissingTimepoints(missingYears, 'years')
        #print('\t{n} missing years...'.format(n=len(missingYears)))
        if len(missingYears) > 0:
            stock.getFundamentalTables()
            self._updateTables(stock, stockId, 'year', missingYears)

    def _updateTables(self, stock, stockId, tableType, timepoints):
        """Update all relevant tables for each missing time point"""
        tableTypes = ['day', 'date', 'year']
        if tableType not in tableTypes:
            raise ValueError('tableType must be one of {types}'.format(types=tableTypes))
        tables = {
            'day': Connector.day_tables,
            'year': Connector.year_tables,
            'date': Connector.date_tables
        }
        for tab in tables[tableType]:
            try:
                df = stock.get(tab)
            except ValueError:
                print(("""\nScaper didn't return Table {tab}... """
                       """continuing without it""").format(tab=tab))
            else:
                for tp in timepoints:
                    if tableType == 'day':
                        row = df.loc[[d == tp for d in df['datum']]]
                    if tableType == 'year':
                        row = df.loc[df['year'] == tp]
                    if tableType == 'date':
                        row = df.loc[[d.year == tp for d in df['datum']]]
                    self._insertRow(row, stockId, tab)

    def _getLastEnteredTimepoints(self, colname, stockId, tables):
        """Get last entered timepoint for a list of tables and a stock"""
        query = """SELECT MAX(%(col)s) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s"""
        lastEnteredTimepoints = []
        with self.conn as con:
            with con.cursor() as cur:
                for tab in tables:
                    args = {'col': AsIs(colname), 'tab': AsIs(tab),
                            'schema': AsIs(self.schema_name), 'id': stockId}
                    cur.execute(query, args)
                    lastEnteredTimepoints.append(cur.fetchone()[0])
        return [x for x in lastEnteredTimepoints if x is not None]

    def _unsaveInsertStock(self, name, isin, wkn, typ, currency, boerse_name, avan_ticker):
        """Insert stock without checking whether it already exists"""
        query = ("""INSERT INTO %(schema)s.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) """
                 """VALUES (%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)""")
        args = {'schema': AsIs(self.schema_name), 'name': name, 'isin': isin,
                'wkn': wkn, 'typ': typ, 'currency': currency,
                'boerse_name': boerse_name, 'avan_ticker': avan_ticker}
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(query, args)

    def _insertRow(self, row, stockId, table):
        """Save row insert"""
        if len(row) > 0:
            row = row.where((pd.notnull(row)), None)
            records = row.to_dict(orient='records')[0]
            records['stock_id'] = stockId
            records['schema_name'] = AsIs(self.schema_name)
            records['table_name'] = AsIs(table)
            with self.conn as con:
                with con.cursor() as cur:
                    cur.execute(self.insert_statements[table], records)

    def _customSQL(self, statement, fetch=False):
        """Execute psql statement as is and fetchall if needed"""
        res = None
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(statement)
                if fetch:
                    res = cur.fetchall()
        return res

    def _connect(self):
        """Return mere DB connection"""
        if self.password == "":
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port)
        else:
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port, password=self.password)

    @classmethod
    def todayMinusUpdateLimit(cls):
        return dt.date.today() - dt.timedelta(days=cls.update_limit * 365.24)

    @classmethod
    def _prepareInsertStatements(cls):
        sts = {}
        for tab in cls.col_def:
            cols = ','.join(cls.col_def[tab])
            vals = ','.join(['%({v})s'.format(v=v) for v in cls.col_def[tab]])
            loc = '%(schema_name)s.%(table_name)s'
            sts[tab] = """INSERT INTO {loc} ({cols}) VALUES ({vals})""" \
                       .format(cols=cols, vals=vals, loc=loc)
        return sts

    @classmethod
    def printMissingTimepoints(cls, tps, name):
        details = ', '.join(str(x) for x in tps[:5])
        if len(tps) > 5:
            details = details + '...'
        if len(tps) > 0:
            details = '(' + details + ')'
        print('\t{n} missing {s}{d}...'
              .format(n=len(tps), s=name, d=details))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='INSERTing and SELECTing methods', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    def fun_insert(args):
        connector = Connector(args.db_name, args.db_schema, args.user,
                              args.host, args.port, args.password)
        connector.insertStock(args.name, args.ISIN, args.WKN, args.type,
                              args.currency, args.boerse_name, args.avan_ticker)

    def fun_update(args):
        print('updating')
        connector = Connector(args.db_name, args.db_schema, args.user,
                              args.host, args.port, args.password)
        connector.updateData()

    # main parser for connection
    parser.add_argument('--schema', dest='db_schema', type=str, help='schema name', required=True)
    parser.add_argument('--db', dest='db_name', type=str, help='database name', default='findata')
    parser.add_argument('--user', dest='user', type=str, help='user name', default='postgres')
    parser.add_argument('--pass', dest='password', type=str, default='', help='user password if any')
    parser.add_argument('--port', dest='port', type=int, help='port', default=5432)
    parser.add_argument('--host', dest='host', type=str, help='host', default='server')

    # insert stock subparser
    parser_insert = subparsers.add_parser('insert', help='Insert new stock symbol into database')
    parser_insert.add_argument('name', type=str, help='stock name')
    parser_insert.add_argument('ISIN', type=str, help='ISIN of stock')
    parser_insert.add_argument('WKN', type=str, help='WKN of stock')
    parser_insert.add_argument('currency', type=str, choices=currencies, help='traded currency')
    parser_insert.add_argument('boerse_name', type=str, help='Name used by boerse.de to request data for this stock')
    parser_insert.add_argument('avan_ticker', type=str, help='Ticker as used by alphavantage API')
    parser_insert.add_argument('--type', dest='type', type=str, help='Currently unused', default='Aktie')
    parser_insert.set_defaults(func=fun_insert)

    # update data subparser
    parser_update = subparsers.add_parser('update', help='Update all tables for each stock in database')
    parser_update.set_defaults(func=fun_update)

    # run commands
    args = parser.parse_args()
    args.func(args)
