# This Python file uses the following encoding: utf-8

# TODO date types sollten eigentlich aus sql geladen werden
# TODO yearly und daily könnten in table namen encoded werden
# TODO constriants (zB currency) sollten in sql definiert sein


class ASchema(object):

    # name of the schema
    name = ''

    # special treatment, None update rate, str expect for id, no conversion
    # also the id column will be excluded from insert statement
    stock_table = ''

    # tables which are updated daily, the rest is considered yearly
    daily_updates = ['']

    # non-numeric column types as they will be in DB schema
    date_columns = ['']
    int_columns = ['']

    # column definitions as in DB schema
    tables = {'table_name': ['col_name']}

    # from scraper table id to name as in DB schema for each table
    conversions = {'table_name': [{'id': 'scraper_id', 'name': 'col_name'}]}

    def __init__(self):
        tabs = [tab for tab in self.tables]
        convs = [tab for tab in self.conversions]
        if set(tabs) != set(convs):
            raise AttributeError('Definitions for tables and conversions do not match')
        if self.stock_table not in tabs:
            raise AttributeError('Stock table %s not defined in tables' % self.stock_table)

    def table(self, name):
        if name not in [tab for tab in self.tables]:
            raise ValueError('table %s not defined in schema %s' %
                             (name, self.name))
        if name == self.stock_table:
            update_rate = None
            cols = [key for key in self.tables.get(name)]
            col_types = {key: 'str' for key in self.tables.get(name)}
            col_types['id'] = 'int'
            is_stock_table = True
        else:
            update_rate = 'daily' if name in self.daily_updates else 'yearly'
            cols = [key for key in self.tables.get(name)]
            col_types = {key: self.getType(key) for key in self.tables.get(name)}
            is_stock_table = False
        return Table(name, update_rate, cols, col_types, is_stock_table)

    def listTables(self):
        return [tab for tab in self.tables]

    @classmethod
    def getType(cls, col_name):
        if col_name in cls.date_columns:
            return 'date'
        if col_name in cls.int_columns:
            return 'int'
        return 'numeric'


class Table(object):

    def __init__(self, table_name, update_rate, columns, column_types, stock=False):
        self.name = table_name
        self.update_rate = update_rate
        self.columns = columns
        self._column_types = column_types
        self.insert_statement = self._prepareInsertStatement(stock)

    def column(self, name):
        if name not in [col for col in self._column_types]:
            raise ValueError('column %s not defined in table %s' %
                             (name, self.name))
        return Column(name, self._column_types.get(name))

    def listColumns(self):
        return [col for col in self._column_types]

    def _prepareInsertStatement(self, is_stock_table):

        if is_stock_table:
            columns = [col for col in self.columns if col != 'id']
        else:
            columns = self.columns
        cols = ','.join(columns)
        vals = ','.join(['%({v})s'.format(v=v) for v in columns])
        loc = '%(schema_name)s.%(table_name)s'
        return """INSERT INTO {loc} ({cols}) VALUES ({vals})""" \
               .format(cols=cols, vals=vals, loc=loc)


class Column(object):

    def __init__(self, col_name, col_type):
        self.name = col_name
        self.type = col_type
