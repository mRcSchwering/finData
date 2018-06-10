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

# number of yearly, daily tables and tables with a date but yearly update
nYearTables = 6
nDateTables = 1


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


class ConnectorSetUp(unittest.TestCase):

    def setUp(self):
        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = None
            self.x = finData.connect.Connector(*connList)

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

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_fetchIsWorking(self):
        res = self.x._customSQL('a statement', fetch=False)
        self.assertIsNone(res)
        res = self.x._customSQL('a statement', fetch=True)
        self.assertEqual(res, 'fetched')

    def test_correctCursorCalls(self):
        self.x._customSQL('a statement', fetch=True)
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, 1)
        self.assertEqual(cur.fetchall.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'a statement')


class InsertRow(unittest.TestCase):

    def setUp(self):
        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = MagicMock()
            self.x = finData.connect.Connector(*connList)

    def test_correctCursorCalls(self):
        row = pd.DataFrame({'A': [1], 'B': [2]})
        self.x._insertRow(row, 'stockId', 'person')
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        st = ('INSERT INTO %(schema_name)s.%(table_name)s '
              '(stock_id,year,personal,aufwand,umsatz,gewinn) '
              'VALUES (%(stock_id)s,%(year)s,%(personal)s,%(aufwand)s,%(umsatz)s,%(gewinn)s)')
        self.assertEqual(calls[0], st)


class UpdateYearTables(unittest.TestCase):

    def setUp(self):
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(2016,))
        # maximum year for each table is returned

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_correctCursorCalls(self):
        self.x._updateYearTables(MagicMock(), 1)
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, nYearTables)
        self.assertEqual(cur.fetchone.call_count, nYearTables)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'SELECT MAX(year) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s')

    def test_scraperCouldntGetTable(self):
        scraper = MagicMock()
        scraper.get = MagicMock(side_effect=ValueError)
        expected = ("""Scaper didn't return Table guv... continuing without it\n"""
                    """Scaper didn't return Table bilanz... continuing without it\n"""
                    """Scaper didn't return Table kennza... continuing without it\n"""
                    """Scaper didn't return Table rentab... continuing without it\n"""
                    """Scaper didn't return Table person... continuing without it\n"""
                    """Scaper didn't return Table marktk... continuing without it\n""")
        capture = io.StringIO()
        sys.stdout = capture
        self.x._updateYearTables(scraper, 1)
        sys.stdout = sys.__stdout__
        self.assertEqual(capture.getvalue(), expected)


class UpdateYearTablesUnnecessary(unittest.TestCase):

    def setUp(self):
        thisYear = dt.datetime.now().year
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(thisYear,))
        # this year, so no entry necessary

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_correctCursorCalls(self):
        self.x._updateYearTables(MagicMock(), 1)
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, nYearTables)
        self.assertEqual(cur.fetchone.call_count, nYearTables)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'SELECT MAX(year) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s')


class InsertNewStock(unittest.TestCase):

    def setUp(self):
        self.newStock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=[])
        # 1st fetch would return [] (=stock didnt exist before)

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

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
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, 3)
        self.assertEqual(cur.fetchall.call_count, 2)
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
        self.stock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=[(1,)])
        # 1st fetch would return sth (=stock was already entered before)

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

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
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, 1)
        self.assertEqual(cur.fetchall.call_count, 1)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0],
                         'SELECT id FROM %(schema)s.stock WHERE isin = %(isin)s')


class UpdateDateTables(unittest.TestCase):

    def setUp(self):
        maximumReturnDate = dt.datetime(2016, 1, 1).date()
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(maximumReturnDate,))

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_correctCursorCalls(self):
        self.x._updateDateTables(MagicMock(), 1)
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, nDateTables)
        self.assertEqual(cur.fetchone.call_count, nDateTables)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'SELECT MAX(datum) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s')

    def test_scraperCouldntGetTable(self):
        scraper = MagicMock()
        scraper.get = MagicMock(side_effect=ValueError)
        expected = """Scaper didn't return Table divid... continuing without it\n"""
        capture = io.StringIO()
        sys.stdout = capture
        self.x._updateDateTables(scraper, 1)
        sys.stdout = sys.__stdout__
        self.assertEqual(capture.getvalue(), expected)


class UpdateDateTablesUnnecessary(unittest.TestCase):

    def setUp(self):
        thisYear = dt.datetime.now().date()
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=(thisYear,))
        # this year, so no entry necessary

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_correctCursorCalls(self):
        self.x._updateDateTables(MagicMock(), 1)
        cur = self.x.conn.__enter__().cursor().__enter__()
        self.assertEqual(cur.execute.call_count, nDateTables)
        self.assertEqual(cur.fetchone.call_count, nDateTables)
        calls = [str(c[1][0]) for c in cur.execute.mock_calls]
        self.assertEqual(calls[0], 'SELECT MAX(datum) FROM %(schema)s.%(tab)s WHERE stock_id = %(id)s')


# class UpdateData(unittest.TestCase):
#
#     def setUp(self):
#         mockDB = MagicMock()
#         existing = [(1, 'nameA', 'isinA'), (2, 'nameB', 'isinB')]
#         mockDB.fetchall = MagicMock(return_value=existing)
#         # returns list of existing stock by id, name, isin
#
#         with patch('finData.connect.Connector._connect') as connect:
#             connect.return_value = mockDBconnect(mockDB)
#             self.x = finData.connect.Connector(*connList)
#
#     def test_correctCursorCalls(self):
#         with patch('finData.connect.Connector._updateSingleStock') as updateSingleStock:
#             updateSingleStock.return_value = None
#             self.x.updateData()
#         cur = self.x.conn.__enter__().cursor().__enter__()
#         self.assertEqual(cur.execute.call_count, 1)
#         self.assertEqual(cur.fetchall.call_count, 1)
#         calls = [str(c[1][0]) for c in cur.execute.mock_calls]
#         self.assertEqual(calls[0], 'SELECT id, name, isin FROM %(schema)s.stock')
#
#     def test_progressIsPrinted(self):
#         capture = io.StringIO()
#         sys.stdout = capture
#         with patch('finData.connect.Connector._updateSingleStock') as updateSingleStock:
#             updateSingleStock.return_value = None
#             self.x.updateData()
#         sys.stdout = sys.__stdout__
#         self.assertEqual(('[1/2] Updating nameA (isinA)...done\n'
#                           '[2/2] Updating nameB (isinB)...done\n'),
#                          capture.getvalue())
#


if __name__ == '__main__':
    unittest.main()
