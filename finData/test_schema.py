from finData.schema import Schema
from unittest.mock import MagicMock
from unittest.mock import patch
import pandas as pd
import unittest
import sys
import io


# load test info schema
with open('finData/testdata/info_schema.csv') as inf:
    INFO_SCHEMA = pd.read_csv(inf)

# mock tables query answer
TABLES = ['fundamental_yearly', 'divid_yearly', 'stock', 'hist_daily']
DB = MagicMock()
DB.query = MagicMock(return_value=[(tab,) for tab in TABLES])


def patchInfoSchema(args_list):
    with patch('finData.schema.Schema._getInfoSchema') as info:
        info.return_value = INFO_SCHEMA
        return Schema(*args_list)


def patchGetTables(args_list):
    with patch('finData.schema.Schema._getTables') as tables:
        tables.return_value = TABLES
        return Schema(*args_list)


# helper for silencing
class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


class InfoSchemaPatched(unittest.TestCase):

    def setUp(self):
        db = MagicMock()
        db.query = MagicMock(return_value=[(tab,) for tab in TABLES])
        self.S = patchInfoSchema(['schema_name', 'stock', db])

    def test_schemaArgs(self):
        self.assertEqual(self.S.name, 'schema_name')
        self.assertEqual(self.S.stock_table, 'stock')
        self.assertEqual(self.S.tables, TABLES)

    def test_expectedInfoSchema(self):
        self.assertEqual(self.S._info_schema.shape, (17, 4))
        ords = self.S._info_schema['ordinal_position'].tolist()
        exp = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4]
        self.assertEqual(ords, exp)

    def test_correctCalls(self):
        # _getInfoSchema was patched so only the tables call
        calls = self.S._db.method_calls
        self.assertEqual(len(calls), 1)
        exp = ("""SELECT tablename FROM pg_catalog.pg_tables """
               """WHERE schemaname = %(schema_name)s""")
        self.assertEqual(calls[0][1][0], exp)
        self.assertEqual(calls[0][1][1], {'schema_name': 'schema_name'})


class GetTablesPatched(unittest.TestCase):

    def setUp(self):
        db = MagicMock()
        db.query = MagicMock(return_value=INFO_SCHEMA.to_dict())
        self.S = patchGetTables(['schema_name', 'stock', db])

    def test_schemaArgs(self):
        self.assertEqual(self.S.name, 'schema_name')
        self.assertEqual(self.S.stock_table, 'stock')
        self.assertEqual(self.S.tables, TABLES)

    def test_expectedInfoSchema(self):
        self.assertEqual(self.S._info_schema.shape, (17, 4))
        ords = self.S._info_schema['ordinal_position'].tolist()
        exp = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4]
        self.assertEqual(ords, exp)

    def test_correctCalls(self):
        # _getTables was patched so only getInfoSchema call
        calls = self.S._db.method_calls
        self.assertEqual(len(calls), 1)
        info_cols = ['table_name', 'column_name', 'ordinal_position', 'data_type']
        exp = ("""SELECT {cols} FROM information_schema.columns """
               """WHERE table_schema = %(schema)s""").format(cols=', '.join(info_cols))
        self.assertEqual(calls[0][1][0], exp)
        self.assertEqual(calls[0][1][1], {'schema': 'schema_name'})


class SchemaInitErrors(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.db.query = MagicMock(return_value=[(tab,) for tab in TABLES[:3]])

    def test_wrongStockTable(self):
        with self.assertRaises(AttributeError):
            self.S = patchInfoSchema(['schema_name', 'asd', self.db])

    def test_fuckedUpSchema(self):
        with self.assertRaises(AttributeError):
            self.S = patchInfoSchema(['schema_name', 'stock', self.db])


class InitTable(unittest.TestCase):

    def setUp(self):
        self.S = patchInfoSchema(['schema_name', 'stock', DB])

    def test_wrongTable(self):
        with self.assertRaises(ValueError):
            self.S.table('asd')

    def test_stockTable(self):
        self.T = self.S.table('stock')
        self.assertEqual(self.T.name, 'stock')
        self.assertTrue(self.T._isStock)

    def test_normalTable(self):
        self.T = self.S.table('divid_yearly')
        self.assertEqual(self.T.name, 'divid_yearly')
        self.assertFalse(self.T._isStock)


class StockTable(unittest.TestCase):

    cols = ['id', 'name', 'isin']

    def setUp(self):
        self.T = patchInfoSchema(['schema_name', 'stock', DB]).table('stock')

    def test_updateRate(self):
        self.assertIsNone(self.T.update_rate)

    def test_infoTable(self):
        act = self.T._info_table['ordinal_position'].tolist()
        self.assertEqual(act, [1, 2, 3])

    def test_infoTable(self):
        self.assertEqual(self.T.columns, self.cols)

    def test_infoTable(self):
        exp = 'INSERT INTO schema_name.stock ({a}) VALUES (%({b})s)' \
              .format(a=','.join(self.cols[1:]), b=')s,%('.join(self.cols[1:]))
        self.assertEqual(self.T.insert_statement, exp)

    def test_timepointColumn(self):
        self.assertIsNone(self.T.time_column)

    def test_allColumnTypes(self):
        exp = ['integer', 'string', 'string']
        act = [self.T.column(col).type for col in self.T.columns]
        self.assertEqual(exp, act)


class DividTable(unittest.TestCase):

    cols = ['id', 'stock_id', 'datum', 'dividende']

    def setUp(self):
        self.T = patchInfoSchema(['schema_name', 'stock', DB]).table('divid_yearly')

    def test_updateRate(self):
        self.assertEqual(self.T.update_rate, 'yearly')

    def test_infoTable(self):
        act = self.T._info_table['ordinal_position'].tolist()
        self.assertEqual(act, [1, 2, 3, 4])

    def test_infoTable(self):
        self.assertEqual(self.T.columns, self.cols)

    def test_infoTable(self):
        exp = 'INSERT INTO schema_name.divid_yearly ({a}) VALUES (%({b})s)' \
              .format(a=','.join(self.cols[1:]), b=')s,%('.join(self.cols[1:]))
        self.assertEqual(self.T.insert_statement, exp)

    def test_timepointColumn(self):
        self.assertEqual(self.T.time_column, 'datum')

    def test_allColumnTypes(self):
        exp = ['integer', 'integer', 'date', 'numeric']
        act = [self.T.column(col).type for col in self.T.columns]
        self.assertEqual(exp, act)


class HistTable(unittest.TestCase):

    cols = ['id', 'stock_id', 'datum', 'open']

    def setUp(self):
        self.T = patchInfoSchema(['schema_name', 'stock', DB]).table('hist_daily')

    def test_updateRate(self):
        self.assertEqual(self.T.update_rate, 'daily')

    def test_infoTable(self):
        act = self.T._info_table['ordinal_position'].tolist()
        self.assertEqual(act, [1, 2, 3, 4])

    def test_infoTable(self):
        self.assertEqual(self.T.columns, self.cols)

    def test_infoTable(self):
        exp = 'INSERT INTO schema_name.hist_daily ({a}) VALUES (%({b})s)' \
              .format(a=','.join(self.cols[1:]), b=')s,%('.join(self.cols[1:]))
        self.assertEqual(self.T.insert_statement, exp)

    def test_timepointColumn(self):
        self.assertEqual(self.T.time_column, 'datum')

    def test_allColumnTypes(self):
        exp = ['integer', 'integer', 'date', 'numeric']
        act = [self.T.column(col).type for col in self.T.columns]
        self.assertEqual(exp, act)


class FundTable(unittest.TestCase):

    cols = ['id', 'stock_id', 'jahr', 'umsatz', 'sum_aktiva', 'dividende']

    def setUp(self):
        self.T = patchInfoSchema(['schema_name', 'stock', DB]).table('fundamental_yearly')

    def test_updateRate(self):
        self.assertEqual(self.T.update_rate, 'yearly')

    def test_infoTable(self):
        act = self.T._info_table['ordinal_position'].tolist()
        self.assertEqual(act, [1, 2, 3, 4, 5, 6])

    def test_infoTable(self):
        self.assertEqual(self.T.columns, self.cols)

    def test_infoTable(self):
        exp = 'INSERT INTO schema_name.fundamental_yearly ({a}) VALUES (%({b})s)' \
              .format(a=','.join(self.cols[1:]), b=')s,%('.join(self.cols[1:]))
        self.assertEqual(self.T.insert_statement, exp)

    def test_timepointColumn(self):
        self.assertEqual(self.T.time_column, 'jahr')

    def test_allColumnTypes(self):
        exp = ['integer', 'integer', 'integer', 'integer', 'numeric', 'numeric']
        act = [self.T.column(col).type for col in self.T.columns]
        self.assertEqual(exp, act)


class ColumnInit(unittest.TestCase):

    def setUp(self):
        self.T = patchInfoSchema(['schema_name', 'stock', DB]).table('stock')

    def test_wrongColumn(self):
        with self.assertRaises(ValueError):
            self.T.column('asd')

    def test_unknownDataType(self):
        self.T._info_table.iat[1, 3] = 'asd'
        with self.assertRaises(AttributeError):
            self.T.column('name')
