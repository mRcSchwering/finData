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


# patching DB connection
def patchInfoSchema(args_list):
    with patch('finData.schema.Schema._getInfoSchema') as info:
        info.return_value = INFO_SCHEMA
        return Schema(*args_list)


# helper for silencing
class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


class SchemaInit(unittest.TestCase):

    def setUp(self):
        self.S = patchInfoSchema(['schema_name', 'stock', DB])

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

# class SchemaInit(unittest.TestCase):
#
#     def setUp(self):
#         self.db = MagicMock()
#         self.db.query = MagicMock(return_value=[('stock',), ('divid_yearly',)])
#
#     def test_normalInit(self):
#         S = Schema('schema_name', 'stock', self.db)
#         self.assertEqual(S.name, 'schema_name')
#         self.assertEqual(S.stock_table, 'stock')
#         self.assertEqual(S.tables, ['stock', 'divid_yearly'])
#
#     def test_wrongStockTable(self):
#         with self.assertRaises(AttributeError):
#             Schema('schema_name', 'stck', self.db)
#
#     def test_correctCalls(self):
#         S = Schema('schema_name', 'stock', self.db)
#         calls = S._db.method_calls
#         self.assertEqual(len(calls), 1)
#         exp = ("""SELECT tablename FROM pg_catalog.pg_tables """
#                """WHERE schemaname = %(schema_name)s""")
#         self.assertEqual(calls[0][1][0], exp)
#         self.assertEqual(calls[0][1][1], {'schema_name': 'schema_name'})
#
#
# class CreatingTable(unittest.TestCase):
#
#     def setUp(self):
#         db = MagicMock()
#         db.query = MagicMock(return_value=[('stock',), ('divid_yearly',)])
#         self.S = Schema('schema_name', 'stock', db)
#
#     def test_normalTable(self):
#         T = self.S.table('divid_yearly')
#         self.assertEqual(T.name, 'divid_yearly')
#         self.assertEqual(type(T).__name__, 'Table')
#         self.assertFalse(T._isStock)
#
#     def test_wrongTable(self):
#         with self.assertRaises(ValueError):
#             self.S.table('divid')
#
#     def test_stockTable(self):
#         T = self.S.table('stock')
#         self.assertTrue(T._isStock)
#
#
# class TableAttr(unittest.TestCase):
#
#     def setUp(self):
#         db = MagicMock()
#         db.query = MagicMock(return_value=[('stock',), ('divid_yearly',)])
#         S = Schema('schema_name', 'stock', db)
#         db.query = MagicMock(return_value=[('year',), ('divid',)])
#         self.T = S.table('divid_yearly')
#
#     def test_correctColumns(self):
#         self.assertEqual(self.T.columns, ['year', 'divid'])
#
#     def test_updateRate(self):
#         self.assertEqual(self.T.update_rate, 'yearly')
#
#     def test_insertStatement(self):
#         exp = ("""INSERT INTO schema_name.divid_yearly (year,divid) """
#                """VALUES (%(year)s,%(divid)s)""")
#         self.assertEqual(self.T.insert_statement, exp)


# class SchemaBehaviour(unittest.TestCase):
#
#     def setUp(self):
#         self.S = GoodSchema()
#
#     def test_nameAttr(self):
#         self.assertEqual(self.S.name, 'findata_init')
#
#     def test_listTables(self):
#         self.assertSetEqual(set(self.S.listTables()), set(['stock', 'marktk', 'hist']))
#
#     def test_getWrongTable(self):
#         with self.assertRaises(ValueError):
#             self.S.table('asd')
#
#     def test_getTable(self):
#         tab = self.S.table('hist')
#         self.assertEqual(type(tab).__name__, 'Table')
#
#     def test_tablesAndConversionsNotMatching(self):
#         with self.assertRaises(AttributeError):
#             self.S = WrongSchema()
#
#     def test_missingStockTable(self):
#         with self.assertRaises(AttributeError):
#             self.S = MissingStockSchema()
#
#
# class TableBehaviour(unittest.TestCase):
#
#     def setUp(self):
#         self.T = GoodSchema().table('hist')
#
#     def test_nameAttr(self):
#         self.assertEqual(self.T.name, 'hist')
#
#     def test_columnsAttr(self):
#         self.assertEqual(self.T.columns, ['stock_id', 'datum', 'open'])
#
#     def test_updateRate(self):
#         self.assertEqual(self.T.update_rate, 'daily')
#
#     def test_insertStatement(self):
#         exp = ("""INSERT INTO %(schema_name)s.%(table_name)s """
#                """(stock_id,datum,open) VALUES """
#                """(%(stock_id)s,%(datum)s,%(open)s)""")
#         self.assertEqual(self.T.insert_statement, exp)
#
#     def test_getWrongColumn(self):
#         with self.assertRaises(ValueError):
#             self.T.column('asd')
#
#     def test_getColumn(self):
#         col = self.T.column('stock_id')
#         self.assertEqual(type(col).__name__, 'Column')
#
#
# class StockTableBehaviour(unittest.TestCase):
#
#     def setUp(self):
#         self.T = GoodSchema().table('stock')
#
#     def test_nameAttr(self):
#         self.assertEqual(self.T.name, 'stock')
#
#     def test_columnsAttr(self):
#         self.assertEqual(self.T.columns, ['id', 'isin'])
#
#     def test_updateRate(self):
#         self.assertIsNone(self.T.update_rate)
#
#     def test_insertStatement(self):
#         exp = ("""INSERT INTO %(schema_name)s.%(table_name)s """
#                """(isin) VALUES (%(isin)s)""")
#         self.assertEqual(self.T.insert_statement, exp)
#
#     def test_getWrongColumn(self):
#         with self.assertRaises(ValueError):
#             self.T.column('asd')
#
#     def test_getColumn(self):
#         col = self.T.column('id')
#         self.assertEqual(type(col).__name__, 'Column')
#
#
# class ColumnBehaviour(unittest.TestCase):
#
#     def setUp(self):
#         self.C = GoodSchema().table('hist').column('datum')
#
#     def test_nameAttr(self):
#         self.assertEqual(self.C.name, 'datum')
#
#     def test_typeAttr(self):
#         self.assertEqual(self.C.type, 'date')
#
#
# class StockColumnBehaviour(unittest.TestCase):
#
#     def setUp(self):
#         self.C = GoodSchema().table('stock').column('isin')
#         self.C2 = GoodSchema().table('stock').column('id')
#
#     def test_nameAttr(self):
#         self.assertEqual(self.C.name, 'isin')
#         self.assertEqual(self.C2.name, 'id')
#
#     def test_typeAttr(self):
#         self.assertEqual(self.C.type, 'str')
#         self.assertEqual(self.C2.type, 'int')
