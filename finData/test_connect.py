# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
from unittest.mock import patch
from unittest.mock import MagicMock
import finData.connect
import psycopg2 as pg
import unittest


connList = ['findata', 'testdb', 'postgres', '127.0.0.1', 5432]

newStock = {
    'name': 'testname',
    'isin': 'testisin',
    'wkn': 'testwkn',
    'typ': 'testtyp',
    'currency': 'testcurrency',
    'boerse_name': 'testname-typ',
    'avan_ticker': 'TEST'
}

queryRes = [(1,), (2,), (3,), (4,), (5,), (6,), (7,), ]


def mockDBconnect(mockDB):
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=mockDB)
    cur.__exit__ = MagicMock(return_value=False)
    con = MagicMock()
    con.cursor = MagicMock(return_value=cur)
    return con


class WithoutConnection(unittest.TestCase):

    def setUp(self):
        with patch('finData.connect.Connector._connect') as mockCon:
            mockCon.return_value = "x"
            self.x = finData.connect.Connector(*connList)

    def test_properInsertStatements(self):
        colNames = 'col1, col2'
        colVals = ["'x',1", "'y', 2"]
        exp = """INSERT INTO schem.tab (col1, col2) VALUES ('x',1),('y', 2)"""
        res = self.x._insertStatement('schem', 'tab', colNames, colVals)
        self.assertEqual(res, exp)


class InsertNewStockRow(unittest.TestCase):

    def setUp(self):
        mockDB = MagicMock()
        mockDB.fetchone = MagicMock(return_value=[1])

        with patch('finData.connect.Connector._connect') as connect:
            connect.return_value = mockDBconnect(mockDB)
            self.x = finData.connect.Connector(*connList)

    def test_mockDBworks(self):
            res = self.x._insertNewStockRow(newStock, 'testdb', self.x.conn)
            self.assertEqual(res, 1)

    def test_exexuteWasProperlyCalled(self):
            res = self.x._insertNewStockRow(newStock, 'testdb', self.x.conn)
            ex = self.x.conn.cursor().__enter__().execute
            ex.assert_any_call("""INSERT INTO testdb.stock (name,isin,wkn,typ,currency,boerse_name,avan_ticker) VALUES ('testname','testisin','testwkn','testtyp','testcurrency','testname-typ','TEST')""")
            ex.assert_any_call("""SELECT id FROM testdb.stock WHERE isin = 'testisin'""")

    def test_helpDevelopingTests(self):
            res = self.x._insertNewStockRow(newStock, 'testdb', self.x.conn)
            cur = self.x.conn.cursor().__enter__()
            print(cur.execute.call_args_list)


if __name__ == '__main__':
    unittest.main()
