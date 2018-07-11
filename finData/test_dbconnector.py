# This Python file uses the following encoding: utf-8
from finData.dbconnector import DBConnector
from unittest.mock import patch
from unittest.mock import MagicMock
import unittest

# pseudo connection info (will be mocked)
conn_list = ['findata', 'postgres', '127.0.0.1', 5432]


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
    with patch('finData.dbconnector.DBConnector._connect') as connect:
        connect.return_value = mocked
        return DBConnector(*conn_list)


# extracting cursor from mocked connection
def getCursor(x):
    return x.conn.__enter__().cursor().__enter__()


class DBConnectorSetUp(unittest.TestCase):

    def setUp(self):
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value='hi')
        self.C = patchConnect(mockDBconnect(mockDB))

    def test_attributes(self):
        self.assertEqual(self.C.name, 'findata')
        self.assertEqual(self.C.user, 'postgres')
        self.assertEqual(self.C.password, '')
        self.assertEqual(self.C.host, '127.0.0.1')
        self.assertEqual(self.C.port, 5432)

    def test_mockingWorks(self):
        with self.C.conn as conn:
            with conn.cursor() as cur:
                res = cur.fetchall()
        self.assertEqual(res, 'hi')


class Queries(unittest.TestCase):

    def setUp(self):
        mockDB = MagicMock()
        mockDB.fetchall = MagicMock(return_value='all')
        mockDB.fetchone = MagicMock(return_value='one')
        self.C = patchConnect(mockDBconnect(mockDB))

    def test_fetchNone(self):
        self.C.query('statement', {'arg': 'value'})
        calls = getCursor(self.C).method_calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], 'execute')
        self.assertEqual(calls[0][1], ('statement', {'arg': 'value'}))

    def test_fetchAll(self):
        res = self.C.query('statement', 'args', 'all')
        calls = getCursor(self.C).method_calls
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], 'execute')
        self.assertEqual(calls[0][1], ('statement', 'args'))
        self.assertEqual(calls[1][0], 'fetchall')
        self.assertEqual(res, 'all')

    def test_fetchOne(self):
        res = self.C.query('statement', 'args', 'one')
        calls = getCursor(self.C).method_calls
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], 'execute')
        self.assertEqual(calls[0][1], ('statement', 'args'))
        self.assertEqual(calls[1][0], 'fetchone')
        self.assertEqual(res, 'one')
