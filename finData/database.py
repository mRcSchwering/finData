# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg
import datetime as dt
import pandas as pd
import finData.scrape as fDs
import argparse

# TODO schema abändern, sodass 3 tabellen entsprehcend dem scraper
# TODO dann zeit columns immer angeben -> year, datum usw
# TODO und yearly, daily oder so als namenskonvention
# TODO dann kann fast alles aus dem schema gelesen werden
# TODO stock table kriegt vermutlich immer noch speziellen Platz

# TODO ASchema sollte Schema sein und Schema sollte Schema_init sein
# wird nur einmal verwenden 'schema = Schema_init' in Facade

# traded currencies
currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD', 'INR', 'CNY', 'JPY', 'KRW', 'RUB']


class Connector(object):
    """
    DB Connector for selecting and inserting data
    """

    # update limit in years (going into the past from today)
    update_limit = 20  # TODO sollte in main

    # TODO schema benutzen

    def __init__(self, db, schema, schema_name):
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

    # TODO identify from Schema class which table needs to be updated
    # also I would provide a list of scrapers/requesters (3 defs below)

    # TODO da schema -> table 1. update rate und 2. date column kennt,
    # kann es selber herausfinden, wie die update rate ist
    # andererseits ist es sinnvoll durch diese 3 Gruppen von Tabellen
    # update zu machen, da das dem scraper entspricht

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

    # TODO cls.update_limit sollte in main angegeben werden
    # da schema Update rate beinhaltet sollte in schema auch die query zum
    # last update definiert werden (schema -> table)
    @classmethod
    def todayMinusUpdateLimit(cls):
        return dt.date.today() - dt.timedelta(days=cls.update_limit * 365.24)

    @classmethod
    def printMissingTimepoints(cls, tps, name):
        details = ', '.join(str(x) for x in tps[:5])
        if len(tps) > 5:
            details = details + '...'
        if len(tps) > 0:
            details = '(' + details + ')'
        print('\t{n} missing {s}{d}...'
              .format(n=len(tps), s=name, d=details))
