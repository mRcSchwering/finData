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
        schema = mockSchema(2018, 'integer')
        hist = History(schema, self.stock)
        hist.today = dt.date(2018, 1, 10)
        hist.table('tab_daily')
        self.assertEqual(hist.name, 'tab_daily')
        self.assertEqual(hist.years_missing, 0)
        self.assertEqual(hist.days_missing, dt.timedelta(9))
        hist.today = dt.date(2018, 1, 9)
        hist.table('tab_yearly')
        self.assertEqual(hist.name, 'tab_yearly')
        self.assertEqual(hist.years_missing, 0)
        self.assertEqual(hist.days_missing, dt.timedelta(8))

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

    def test_missingYearsWithDate(self):
        schema = mockSchema(dt.date(2017, 1, 1), 'date')
        hist = History(schema, self.stock)
        hist.today = dt.date(2017, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.years_missing, 0)
        hist.today = dt.date(2018, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.years_missing, 1)

    def test_missingYearsWithYear(self):
        schema = mockSchema(2017, 'integer')
        hist = History(schema, self.stock)
        hist.today = dt.date(2017, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.years_missing, 0)
        hist.today = dt.date(2018, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.years_missing, 1)

    def test_missingDaysWithDate(self):
        schema = mockSchema(dt.date(2018, 1, 1), 'date')
        hist = History(schema, self.stock)
        hist.today = dt.date(2018, 1, 10)
        hist.table('tab_daily')
        self.assertEqual(hist.days_missing, dt.timedelta(9))
        hist.today = dt.date(2018, 1, 20)
        hist.table('tab_daily')
        self.assertEqual(hist.days_missing, dt.timedelta(19))

    def test_missingDaysWithYear(self):
        schema = mockSchema(2018, 'integer')
        hist = History(schema, self.stock)
        hist.today = dt.date(2018, 1, 30)
        hist.table('tab_daily')
        self.assertEqual(hist.days_missing, dt.timedelta(29))
        hist.today = dt.date(2018, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.days_missing, dt.timedelta(0))

    def test_noEntriesInTableYet(self):
        schema = mockSchema(None, 'integer')
        hist = History(schema, self.stock)
        hist.today = dt.date(2018, 1, 1)
        hist.table('tab_daily')
        self.assertEqual(hist.years_missing, 20)
        self.assertEqual(hist.days_missing, dt.timedelta(7305))


class isNewSetup(unittest.TestCase):

    def setUp(self):
        stock = MagicMock()
        stock._id = 1
        schema = MagicMock()
        self.hist = History(schema, stock)

    def test_noTableSet(self):
        with self.assertRaises(AttributeError):
            self.hist.isNew(dt.date(2018, 1, 10))


class isNewForYears(unittest.TestCase):

    def setUp(self):
        stock = MagicMock()
        stock._id = 1
        schema = mockSchema(2018, 'integer')
        self.hist = History(schema, stock)

    def test_neitherDateNorIntGiven(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        with self.assertRaises(ValueError):
            self.hist.isNew('asd')

    def test_newDayButSameYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(dt.date(2018, 1, 10))
        self.assertFalse(res)

    def test_newDayAndYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(dt.date(2019, 1, 10))
        self.assertTrue(res)

    def test_sameYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(2018)
        self.assertFalse(res)

    def test_newYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(2019)
        self.assertTrue(res)


class isNewForDays(unittest.TestCase):

    def setUp(self):
        stock = MagicMock()
        stock._id = 1
        schema = mockSchema(dt.date(2018, 1, 1), 'date')
        self.hist = History(schema, stock)

    def test_giveYearToDaily(self):
        self.hist.table('tab_daily')
        self.hist.update_rate = 'daily'
        with self.assertRaises(ValueError):
            self.hist.isNew(2018)

    def test_newDayButSameYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(dt.date(2018, 1, 10))
        self.assertFalse(res)

    def test_newDayAndYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(dt.date(2019, 1, 10))
        self.assertTrue(res)

    def test_currentYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(2018)
        self.assertFalse(res)

    def test_newYearForYearlyUpdates(self):
        self.hist.table('tab_yearly')
        self.hist.update_rate = 'yearly'
        res = self.hist.isNew(2019)
        self.assertTrue(res)

    def test_newDayForDailyUpdates(self):
        self.hist.table('tab_daily')
        self.hist.update_rate = 'daily'
        res = self.hist.isNew(dt.date(2018, 1, 10))
        self.assertTrue(res)

    def test_sameDayForDailyUpdates(self):
        self.hist.table('tab_daily')
        self.hist.update_rate = 'daily'
        res = self.hist.isNew(dt.date(2018, 1, 1))
        self.assertFalse(res)
