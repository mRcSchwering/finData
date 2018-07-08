# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import datetime as dt
import pandas as pd
import finData.scrape as fDs
import argparse

# TODO connector vllt in DB aktionen aufteilen zB Connector klasse (nur fürs connecten)


# traded currencies
currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD', 'INR', 'CNY', 'JPY', 'KRW', 'RUB']


class Connector(object):
    """DB Connector for SELECTing and INSERTing data"""

    # update limit in years (going into the past from today)
    update_limit = 20  # TODO sollte in main

    # TODO schema benutzen

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
        # TODO Liste von Scrapers/Requesters setzen (siehe unten)

    # TODO vllt diesen hier ausbauen und wiederverwenden
    def customSQL(self, statement, fetch=False):  # None, one, all
        """
        Execute psql statement as is and fetchall if needed
        """
        res = None
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(statement)
                if fetch:
                    res = cur.fetchall()
        return res

    # TODO stock Id vllt als attribut setzen (wird häufiger gebraucht, siehe unten)

    def stockIdFromISIN(self, isin):
        """
        Get database primary key for stock from ISIN
        """
        query = """SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s"""
        args = {'schema': AsIs(self.schema_name), 'isin': isin}
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(query, args)
                res = cur.fetchone()
        return res

    def insertStock(self, name, isin, wkn, typ, currency, boerse_name, avan_ticker):
        """
        Insert stock without checking whether it already exists
        """
        query = ("""INSERT INTO %(schema)s.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) """
                 """VALUES (%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)""")
        args = {'schema': AsIs(self.schema_name), 'name': name, 'isin': isin,
                'wkn': wkn, 'typ': typ, 'currency': currency,
                'boerse_name': boerse_name, 'avan_ticker': avan_ticker}
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(query, args)

    # TODO identify from Schema class which table needs to be updated
    # also I would provide a list of scrapers/requesters (3 defs below)

    def updateDayTables(self, stock, stockId):
        """
        Bring tables with daily entries up to todays date for a single stock symbol
        """
        today = dt.date.today()
        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.day_tables)
        lastEnteredDay = max(x for x in dates + [self.minimum_date] if x is not None)
        nMissingDays = today - lastEnteredDay
        missingDays = [today - dt.timedelta(days=x) for x in range(1, nMissingDays.days)]
        Connector.printMissingTimepoints(missingDays, 'days')
        if len(missingDays) > 0:
            if len(missingDays) > 100:
                stock.getHistoricPrices(onlyLast100=False)
            else:
                stock.getHistoricPrices(onlyLast100=True)
            self._updateTables(stock, stockId, 'day', missingDays)

    def updateDateTables(self, stock, stockId):
        """
        Bring tables with yearly entries based on a single date up to todays date for a single stock symbol
        """
        dates = self._getLastEnteredTimepoints('datum', stockId, Connector.date_tables)
        years = [d.year for d in dates] + [self.minimum_date.year]
        lastEnteredYear = max(x for x in years if x is not None)
        missingYears = list(range(lastEnteredYear + 1, dt.date.today().year + 1))
        Connector.printMissingTimepoints(missingYears, 'years')
        if len(missingYears) > 0:
            stock.getDividendTable()
            self._updateTables(stock, stockId, 'date', missingYears)

    def updateYearTables(self, stock, stockId):
        """
        Bring tables with yearly entries up to todays date for a single stock symbol
        """
        years = self._getLastEnteredTimepoints('year', stockId, Connector.year_tables)
        highestYear = max(x for x in years + [self.minimum_date.year] if x is not None)
        missingYears = list(range(highestYear + 1, dt.date.today().year + 1))
        Connector.printMissingTimepoints(missingYears, 'years')
        if len(missingYears) > 0:
            stock.getFundamentalTables()
            self._updateTables(stock, stockId, 'year', missingYears)

    # TODO stock, sollte kein argument sein sondern attribut
    # bzw wie oben genannt ne liste von Klassen
    # also in __init__ setzen

    # TODO stock_id könnte man auch so übergeben, da seriell

    def _updateTables(self, stock, stockId, tableType, timepoints):
        """
        Update all relevant tables for each missing time point
        """
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
        """
        Get last entered timepoint for a list of tables and a stock
        """
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

    def _insertRow(self, row, stockId, table):
        """
        Save row insert
        """
        if len(row) > 0:
            row = row.where((pd.notnull(row)), None)
            records = row.to_dict(orient='records')[0]
            records['stock_id'] = stockId
            records['schema_name'] = AsIs(self.schema_name)
            records['table_name'] = AsIs(table)
            with self.conn as con:
                with con.cursor() as cur:
                    cur.execute(self.insert_statements[table], records)

    def _connect(self):
        """
        Return mere DB connection
        """
        if self.password == "":
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port)
        else:
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port, password=self.password)

    # TODO cls.update_limit sollte in main angegeben werden
    @classmethod
    def todayMinusUpdateLimit(cls):
        return dt.date.today() - dt.timedelta(days=cls.update_limit * 365.24)

    # TODO die hier könnten aus Schema Klasse kommen (zumindest col_def)
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
