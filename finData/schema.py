# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import pandas as pd
import numpy as np


class Schema(object):
    """
    Reads DB schema and provides schema attributes

    name        schema name
    stock_table name of primary table with stock information
    table       table names in schema

    table       create table object
    getISINs    get all stock ISINs
    """

    def __init__(self, name, stock_table, db):
        self.name = name
        self.stock_table = stock_table
        self._db = db
        self.tables = self._getTables()
        self._info_schema = self._getInfoSchema()
        if self.stock_table not in self.tables:
            raise AttributeError(
                'Stock table %s not defined in tables' % self.stock_table)
        info_tabs = self._info_schema.get('table_name').tolist()
        if set(self.tables) != set(info_tabs):
            raise AttributeError(
                ('Weird error occured. DB might be fucked up.\n'
                 'DB has these tables: {tabs}\n'
                 'But information schema has these: {infos}')
                .format(tabs=self.tables, infos=info_tabs))

    def table(self, name):
        """
        Create table object with further table attributes
        """
        if name not in self.tables:
            raise ValueError('table %s not defined in schema %s' % (name, self.name))
        df = self._info_schema
        df = df.loc[df['table_name'] == name]
        df = df.sort_values(by=['ordinal_position'])
        return Table(name, self.stock_table, df, self.name, self._db)

    def getISINs(self):
        query = """SELECT isin FROM {schema}.{stock}""" \
                .format(schema=self.name, stock=self.stock_table)
        res = self._db.query(query, {}, 'all')
        if res is not None and len(res) > 0:
            return [d[0] for d in res]
        return None

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
        res = self._db.query(query, args, fetch='all')
        return pd.DataFrame(res, columns=info_cols)


class Table(object):
    """
    Provide table attributes

    name                table name
    update_rate         rate by which data in this table is updated
    columns             column names in table
    time_column         column name which has time points

    column              create column object
    insertRow           insert new row into table
    lastUpdate          get time point of latest entry
    """

    id_column = 'id'
    time_columns = ['datum', 'jahr']

    def __init__(self, name, stock, info_table, schema, db):
        self.name = name
        self._schema = schema
        self._stock_table = stock
        self._info_table = info_table
        self._db = db
        self.update_rate = self._getUpdateRate()
        self.columns = self._getColumns()
        self.time_column = self._getTimeColumn()

    def column(self, name):
        """
        Create Column object  with further column attributes
        """
        if name not in self.columns:
            raise ValueError(
                'column %s not defined in table %s' % (name, self.name))
        df = self._info_table
        return Column(name, df.loc[df['column_name'] == name])

    def insertRow(self, row):
        """
        Insert row by providing dict with column names
        """
        query = self._getInsertStatement()
        keys = list(row.keys())
        cols = [col for col in self.columns if col != self.id_column]
        if set(keys) != set(cols):
            raise ValueError('Column definitions not matching. Provided: {p}; Needed: {n}'
                             .format(p=keys, n=cols))
        vals = [row[k] for k in row]
        if set(vals) == set([None]):
            return False
        for k in row:
            if not isinstance(row[k], str) and np.isnan(row[k]):
                row[k] = AsIs('NULL')
        self._db.query(query, row)
        return True

    def lastUpdate(self, stock_id):
        """
        Show time point of latest table entry for a stock by stock id
        """
        if self.name == self._stock_table:
            raise ValueError('This table has no updates')
        query = self._getLatestUpdateStatement()
        args = {'id': stock_id}
        print(query)
        print(args)
        res = self._db.query(query, args, 'one')
        print(res)
        if res is None:
            return None
        return res[0]

    def _getColumns(self):
        return self._info_table.get('column_name').tolist()

    def _getUpdateRate(self):
        if self.name == self._stock_table:
            return None
        splitted = self.name.split('_')
        if len(splitted) < 2:
            return None
        return splitted[-1]

    def _getInsertStatement(self):
        columns = [col for col in self.columns if col != self.id_column]
        cols = ','.join(columns)
        vals = ','.join(['%({v})s'.format(v=v) for v in columns])
        loc = '{schem}.{tab}'.format(schem=self._schema, tab=self.name)
        return """INSERT INTO {loc} ({cols}) VALUES ({vals})""" \
               .format(cols=cols, vals=vals, loc=loc)

    def _getTimeColumn(self):
        if self.name == self._stock_table:
            return None
        cols = [col for col in self.columns if col in self.time_columns]
        return cols[0]

    def _getLatestUpdateStatement(self):
        stock_id = self._stock_table + '_' + self.id_column
        loc = '{schem}.{tab}'.format(schem=self._schema, tab=self.name)
        return """SELECT MAX({tp}) FROM {loc} WHERE {id} = %(id)s""" \
               .format(tp=self.time_column, loc=loc, id=stock_id)


class Column(object):
    """
    Provide column attributes

    name    column name
    type    column data type
    """

    def __init__(self, col_name, info_col):
        self.name = col_name
        self.type = self._getType(info_col)

    def _getType(self, df):
        data_type = df.get('data_type').tolist()[0]
        if data_type in ['integer']:
            return 'integer'
        if data_type in ['double precision', 'numeric']:
            return 'numeric'
        if data_type in ['character varying']:
            return 'string'
        if data_type in ['date']:
            return 'date'
        raise AttributeError('data type {d} of column {c} unknown'
                             .format(d=data_type, c=self.name))
