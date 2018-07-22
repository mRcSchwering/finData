# This Python file uses the following encoding: utf-8
from finData.history import History
from finData.testing_utils import *
import datetime as dt


def mockSchema(last_update, col_type):
    col = MagicMock()
    col.type = col_type
    table = MagicMock()
    table.time_column = 'time_col'
    table.column = MagicMock(return_value=col)
    table.lastUpdate = MagicMock(return_value=last_update)
    schema = MagicMock()
    schema.tables = ['tab_daily', 'tab_yearly']
    schema.table = MagicMock(return_value=table)
    return schema


class HistorySetup(unittest.TestCase):

    def setUp(self):
        self.schema = MagicMock()
        self.stock = MagicMock()
        self.stock._id = 1

    def test_initialNones(self):
        hist = History(self.schema, self.stock)
        self.assertIsNone(hist._table)
        self.assertIsNone(hist.last_update)
        self.assertIsNone(hist._type)
        self.assertIsNone(hist.days_missing)
        self.assertIsNone(hist.years_missing)
        self.assertIsNone(hist.name)

    def test_dateIsSet(self):
        hist = History(self.schema, self.stock)
        self.assertEqual(hist.today, dt.date.today())

    def test_errorIfStockUnset(self):
        self.stock._id = None
        with self.assertRaises(AttributeError):
            hist = History(self.schema, self.stock)


class TableHistories(unittest.TestCase):

    def setUp(self):
        self.stock = MagicMock()
        self.stock._id = 1

    def test_mockingSchemaWorks(self):
        schema = mockSchema(2017, 'integer')
        hist = History(schema, self.stock)
        hist.table('tab_daily')
        self.assertEqual(hist.last_update, 2017)
        self.assertEqual(hist.name, 'tab_daily')

    def test_tableNotInSchema(self):
        schema = mockSchema(2017, 'integer')
        hist = History(schema, self.stock)
        with self.assertRaises(ValueError):
            hist.table('wrong_table')

    def test_unclearColumnType(self):
        schema = mockSchema(2017, 'unclear_type')
        hist = History(schema, self.stock)
        with self.assertRaises(AttributeError):
            hist.table('tab_daily')

    def test_switchingTablesWorks(self):
        # TODO check all public attributes
        schema = mockSchema(2017, 'integer')
        hist = History(schema, self.stock)
        hist.table('tab_daily')
        self.assertEqual(hist.name, 'tab_daily')
        hist.table('tab_yearly')
        self.assertEqual(hist.name, 'tab_yearly')

    def test_recognizeDateType(self):
        schema = mockSchema(dt.date(1990, 1, 1), 'date')
        hist = History(schema, self.stock)
        hist.table('tab_daily')
        self.assertEqual(hist._type, 'date')

    def test_recognizeYearType(self):
        schema = mockSchema(2017, 'integer')
        hist = History(schema, self.stock)
        hist.table('tab_daily')
        self.assertEqual(hist._type, 'year')

    # # Bsp hist
    # schema.table().lastUpdate = dt.date(2018, 5, 16)
    # history._table.update_rate = 'daily'  # date type
    # dt.timedelta(67)
    #
    # # Bsp fund
    # schema.table().lastUpdate = 2017
    # history._table.update_rate = 'yearly'  # date type
    # dt.timedelta(429)
