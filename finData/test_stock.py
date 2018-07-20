# This Python file uses the following encoding: utf-8
from finData.stock import Stock
from finData.testing_utils import *


# mocking schema
DB = MagicMock()


# mocking schema with desired schema.table.insertRow() return value
def mockSchema(val):
    table = MagicMock()
    table.insertRow = MagicMock(return_value=val)
    schema = MagicMock()
    schema.name = 'schema_name'
    schema.table = MagicMock(return_value=table)
    return schema


class StockSetUp(unittest.TestCase):

    def setUp(self):
        DB.query = MagicMock(return_value='hi')
        self.S = Stock(DB, mockSchema(True))

    def test_attributes(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)

    def test_dbMockingWorks(self):
        self.assertEqual(self.S._db.query(), 'hi')

    def test_schemaMockingWorks(self):
        self.assertEqual(self.S._schema.name, 'schema_name')


class ExistsReturningNone(unittest.TestCase):

    def setUp(self):
        DB.query = MagicMock(return_value=None)
        self.S = Stock(DB, mockSchema(True))
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertFalse(self.res)

    def test_correctQuery(self):
        calls = self.S._db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %(schema)s.stock WHERE isin = %(isin)s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)


class ExistsReturningEmpty(unittest.TestCase):

    def setUp(self):
        DB.query = MagicMock(return_value=[])
        self.S = Stock(DB, mockSchema(True))
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertFalse(self.res)

    def test_correctQuery(self):
        calls = self.S._db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %(schema)s.stock WHERE isin = %(isin)s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)


class ExistsReturningStockInfo(unittest.TestCase):

    def setUp(self):
        stock_info = (1, 'Name', 'ISIN', 'EUR', 'asd', 'ADS')
        DB.query = MagicMock(return_value=stock_info)
        self.S = Stock(DB, mockSchema(True))
        self.res = self.S.exists('someISIN')

    def test_existsReturnValue(self):
        self.assertTrue(self.res)

    def test_correctQuery(self):
        calls = self.S._db.query.mock_calls
        self.assertEqual(len(calls), 1)
        exp_query = 'SELECT * FROM %(schema)s.stock WHERE isin = %(isin)s'
        self.assertEqual(calls[0][1][0], exp_query)
        self.assertEqual(type(calls[0][1][1]['schema']).__name__, 'AsIs')
        self.assertEqual(calls[0][1][1]['isin'], 'someISIN')
        self.assertEqual(calls[0][2], {'fetch': 'one'})

    def test_argsAreAssigned(self):
        self.assertEqual(self.S._id, 1)
        self.assertEqual(self.S.name, 'Name')
        self.assertEqual(self.S.isin, 'ISIN')
        self.assertEqual(self.S.currency, 'EUR')
        self.assertEqual(self.S.boerse_name, 'asd')
        self.assertEqual(self.S.avan_ticker, 'ADS')


class InsertAlreadyExistingStock(unittest.TestCase):

    def setUp(self):
        # exists returns stock info -> stock already existed
        existing = (1, 'Name', 'ISIN', 'EUR', 'asd', 'ADS')
        DB.query = MagicMock(return_value=existing)
        # use different info to insert -> can distinguish in tests
        insert = ['Nome', 'isin', 'USD', 'dsa', 'STV']
        self.S = Stock(DB, mockSchema(True))
        with catchStdout() as cap:
            self.res = self.S.insert(*insert)
            self.capture = cap.getvalue()

    def test_insertReturnValue(self):
        self.assertFalse(self.res)

    def test_infoPrinted(self):
        msg = 'Name (isin: ISIN) not inserted, it already exists\n'
        self.assertEqual(self.capture, msg)

    def test_existingStockInfoAssigned(self):
        self.assertEqual(self.S._id, 1)
        self.assertEqual(self.S.name, 'Name')
        self.assertEqual(self.S.isin, 'ISIN')
        self.assertEqual(self.S.currency, 'EUR')
        self.assertEqual(self.S.boerse_name, 'asd')
        self.assertEqual(self.S.avan_ticker, 'ADS')


class InsertNewStock(unittest.TestCase):

    def setUp(self):
        # returns empty -> stock did not already exist
        DB.query = MagicMock(return_value=[])
        insert = ['Nome', 'isin', 'USD', 'dsa', 'STV']
        self.S = Stock(DB, mockSchema(True))
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
        self.assertIsNone(self.S.currency,)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)

    def test_2existsCalls(self):
        calls = self.S._db.query.mock_calls
        self.assertEqual(len(calls), 2)

    def test_schemaTableCall(self):
        calls = self.S._schema.table.mock_calls
        self.assertEqual(calls[0][1][0], 'stock')

    def test_insertRowCall(self):
        table = self.S._schema.table()
        calls = table.insertRow.mock_calls
        self.assertEqual(len(calls), 1)
        exp = ['isin', 'avan_ticker', 'boerse_name', 'name', 'currency']
        keys = [k for k in calls[0][1][0]]
        self.assertEqual(set(keys), set(exp))


class InsertNewStockWentWrong(unittest.TestCase):

    def setUp(self):
        # returns empty -> stock did not already exist
        DB.query = MagicMock(return_value=[])
        self.insert = ['Nome', 'isin', 'USD', 'dsa', 'STV']
        self.S = Stock(DB, mockSchema(False))

    def test_caughtError(self):
        with self.assertRaises(ValueError):
                self.S.insert(*self.insert)

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)


class InsertWrongCurrency(unittest.TestCase):

    def setUp(self):
        self.insert = ['Nome', 'isin', 'AAA', 'dsa', 'STV']
        self.S = Stock(MagicMock(), mockSchema([]))

    def test_caughtError(self):
        with self.assertRaises(ValueError):
                self.S.insert(*self.insert)

    def test_argsAreStillNone(self):
        self.assertIsNone(self.S._id)
        self.assertIsNone(self.S.name)
        self.assertIsNone(self.S.isin)
        self.assertIsNone(self.S.currency)
        self.assertIsNone(self.S.boerse_name)
        self.assertIsNone(self.S.avan_ticker)
