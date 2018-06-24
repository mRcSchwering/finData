# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
from unittest.mock import patch
from unittest.mock import MagicMock
import finData.connect
import psycopg2 as pg
import pandas as pd
import datetime as dt
import unittest
import sys
import io

# pseudo connection info (will be mocked)
connList = ['findata', 'testdb', 'postgres', '127.0.0.1', 5432]

# yearly, daily tables and tables with a date but yearly update
yearTables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk']
dayTables = ['hist']
dateTables = ['divid']

# the query used to get the last entered time point
lastEnteredTimepointQuery = 'SELECT MAX(%(col)s) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s'

# time period that is proposedly missing
missingDays = 20
missingYears = 5


# message if scraper couldnt get a table
def couldntScrapeString(tables):
    msg = """\nScaper didn't return Table {tab}... continuing without it\n"""
    strs = [msg.format(tab=tab) for tab in tables]
    return ''.join(strs)


# mocking DB connection
def mockDBconnect(mockDB):
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=mockDB)
    cur.__exit__ = MagicMock(return_value=False)
    con = MagicMock()
    con.cursor = MagicMock(return_value=cur)
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=con)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


# patching DB connection
def patchConnect(mocked):
    with patch('finData.connect.Connector._connect') as connect:
        connect.return_value = mocked
        return finData.connect.Connector(*connList)


# extracting cursor from mocked connection
def getCursor(x):
    return x.conn.__enter__().cursor().__enter__()


# helper for silencing
class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


class ConnectorSetUp(unittest.TestCase):

    def setUp(self):
        self.x = patchConnect(None)

    def test_insertStatementsProperlyPrepared(self):
        sts = self.x.insert_statements
        self.assertEqual(list(sts.keys()).sort(),
                         ['person', 'marktk'].sort())
        person = ('INSERT INTO %(schema_name)s.%(table_name)s '
                  '(stock_id,year,personal,aufwand,umsatz,gewinn) '
                  'VALUES (%(stock_id)s,%(year)s,%(personal)s,%(aufwand)s,%(umsatz)s,%(gewinn)s)')
        self.assertEqual(sts['person'], person)


class CustomSQL(unittest.TestCase):

    def setUp(self):
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value='fetched')
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_fetchIsWorking(self):
        res = self.x._customSQL('a statement', fetch=False)
        self.assertIsNone(res)
        res = self.x._customSQL('a statement', fetch=True)
        self.assertEqual(res, 'fetched')

    def test_correctCursorCalls(self):
        self.x._customSQL('a statement', fetch=True)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, 1)
        self.assertEqual(cur.fetchall.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'a statement')


class InsertRow(unittest.TestCase):

    def setUp(self):
        self.x = patchConnect(MagicMock())

    def test_correctCursorCalls(self):
        row = pd.DataFrame({'A': [1], 'B': [2]})
        self.x._insertRow(row, 'stockId', 'person')
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        st = ('INSERT INTO %(schema_name)s.%(table_name)s '
              '(stock_id,year,personal,aufwand,umsatz,gewinn) '
              'VALUES (%(stock_id)s,%(year)s,%(personal)s,%(aufwand)s,%(umsatz)s,%(gewinn)s)')
        self.assertEqual(calls[0], st)


class InsertNewStock(unittest.TestCase):

    def setUp(self):
        # 1st fetch would return () (=stock didnt exist before)
        self.newStock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=())
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_InsertedStockIsPrinted(self):
        capture = io.StringIO()
        sys.stdout = capture
        with self.assertRaises(IndexError):
            self.x.insertStock(*self.newStock)
        sys.stdout = sys.__stdout__
        self.assertEqual(capture.getvalue(), 'n (isin: n) inserted\n')

    def test_correctCursorCalls(self):
        with self.assertRaises(IndexError):
            self.x.insertStock(*self.newStock)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, 3)
        self.assertEqual(cur.fetchone.call_count, 2)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0],
                         'SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s')
        self.assertEqual(calls[1],
                         ('INSERT INTO %(schema)s.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) '
                          'VALUES (%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)'))
        self.assertEqual(calls[2],
                         'SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s')


class InsertExistingStock(unittest.TestCase):

    def setUp(self):
        # 1st fetch would return id (=stock was already entered before)
        self.stock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(1,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_NotInsertedStockIsPrinted(self):
        capture = io.StringIO()
        sys.stdout = capture
        self.x.insertStock(*self.stock)
        sys.stdout = sys.__stdout__
        self.assertEqual(capture.getvalue(),
                         'n (isin: n) not inserted, it already exists\n')

    def test_stockIdIsCorrect(self):
        self.x.insertStock(*self.stock)
        self.assertEqual(self.x.stock_id, 1)

    def test_correctCursorCalls(self):
        self.x.insertStock(*self.stock)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, 1)
        self.assertEqual(cur.fetchone.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0],
                         'SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s')


class UpdateYearTables(unittest.TestCase):

    def setUp(self):
        ood = dt.date.today().year - missingYears
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(ood,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as capture:
            self.x.updateYearTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(yearTables))
        self.assertEqual(cur.fetchone.call_count, len(yearTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)

    def test_correctStockCalls(self):
        scraper = MagicMock()
        scraper.get = MagicMock(return_value=MagicMock())
        with catchStdout() as capture:
            self.x.updateYearTables(scraper, 1)
        self.assertEqual(scraper.mock_calls[0][0], 'getFundamentalTables')
        for call in scraper.get.mock_calls:
            self.assertIn(call[1][0], yearTables)

    def test_scraperCouldntGetTable(self):
        scraper = MagicMock()
        scraper.get = MagicMock(side_effect=ValueError)
        expected = couldntScrapeString(yearTables)
        with catchStdout() as cap:
            self.x.updateYearTables(scraper, 1)
            capture = cap
        self.assertTrue(expected in capture.getvalue())

    def test_inserts(self):
        self.x._insertRow = MagicMock()
        with catchStdout() as capture:
            self.x.updateYearTables(MagicMock(), 1)
        obj = self.x._insertRow
        self.assertEqual(obj.call_count, missingYears * len(yearTables))
        for call in obj.mock_calls:
            self.assertEqual(call[1][1], 1)
            self.assertIn(call[1][2], yearTables)


class UpdateYearTablesUnnecessary(unittest.TestCase):

    def setUp(self):
        thisYear = dt.date.today().year
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(thisYear,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as cap:
            self.x.updateYearTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(yearTables))
        self.assertEqual(cur.fetchone.call_count, len(yearTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)


class UpdateDateTables(unittest.TestCase):

    def setUp(self):
        ood = dt.date.today() - dt.timedelta(days=missingYears * 365.24)
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(ood,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as cap:
            self.x.updateDateTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(dateTables))
        self.assertEqual(cur.fetchone.call_count, len(dateTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)

    def test_correctStockCalls(self):
        scraper = MagicMock()
        scraper.get = MagicMock(return_value=MagicMock())
        with catchStdout() as cap:
            self.x.updateDateTables(scraper, 1)
        self.assertEqual(scraper.mock_calls[0][0], 'getDividendTable')
        for call in scraper.get.mock_calls:
            self.assertIn(call[1][0], dateTables)

    def test_scraperCouldntGetTable(self):
        scraper = MagicMock()
        scraper.get = MagicMock(side_effect=ValueError)
        expected = couldntScrapeString(dateTables)
        with catchStdout() as cap:
            self.x.updateDateTables(scraper, 1)
            capture = cap
        self.assertTrue(expected in capture.getvalue())

    def test_inserts(self):
        self.x._insertRow = MagicMock()
        with catchStdout() as cap:
            self.x.updateDateTables(MagicMock(), 1)
        obj = self.x._insertRow
        self.assertEqual(obj.call_count, missingYears * len(dateTables))
        for call in obj.mock_calls:
            self.assertEqual(call[1][1], 1)
            self.assertIn(call[1][2], dateTables)


class UpdateDateTablesUnnecessary(unittest.TestCase):

    def setUp(self):
        today = dt.date.today()
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(today,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as cap:
            self.x.updateDateTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(dateTables))
        self.assertEqual(cur.fetchone.call_count, len(dateTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)


class UpdateDayTables(unittest.TestCase):

    def setUp(self):
        ood = dt.date.today() - dt.timedelta(days=missingDays + 1)
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(ood,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as cap:
            self.x.updateDayTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(dayTables))
        self.assertEqual(cur.fetchone.call_count, len(dayTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)

    def test_correctStockCalls(self):
        scraper = MagicMock()
        scraper.get = MagicMock(return_value=MagicMock())
        with catchStdout() as cap:
            self.x.updateDayTables(scraper, 1)
        self.assertEqual(scraper.mock_calls[0][0], 'getHistoricPrices')
        for call in scraper.get.mock_calls:
            self.assertIn(call[1][0], dayTables)

    def test_scraperCouldntGetTable(self):
        scraper = MagicMock()
        scraper.get = MagicMock(side_effect=ValueError)
        expected = couldntScrapeString(dayTables)
        with catchStdout() as cap:
            self.x.updateDayTables(scraper, 1)
            capture = cap
        self.assertTrue(expected in capture.getvalue())

    def test_inserts(self):
        self.x._insertRow = MagicMock()
        with catchStdout() as cap:
            self.x.updateDayTables(MagicMock(), 1)
        obj = self.x._insertRow
        self.assertEqual(obj.call_count, missingDays * len(dayTables))
        for call in obj.mock_calls:
            self.assertEqual(call[1][1], 1)
            self.assertIn(call[1][2], dayTables)


class UpdateDayTablesUnnecessary(unittest.TestCase):

    def setUp(self):
        # today, so no entry necessary
        today = dt.date.today()
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(today,))
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCursorCalls(self):
        with catchStdout() as cap:
            self.x.updateDateTables(MagicMock(), 1)
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, len(dayTables))
        self.assertEqual(cur.fetchone.call_count, len(dayTables))
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], lastEnteredTimepointQuery)


class UpdateData(unittest.TestCase):

    def setUp(self):
        self.stocks = [(1, 'a', 'A'), (1, 'b', 'B')]
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=self.stocks)
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCalls(self):
        self.x.updateSingleStock = MagicMock()
        with catchStdout() as cap:
            self.x.updateData()
        self.assertEqual(self.x.updateSingleStock.call_count, len(self.stocks))


class UpdateSingleStock(unittest.TestCase):

    def setUp(self):
        self.stock = tuple(['s'] * 7)
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=self.stock)
        self.x = patchConnect(mockDBconnect(mockDB))

    def test_correctCalls(self):
        self.x.updateYearTables = MagicMock()
        self.x.updateDateTables = MagicMock()
        self.x.updateDayTables = MagicMock()
        with patch('finData.scrape.Scraper.__init__') as scraper:
            scraper.return_value = None
            capture = io.StringIO()
            sys.stdout = capture
            self.x.updateSingleStock(1)
            sys.stdout = sys.__stdout__
        cur = getCursor(self.x)
        self.assertEqual(cur.execute.call_count, 1)
        self.assertEqual(cur.fetchone.call_count, 1)
        self.assertEqual(scraper.call_count, 1)
        self.assertEqual(self.x.updateYearTables.call_count, 1)
        self.assertEqual(self.x.updateDateTables.call_count, 1)
        self.assertEqual(self.x.updateDayTables.call_count, 1)


if __name__ == '__main__':
    unittest.main()
