# This Python file uses the following encoding: utf-8
import pandas as pd

# TODO date types sollten eigentlich aus sql geladen werden
# TODO yearly und daily könnten in table namen encoded werden
# TODO constriants (zB currency) sollten in sql definiert sein

# from finData.dbconnector import DBConnector
# db = DBConnector('findata_test', 'postgres', '127.0.0.1', 5432)
# schema = Schema('findata_init2', 'stock', db)


class Schema(object):

        # TODO wie krieg ich column names
        # TODO wie krieg ich data types?
        # TODO aus namen, update rate extrahieren

    def __init__(self, name, stock_table, db):
        self.name = name
        self.stock_table = stock_table
        self._db = db
        self.tables = self._getTables()
        if self.stock_table not in self.tables:
            raise AttributeError('Stock table %s not defined in tables' % self.stock_table)
        self._info_schema = self._getInfoSchema()
        #convs = [tab for tab in self.conversions]
        # if set(tabs) != set(convs):
        #     raise AttributeError('Definitions for tables and conversions do not match')

    def table(self, name):
        if name not in self.tables:
            raise ValueError('table %s not defined in schema %s' % (name, self.name))
        # if name == self.stock_table:
        #     update_rate = None
        #     cols = [key for key in self.tables.get(name)]
        #     col_types = {key: 'str' for key in self.tables.get(name)}
        #     col_types['id'] = 'int'
        #     is_stock_table = True
        # else:
        #     update_rate = 'daily' if name in self.daily_updates else 'yearly'
        #     cols = [key for key in self.tables.get(name)]
        #     col_types = {key: self.getType(key) for key in self.tables.get(name)}
        #     is_stock_table = False
        return Table(name, self._db, name == self.stock_table, self.name)

    def listTables(self):
        return [tab for tab in self.tables]

    def _getTables(self):
        query = ("""SELECT tablename FROM pg_catalog.pg_tables """
                 """WHERE schemaname = %(schema_name)s""")
        args = {'schema_name': self.name}
        res = self._db.query(query, args, fetch='all')
        return [tab[0] for tab in res]

    def _getInfoSchema(self):
        info_cols = ['table_name', 'column_name', 'ordinal_position', 'data_type']
        query = ("""SELECT {cols} FROM information_schema.columns """
                 """WHERE table_schema = %(schema)s""").format(cols=', '.join(info_cols))
        args = {'schema': self.name}
        df = self._db.query(query, args, fetch='all')
        return pd.DataFrame(res, columns=info_cols)

    @classmethod
    def getType(cls, col_name):
        if col_name in cls.date_columns:
            return 'date'
        if col_name in cls.int_columns:
            return 'int'
        return 'numeric'


class Table(object):

    id_column = 'id'

    def __init__(self, name, db, stock, schema):
        self.name = name
        self._isStock = stock
        self._db = db
        self._schema = schema
        self.columns = self._getColumns()
        self.update_rate = self._getUpdateRate()
        # self.update_rate = update_rate
        # self.columns = columns
        # self._column_types = column_types
        self.insert_statement = self._getInsertStatement()

    def column(self, name):
        if name not in [col for col in self._column_types]:
            raise ValueError('column %s not defined in table %s' %
                             (name, self.name))
        return Column(name, self._column_types.get(name))

    def _getColumns(self):
        query = ("""SELECT column_name FROM information_schema.columns """
                 """WHERE table_schema = %(schema)s """
                 """AND table_name = %(table)s""")
        args = {'schema': self._schema, 'table': self.name}
        res = self._db.query(query, args, fetch='all')
        return [col[0] for col in res]

    def _getUpdateRate(self):
        return self.name.split('_')[-1]

    def _getInsertStatement(self):
        columns = [col for col in self.columns if col != self.id_column]
        cols = ','.join(columns)
        vals = ','.join(['%({v})s'.format(v=v) for v in columns])
        loc = '{schem}.{tab}'.format(schem=self._schema, tab=self.name)
        return """INSERT INTO {loc} ({cols}) VALUES ({vals})""" \
               .format(cols=cols, vals=vals, loc=loc)


class Column(object):

    def __init__(self, col_name, col_type):
        self.name = col_name
        self.type = col_type
