# This Python file uses the following encoding: utf-8
from finData.stock import Stock
from finData.testing_utils import *


# mocking schema
db = MagicMock()
table = MagicMock()
table.insert_statement = (
    """INSERT INTO %(schema)s.stock """
    """(name,isin,wkn,typ,currency,boerse_name,avan_ticker) """
    """VALUES (%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)"""
)
schema = MagicMock()
schema.name = 'schema_name'
schema.table = MagicMock(return_value=table)


class StockSetUp(unittest.TestCase):

    def setUp(self):
        db.query = MagicMock(return_value='hi')
        self.S = Stock(db, schema)

    def test_attributes(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.wkn)
        self.assertIsNone(self.S.typ)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)

    def test_dbMockingWorks(self):
        self.assertEqual(self.S.db.query(), 'hi')

    def test_schemaMockingWorks(self):
        self.assertEqual(self.S.schema.name, 'schema_name')


class ExistsReturningNone(unittest.TestCase):

    def setUp(self):
        db.query = MagicMock(return_value=None)
        self.S = Stock(db, schema)
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertFalse(self.res)

    def test_correctQuery(self):
        calls = self.S.db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %{schema}s.stock WHERE isin = %{isin}s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.wkn)
        self.assertIsNone(self.S.typ)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)


class ExistsReturningEmpty(unittest.TestCase):

    def setUp(self):
        db.query = MagicMock(return_value=[])
        self.S = Stock(db, schema)
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertFalse(self.res)

    def test_correctQuery(self):
        calls = self.S.db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %{schema}s.stock WHERE isin = %{isin}s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.wkn)
        self.assertIsNone(self.S.typ)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)


class ExistsReturningStockInfo(unittest.TestCase):

    def setUp(self):
        stock_info = (1, 'Name', 'ISIN', 'WKN', 'ST', 'EUR', 'asd', 'ADS')
        db.query = MagicMock(return_value=stock_info)
        self.S = Stock(db, schema)
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertTrue(self.res)

    def test_correctQuery(self):
        calls = self.S.db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %{schema}s.stock WHERE isin = %{isin}s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreStillNone(self):
        self.assertEqual(self.S._id, 1)
        self.assertEqual(self.S.name, 'Name')
        self.assertEqual(self.S.isin, 'ISIN')
        self.assertEqual(self.S.wkn, 'WKN')
        self.assertEqual(self.S.typ, 'ST')
        self.assertEqual(self.S.currency, 'EUR')
        self.assertEqual(self.S.boerse_name, 'asd')
        self.assertEqual(self.S.avan_ticker, 'ADS')


class InsertAlreadyExistingStock(unittest.TestCase):

    def setUp(self):
        # exists returns stock info -> stock already existed
        existing = (1, 'Name', 'ISIN', 'WKN', 'ST', 'EUR', 'asd', 'ADS')
        db.query = MagicMock(return_value=existing)
        # use different info to insert -> can distinguish in tests
        insert = ['Nome', 'isin', 'wkn', 'st', 'USD', 'dsa', 'STV']
        self.S = Stock(db, schema)
        with catchStdout() as cap:
            self.res = self.S.insert(*insert)
            self.capture = cap.getvalue()

    def test_insertReturnValue(self):
        self.assertFalse(self.res)

    def test_infoPrinted(self):
        msg = 'Nome (isin: wkn) not inserted, it already exists\n'
        self.assertEqual(self.capture, msg)

    def test_existingStockInfoAssigned(self):
        self.assertEqual(self.S._id, 1)
        self.assertEqual(self.S.name, 'Name')
        self.assertEqual(self.S.isin, 'ISIN')
        self.assertEqual(self.S.wkn, 'WKN')
        self.assertEqual(self.S.typ, 'ST')
        self.assertEqual(self.S.currency, 'EUR')
        self.assertEqual(self.S.boerse_name, 'asd')
        self.assertEqual(self.S.avan_ticker, 'ADS')


class InsertAlreadyExistingStock(unittest.TestCase):

    def setUp(self):
        # returns empty -> stock did not already exist
        db.query = MagicMock(return_value=[])
        insert = ['Nome', 'isin', 'wkn', 'st', 'USD', 'dsa', 'STV']
        self.S = Stock(db, schema)
        with catchStdout() as cap:
            self.res = self.S.insert(*insert)
            self.capture = cap.getvalue()

    def test_insertReturnValue(self):
        self.assertTrue(self.res)

    def test_nothingPrinted(self):
        self.assertEqual(self.capture, '')

    def test_noStockInfoAssigned(self):
        # since exists will return False twice, no info will be assigned
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.wkn)
        self.assertIsNone(self.S.typ)
        self.assertIsNone(self.S.currency,)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)

    def test_insertNewStockCall(self):
        calls = self.S.db.query.mock_calls
        self.assertEqual(len(calls), 3)
        exp = ('INSERT INTO %(schema)s.stock '
               '(name,isin,wkn,typ,currency,boerse_name,avan_ticker) VALUES '
               '(%(name)s,%(isin)s,%(wkn)s,%(typ)s,%(currency)s,%(boerse_name)s,%(avan_ticker)s)')
        self.assertEqual(calls[1][1][0], exp)
