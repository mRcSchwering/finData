# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import datetime as dt
import pandas as pd
import finData.scrape as fDs

# TODO refactor
# TODO bessere tests
# TODO update data tests

# # ./helper.sh start server
# # load conector
# x = Connector('findata', 'testdb', 'postgres', '127.0.0.1', 5432)
#
# x._customSQL("SELECT * FROM testdb.marktk WHERE year > 2016", fetch=True)
# res = x._customSQL("SELECT MAX(datum) FROM testdb.hist WHERE stock_id = 1", fetch=True)
# res = x._customSQL("SELECT * FROM testdb.hist WHERE stock_id = 1 AND datum = ( SELECT MAX(datum) FROM testdb.hist WHERE stock_id = 1 )", fetch=True)
# res
#
#
# x._customSQL(("""INSERT INTO testdb.marktk (stock_id,year,zahl_aktien,marktkapita)"""
#              """ VALUES (1, 9999, NULL,0.99)"""))
# x._customSQL("""DELETE FROM testdb.marktk WHERE year = 9999""")
# x._customSQL("""DELETE FROM testdb.marktk WHERE year = 2017""")
#
# df = x.updateData()
# row = df.loc[[d.year == 2011 for d in df['datum']]]
# row = row.where((pd.notnull(row)), None)
# records = row.to_dict(orient='records')[0]
#
# ids = x.updateData()
# today = dt.datetime.now().date()
# today.day


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
        self.conn = self._connect()

    def insertStock(self, name, isin, wkn, typ, currency, boerse_name, avan_ticker):
        """Insert stock symbol into stocks table if not already exists"""
        with self.conn as con:

            # check out if stock exists
            with con.cursor() as cur:
                cur.execute("""SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s""",
                            {'schema': AsIs(self.schema_name), 'isin': isin})
                res = cur.fetchall()

            # set id if it exists already
            if len(res) > 0:
                print('{name} (isin: {isin}) not inserted, it already exists'
                      .format(name=name, isin=isin))
                self.stock_id = res[0][0]

            # insert and get id if it didnt exist
            else:
                with con.cursor() as cur:
                    cur.execute(
                        """INSERT INTO %(schema)s.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) VALUES (%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)""",
                        {'schema': AsIs(self.schema_name), 'name': name, 'isin': isin, 'wkn': wkn, 'typ': typ, 'currency': currency, 'boerse_name': boerse_name, 'avan_ticker': avan_ticker}
                    )
                    cur.execute("""SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s""",
                                {'schema': AsIs(self.schema_name), 'isin': isin})
                    res = cur.fetchall()
                print('{name} (isin: {isin}) inserted'.format(name=name, isin=isin))
                self.stock_id = res[0][0]

    def updateData(self):
        """Bring data for each stock symbol in database up to todays date"""
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute("""SELECT id, name, isin FROM %(schema)s.stock""",
                            {'schema': AsIs(self.schema_name)})
                stockIds = cur.fetchall()

        # TODO: reduce while trying out
        stockIds = stockIds[:1]

        n = len(stockIds)
        for i in range(n):
            print("[{i}/{n}] Updating {name} ({isin})..."
                  .format(i=i+1, n=n, name=stockIds[i][1], isin=stockIds[i][2]))
            self._updateSingleStock(stockIds[i][0])
            print("...done")
        return True

    def _updateSingleStock(self, stockId):
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
        # self._updateYearTables(stock, stockId)
        # self._updateDateTables(stock, stockId)
        self._updateDayTables(stock, stockId)

    def _updateDayTables(self, stock, stockId):
        """Bring tables with dayly entries up to todays date for a single stock symbol"""

        today = dt.date.today()
        aveDaysPerYear = 365.24
        minimumDay = today - dt.timedelta(days=Connector.update_limit * aveDaysPerYear)

        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.day_tables)
        lastEnteredDay = max(x for x in dates + [minimumDay] if x is not None)

        nMissingDays = today - lastEnteredDay
        missingDays = [today - dt.timedelta(days=x) for x in range(1, nMissingDays.days)]

        if len(missingDays) > 0:
            if len(missingDays) > 100:
                stock.getHistoricPrices(onlyLast100=False)
            else:
                stock.getHistoricPrices(onlyLast100=True)
            for tab in Connector.day_tables:
                try:
                    df = stock.get(tab)
                except ValueError:
                    print(("""Scaper didn't return Table {tab}... """
                           """continuing without it""").format(tab=tab))
                else:
                    for day in missingDays:
                        row = df.loc[[d == day for d in df['datum']]]
                        self._insertRow(row, stockId, tab)

    def _updateDateTables(self, stock, stockId):
        """Bring tables with yearly entries based on a single date up to todays date for a single stock symbol"""

        thisYear = dt.date.today().year
        minimumYear = thisYear - Connector.update_limit

        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.date_tables)

        years = [d.year for d in dates] + [minimumYear]
        lastEnteredYear = max(x for x in years if x is not None)
        missingYears = list(range(lastEnteredYear + 1, thisYear + 1))

        if len(missingYears) > 0:
            stock.getDividendTable()
            for tab in Connector.date_tables:
                try:
                    df = stock.get(tab)
                except ValueError:
                    print(("""Scaper didn't return Table {tab}... """
                           """continuing without it""").format(tab=tab))
                else:
                    for year in missingYears:
                        row = df.loc[[d.year == year for d in df['datum']]]
                        self._insertRow(row, stockId, tab)

    def _updateYearTables(self, stock, stockId):
        """Bring tables with yearly entries up to todays date for a single stock symbol"""
        thisYear = dt.date.today().year
        minimumYear = thisYear - Connector.update_limit

        years = self._getLastEnteredTimepoints('year', stockId, Connector.year_tables)

        highestYear = max(x for x in years + [minimumYear] if x is not None)
        missingYears = list(range(highestYear + 1, thisYear + 1))

        if len(missingYears) > 0:
            stock.getFundamentalTables()
            for tab in Connector.year_tables:
                try:
                    df = stock.get(tab)
                except ValueError:
                    print(("""Scaper didn't return Table {tab}... """
                           """continuing without it""").format(tab=tab))
                else:
                    for year in missingYears:
                        row = df.loc[df['year'] == year]
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
        return lastEnteredTimepoints

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
    def _prepareInsertStatements(cls):
        sts = {}
        for tab in cls.col_def:
            cols = ','.join(cls.col_def[tab])
            vals = ','.join(['%({v})s'.format(v=v) for v in cls.col_def[tab]])
            loc = '%(schema_name)s.%(table_name)s'
            sts[tab] = """INSERT INTO {loc} ({cols}) VALUES ({vals})""" \
                       .format(cols=cols, vals=vals, loc=loc)
        return sts
