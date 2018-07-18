# This Python file uses the following encoding: utf-8
import datetime as dt

# TODO sowas wie 'Update' Klasse um über 'update_limit', 'date_today', und zusammen
# mit 'Table.latestUpdate()' und 'Table.update_rate' berechnen wie lange letztes
# update in table her war -> braucht schema
# braucht stock_id oder stock mit isin
from finData.dbconnector import DBConnector
from finData.schema import Schema
from finData.stock import Stock

db = DBConnector('findata_test', 'postgres', 'localhost', 5432)
schema = Schema('findata_init2', 'stock', db)
stock = Stock(db, schema)

tl = Timeline(schema, stock)  # error because stock not set
tl.today
tl.table('stock')  # error because stock has no update rate
tl.table('hist_daily')


class Timeline(object):
    """
    Handling timeline information for a Stock object

    today   date today

    table   set table to generate update information for table
    isNew   test if a given time point is new
    """

    #update limit in years
    limit = 20

    def __init__(self, schema, stock):
        if stock._id is None:
            raise AttributeError('Set Stock object first with "exists" method')
        self._schema = schema
        self._stock = stock
        self.today = dt.date.today()
        self._table = None
        self.last_update = None
        self._type = None
        self.time_missing = None

    def table(self, name):
        """
        Set table to generate update information about it. Sets attributes:

        last_update     latest timepoint for stock in this table
        time_missing    time delta between today and the last update
        """
        if name not in self._schema.tables:
            raise ValueError(
                'Table %s not defined in schema %s' % (name, self._schema.name))
        self._table = self._schema.table(name)
        self.last_update = self._table.lastUpdate(self._stock._id)
        time_column = self.table.time_column
        self.type = self.table.column(time_column).type
        self.years_missing = self._getMissingYears()
        self.days_missing = self._getMissingDays()

    def isNew(self, timepoint):
        """
        Tell if date or year is newer than last update for stock in set table
        """
        if self._table is None:
            raise AttributeError('Set table first with "table" method')
        pass

    def _getMissingYears(self):
        pass

    def _getMissingDays(self):
        pass
