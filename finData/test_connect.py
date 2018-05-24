# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
from unittest.mock import patch
from unittest.mock import MagicMock
import finData.connect
import psycopg2 as pg
import unittest
import sys
import io


connList = ['findata', 'testdb', 'postgres', '127.0.0.1', 5432]

oldStock = {'name': 'o', 'isin': 'o', 'wkn': 'o', 'typ': 'o', 'currency': 'o',
            'boerse_name': 'o', 'avan_ticker': 'o'}

oldStockSQL = ("""INSERT INTO testdb.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) """
               """VALUES ('oldname','oldisin','oldwkn','oldtyp','oldcurrency','oldname-typ','TEST')""")

queryRes = [(1,), (2,), (3,), (4,), (5,), (6,), (7,), ]


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


class InsertNewStock(unittest.TestCase):

    def setUp(self):
        self.newStock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=[])

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_InsertedStockIsPrinted(self):
            capture = io.StringIO()
            with self.assertRaises(IndexError):
                sys.stdout = capture
                self.x.insertStock(*self.newStock)
            sys.stdout = sys.__stdout__
            self.assertEqual(capture.getvalue(), 'n (isin: n) inserted\n')

    def test_correctCursorCalls(self):
            with self.assertRaises(IndexError):
                self.x.insertStock(*self.newStock)
            cur = self.x.conn.__enter__().cursor().__enter__()
            self.assertEqual(cur.execute.call_count, 3)
            self.assertEqual(cur.fetchall.call_count, 2)


class InsertExistingStock(unittest.TestCase):

    def setUp(self):
        self.stock = ['n'] * 7
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value=[(1,)])

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_InsertedStockIsPrinted(self):
            capture = io.StringIO()
            sys.stdout = capture
            self.x.insertStock(*self.stock)
            sys.stdout = sys.__stdout__
            self.assertEqual(capture.getvalue(), 'n (isin: n) not inserted, it already exists\n')

    def test_stockIdIsCorrect(self):
            self.x.insertStock(*self.stock)
            self.assertEqual(self.x.stock_id, 1)

    def test_correctCursorCalls(self):
            self.x.insertStock(*self.stock)
            cur = self.x.conn.__enter__().cursor().__enter__()
            self.assertEqual(cur.execute.call_count, 1)
            self.assertEqual(cur.fetchall.call_count, 1)

#
#
# class WithoutConnection(unittest.TestCase):
#
#     def setUp(self):
#         with patch('finData.connect.Connector._connect') as mockCon:
#             mockCon.return_value = "x"
#             self.x = finData.connect.Connector(*connList)
#
#     def test_StockColnamesExtractedCorrectly(self):
#         prim_cols = ("'{name}','{isin}','{wkn}','{typ}','{currency}',"
#                      "'{boerse_name}','{avan_ticker}'")
#         exp = 'name,isin,wkn,typ,currency,boerse_name,avan_ticker'
#         res = self.x._extractColNames(prim_cols)
#         self.assertEqual(exp, res)
#
#     def test_properInsertStatements(self):
#         colNames = 'col1, col2'
#         colVals = ["'x',1", "'y', 2"]
#         exp = """INSERT INTO schem.tab (col1, col2) VALUES ('x',1),('y', 2)"""
#         res = self.x._insertStatement('schem', 'tab', colNames, colVals)
#         self.assertEqual(res, exp)
#
#
# class InsertNewStockRow(unittest.TestCase):
#
#     def setUp(self):
#         def enforceUnique(sql):
#             if sql == oldStockSQL:
#                 raise pg.IntegrityError()
#         mockDB = MagicMock()
#         mockDB.execute = MagicMock(side_effect=enforceUnique)
#         mockDB.fetchone = MagicMock(return_value=[1])
#
#         with patch('finData.connect.Connector._connect') as connect:
#             connect.return_value = mockDBconnect(mockDB)
#             self.x = finData.connect.Connector(*connList)
#
#     def test_mockDBworks(self):
#             res = self.x._insertNewStockRow(newStock, 'testdb', self.x.conn)
#             self.assertEqual(res, 1)
#
#     def test_exexuteWasProperlyCalled(self):
#             res = self.x._insertNewStockRow(newStock, 'testdb', self.x.conn)
#             ex = self.x.conn.cursor().__enter__().execute
#             ex.assert_any_call("""INSERT INTO testdb.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) VALUES ('testname','testisin','testwkn','testtyp','testcurrency','testname-typ','TEST')""")
#             ex.assert_any_call("""SELECT id FROM testdb.stock WHERE isin = 'testisin'""")
#
#     def test_uniqueConstraintEnforced(self):
#             capture = io.StringIO()
#             sys.stdout = capture
#             res = self.x._insertNewStockRow(oldStock, 'testdb', self.x.conn)
#             sys.stdout = sys.__stdout__
#             self.assertEqual(res, 1)
#             self.assertEqual(capture.getvalue(), 'oldname (isin: oldisin) not inserted, it already exists\n')


            #print(self.stock_id)

    # def test_exexuteWasProperlyCalled(self):
    #         res = self.x.insertStock(*newStock)
    #         ex = self.x.conn.cursor().__enter__().execute
            #ex.assert_any_call("""INSERT INTO testdb.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) VALUES ('testname','testisin','testwkn','testtyp','testcurrency','testname-typ','TEST')""")
            #ex.assert_any_call("""SELECT id FROM testdb.stock WHERE isin = 'testisin'""")
    #
    # def test_uniqueConstraintEnforced(self):

if __name__ == '__main__':
    unittest.main()
