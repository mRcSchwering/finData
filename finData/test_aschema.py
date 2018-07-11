from finData.aschema import ASchema
import unittest
#import sys
#import io


class Schema(ASchema):

    # name of the schema
    name = "findata_init"

    # special treatment, None update rate, str expect for id, no conversion
    # also the id column will be excluded from insert statement
    stock_table = 'stock'

    # tables which are updated daily, the rest is considered yearly
    daily_updates = ['hist']

    # non-numeric column types as they will be in DB schema
    date_columns = ['datum']
    int_columns = ['year']

    # column definitions as in DB schema
    tables = {
        'stock': ['id', 'isin'],
        'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita'],
        'hist': ['stock_id', 'datum', 'open']
    }

    # from scraper table id to name as in DB schema for each table
    conversions = {
        'stock': [],
        'marktk': [
            {'id': 'Anzahl der Aktien', 'name': 'zahl_aktien'},
            {'id': 'Marktkapitalisierung', 'name': 'marktkapita'}
        ],
        'hist': [
            {'id': 'datum', 'name': 'datum'},
            {'id': '1. open', 'name': 'open'}
        ]
    }

    def __init__(self):
        super().__init__()


class WrongSchema(Schema):

    tables = {'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita']}


class MissingStockSchema(Schema):

    tables = {
        'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita'],
        'hist': ['stock_id', 'datum', 'open']
    }

    conversions = {
        'marktk': [
            {'id': 'Anzahl der Aktien', 'name': 'zahl_aktien'},
            {'id': 'Marktkapitalisierung', 'name': 'marktkapita'}
        ],
        'hist': [
            {'id': 'datum', 'name': 'datum'},
            {'id': '1. open', 'name': 'open'}
        ]
    }


class ASchemaBehaviour(unittest.TestCase):

    def setUp(self):
        self.S = Schema()

    def test_nameAttr(self):
        self.assertEqual(self.S.name, 'findata_init')

    def test_listTables(self):
        self.assertSetEqual(set(self.S.listTables()), set(['stock', 'marktk', 'hist']))

    def test_getWrongTable(self):
        with self.assertRaises(ValueError):
            self.S.table('asd')

    def test_getTable(self):
        tab = self.S.table('hist')
        self.assertEqual(type(tab).__name__, 'Table')

    def test_tablesAndConversionsNotMatching(self):
        with self.assertRaises(AttributeError):
            self.S = WrongSchema()

    def test_missingStockTable(self):
        with self.assertRaises(AttributeError):
            self.S = MissingStockSchema()


class TableBehaviour(unittest.TestCase):

    def setUp(self):
        self.T = Schema().table('hist')

    def test_nameAttr(self):
        self.assertEqual(self.T.name, 'hist')

    def test_columnsAttr(self):
        self.assertEqual(self.T.columns, ['stock_id', 'datum', 'open'])

    def test_updateRate(self):
        self.assertEqual(self.T.update_rate, 'daily')

    def test_insertStatement(self):
        exp = ("""INSERT INTO %(schema_name)s.%(table_name)s """
               """(stock_id,datum,open) VALUES """
               """(%(stock_id)s,%(datum)s,%(open)s)""")
        self.assertEqual(self.T.insert_statement, exp)

    def test_getWrongColumn(self):
        with self.assertRaises(ValueError):
            self.T.column('asd')

    def test_getColumn(self):
        col = self.T.column('stock_id')
        self.assertEqual(type(col).__name__, 'Column')


class StockTableBehaviour(unittest.TestCase):

    def setUp(self):
        self.T = Schema().table('stock')

    def test_nameAttr(self):
        self.assertEqual(self.T.name, 'stock')

    def test_columnsAttr(self):
        self.assertEqual(self.T.columns, ['id', 'isin'])

    def test_updateRate(self):
        self.assertIsNone(self.T.update_rate)

    def test_insertStatement(self):
        exp = ("""INSERT INTO %(schema_name)s.%(table_name)s """
               """(isin) VALUES (%(isin)s)""")
        self.assertEqual(self.T.insert_statement, exp)

    def test_getWrongColumn(self):
        with self.assertRaises(ValueError):
            self.T.column('asd')

    def test_getColumn(self):
        col = self.T.column('id')
        self.assertEqual(type(col).__name__, 'Column')


class ColumnBehaviour(unittest.TestCase):

    def setUp(self):
        self.C = Schema().table('hist').column('datum')

    def test_nameAttr(self):
        self.assertEqual(self.C.name, 'datum')

    def test_typeAttr(self):
        self.assertEqual(self.C.type, 'date')


class StockColumnBehaviour(unittest.TestCase):

    def setUp(self):
        self.C = Schema().table('stock').column('isin')
        self.C2 = Schema().table('stock').column('id')

    def test_nameAttr(self):
        self.assertEqual(self.C.name, 'isin')
        self.assertEqual(self.C2.name, 'id')

    def test_typeAttr(self):
        self.assertEqual(self.C.type, 'str')
        self.assertEqual(self.C2.type, 'int')
